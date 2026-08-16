"""libc shim: emulates imported libc functions for ELF binaries.

Real crackme binaries call functions like printf/scanf/fopen through their
PLT.  The shim locates each PLT stub (scanning .plt / .plt.sec / .plt.got for
RIP-relative `jmp [rip+X]` that targets a known GOT slot), installs a code
hook on every stub, and emulates the called routine in Python so the emulator
never needs a full libc.  Reads from "stdin" consume the executor's input
buffer; files opened via fopen read from / write into per-path byte buffers.
"""

from __future__ import annotations

import struct
from typing import Dict, Optional

from capstone import CS_ARCH_X86, CS_MODE_64, Cs
from capstone.x86_const import X86_OP_MEM, X86_REG_RIP
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_RIP, UC_X86_REG_RSP

from academy.emulator.elf import ElfBinary

# addresses reserved inside the mapped address space for shim housekeeping.
SHIM_ARENA = 0x600000      # FILE handles, argv strings, canary page
SHIM_ARENA_SIZE = 0x20000
FS_BASE = 0x610000         # set as FS.base so fs:0x28 canary reads land here
FILE_HANDLES = 0x601000    # FILE* pointers allocated here
TRAMPOLINE = 0x710000      # return address installed by __libc_start_main

SIG_DFL = 0
SIG_IGN = 1

_MAX_READAHEAD = 0x4000


def find_plt_stubs(binary: ElfBinary, imports: Dict[int, str]) -> Dict[int, str]:
    """Map shim interception sites to imported names.

    Two kinds of site are hooked:
      * PLT stubs — RIP-relative `jmp [rip+disp]` in .plt / .plt.sec /
        .plt.got (possibly `bnd`-prefixed) whose target is a GOT slot.
      * Direct GOT calls — `call qword ptr [rip+disp]` inside .text whose
        target is a GOT slot (newer glibc _start calls __libc_start_main
        straight through the GOT, bypassing the PLT).
    """
    stubs: Dict[int, str] = {}
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    for secname in (".plt", ".plt.sec", ".plt.got", ".text"):
        sec = binary.sections.get(secname)
        if sec is None:
            continue
        _ty, addr, offset, size = sec
        code = binary.data[offset : offset + size]
        for insn in md.disasm(code, addr):
            mnemonic = insn.mnemonic
            is_jump = "jmp" in mnemonic or mnemonic.startswith("bnd jmp")
            is_call = mnemonic == "call"
            if not (is_jump or is_call):
                continue
            if not insn.operands:
                continue
            op = insn.operands[0]
            if op.type != X86_OP_MEM or op.mem.base != X86_REG_RIP:
                continue
            target = insn.address + insn.size + op.mem.disp
            if target in imports:
                stubs[insn.address] = imports[target]
    return stubs


class LibcShim:
    def __init__(self, executor: object, binary: ElfBinary):
        self.ex = executor
        self.binary = binary
        self.stubs = find_plt_stubs(binary, binary.imports)
        self.handlers: Dict[int, int] = {}  # signum -> handler address
        self._files: Dict[int, "_OpenFile"] = {}
        self._stdin_addr: Optional[int] = None
        self._next_handle = FILE_HANDLES
        self.written_files: Dict[str, bytes] = {}
        self._hooks = []

    def install(self) -> None:
        uc = self.ex._uc
        for addr, name in self.stubs.items():
            hook = uc.hook_add(UC_HOOK_CODE, self._on_stub, begin=addr, end=addr)
            self._hooks.append((addr, hook))
        tramp = uc.hook_add(
            UC_HOOK_CODE, self._on_trampoline, begin=TRAMPOLINE, end=TRAMPOLINE
        )
        self._hooks.append((TRAMPOLINE, tramp))
        self._stdin_addr = next(
            (addr for addr, name in self.binary.imports.items() if name == "stdin"), None
        )

    def clear(self) -> None:
        for _addr, hook in self._hooks:
            try:
                self.ex._uc.hook_del(hook)
            except Exception:
                pass
        self._hooks = []
        self.handlers = {}
        self._files = {}
        self.written_files = {}
        self._next_handle = FILE_HANDLES

    def _read_cstr(self, addr: int, limit: int = 256) -> bytes:
        out = bytearray()
        chunk = b""
        while len(out) < limit:
            try:
                chunk = self.ex._uc.mem_read(addr + len(out), min(64, limit - len(out)))
            except Exception:
                break
            if not chunk:
                break
            nul = chunk.find(b"\0")
            if nul != -1:
                out.extend(chunk[:nul])
                break
            out.extend(chunk)
        return bytes(out)

    def _write_cstr(self, addr: int, value: bytes) -> None:
        self.ex._uc.mem_write(addr, value + b"\0")

    def _arg(self, index: int, rsp: int) -> int:
        """SysV vararg: registers rdi,rsi,rdx,rcx,r8,r9 then [rsp+8+k*8]."""
        regs = ("rdi", "rsi", "rdx", "rcx", "r8", "r9")
        if index < len(regs):
            return self.ex.get_register(regs[index])
        stack_off = 8 + (index - len(regs)) * 8
        try:
            return int.from_bytes(
                self.ex._uc.mem_read(rsp + stack_off, 8), "little"
            )
        except Exception:
            return 0

    def _input(self) -> bytearray:
        return bytearray(self.ex._input)

    def _return(self, rsp: int, value: int) -> None:
        self.ex.set_register("rax", value & 0xFFFFFFFFFFFFFFFF)
        self.ex._uc.reg_write(UC_X86_REG_RIP, self._ret_addr)
        self.ex._uc.reg_write(UC_X86_REG_RSP, rsp + 8)

    def _exit(self, code: int) -> None:
        from academy.emulator.executor import STATUS_EXITED

        self.ex.exit_code = code & 0xFF
        self.ex.status = STATUS_EXITED
        try:
            self.ex._uc.emu_stop()
        except Exception:
            pass

    def _on_stub(self, uc, address: int, size: int, user_data) -> None:
        name = self.stubs.get(address)
        if name is None:
            return
        rsp = self.ex.get_register("rsp")
        try:
            raw = uc.mem_read(rsp, 8)
        except Exception:
            return
        self._ret_addr = int.from_bytes(raw, "little")
        handler = getattr(self, f"_f_{name}", None)
        if handler is None:
            self._unhandled(name, rsp)
        else:
            handler(rsp)

    def _on_trampoline(self, uc, address: int, size: int, user_data) -> None:
        self._exit(self.ex.get_register("eax"))

    def _unhandled(self, name: str, rsp: int) -> None:
        self.ex._output = self.ex._output + f"[shim] unhandled {name}()\n".encode()
        self._return(rsp, 0)

    def _f_puts(self, rsp: int) -> None:
        s = self._read_cstr(self.ex.get_register("rdi"))
        self.ex._output = self.ex._output + s + b"\n"
        self._return(rsp, 1)

    def _f_putchar(self, rsp: int) -> None:
        self.ex._output = self.ex._output + bytes([self.ex.get_register("edi") & 0xFF])
        self._return(rsp, self.ex.get_register("edi") & 0xFF)

    def _f_printf(self, rsp: int) -> None:
        fmt = self._read_cstr(self.ex.get_register("rdi"))
        out = self._render(fmt, rsp)
        self.ex._output = self.ex._output + out
        self._return(rsp, len(out))

    def _f_scanf(self, rsp: int) -> None:
        self._scan(rsp)

    def _f___isoc99_scanf(self, rsp: int) -> None:
        self._scan(rsp)

    def _f_strcmp(self, rsp: int) -> None:
        a = self._read_cstr(self.ex.get_register("rdi"))
        b = self._read_cstr(self.ex.get_register("rsi"))
        diff = 0
        for i in range(max(len(a), len(b))):
            ca = a[i] if i < len(a) else 0
            cb = b[i] if i < len(b) else 0
            if ca != cb:
                diff = ca - cb
                break
        self._return(rsp, diff & 0xFFFFFFFFFFFFFFFF)

    def _f_strlen(self, rsp: int) -> None:
        s = self._read_cstr(self.ex.get_register("rdi"))
        self._return(rsp, len(s))

    def _f_strcspn(self, rsp: int) -> None:
        s = self._read_cstr(self.ex.get_register("rdi"))
        reject = self._read_cstr(self.ex.get_register("rsi"))
        span = 0
        for ch in s:
            if ch in reject:
                break
            span += 1
        self._return(rsp, span)

    def _f_exit(self, rsp: int) -> None:
        self._exit(self.ex.get_register("edi"))

    def _f___stack_chk_fail(self, rsp: int) -> None:
        self.ex._output = self.ex._output + b"*** stack smashing detected ***\n"
        self._exit(1)

    def _f_perror(self, rsp: int) -> None:
        s = self._read_cstr(self.ex.get_register("rdi"))
        self.ex._output = self.ex._output + s + b": No such file or directory\n"
        self._return(rsp, 0)

    def _f_signal(self, rsp: int) -> None:
        signum = self.ex.get_register("edi")
        handler = self.ex.get_register("rsi")
        old = self.handlers.get(signum, SIG_DFL)
        self.handlers[signum] = handler
        self._return(rsp, old)

    def _f_raise(self, rsp: int) -> None:
        signum = self.ex.get_register("edi")
        handler = self.handlers.get(signum)
        if handler and handler not in (SIG_DFL, SIG_IGN):
            # jump into the handler; leave the stack so its `ret` returns to
            # the caller of raise().
            self.ex._uc.reg_write(UC_X86_REG_RIP, handler)
            return
        self._return(rsp, 0)

    def _f_fopen(self, rsp: int) -> None:
        path = self._read_cstr(self.ex.get_register("rdi"))
        self._read_cstr(self.ex.get_register("rsi"))
        files = getattr(self.ex, "files", {})
        content = files.get(path)
        if content is None:
            content = files.get(path.decode("latin1"))
        if content is None:
            content = files.get(
                path.lstrip(b"./"), files.get(path.decode("latin1").lstrip("./"), b"")
            )
        if content is None:
            content = b""
        handle = self._next_handle
        self._next_handle += 0x40
        self._files[handle] = _OpenFile(path, bytearray(content))
        self.ex._uc.mem_write(handle, b"F" * 0x40)
        self._return(rsp, handle)

    def _f_fclose(self, rsp: int) -> None:
        handle = self.ex.get_register("rdi")
        f = self._files.get(handle)
        if f is not None:
            self.written_files[f.path] = bytes(f.buf)
            self._files.pop(handle, None)
            self._return(rsp, 0)
        else:
            self._return(rsp, -1)

    def _f_fread(self, rsp: int) -> None:
        buf = self.ex.get_register("rdi")
        size = self.ex.get_register("rsi")
        nmemb = self.ex.get_register("rdx")
        handle = self.ex.get_register("rcx")
        f = self._files.get(handle)
        count = 0
        if f is not None:
            want = size * nmemb
            chunk = bytes(f.buf[f.pos : f.pos + want])
            f.pos += len(chunk)
            if chunk:
                try:
                    self.ex._uc.mem_write(buf, chunk)
                except Exception:
                    chunk = b""
            count = len(chunk) // size if size else 0
        self._return(rsp, count)

    def _f_fwrite(self, rsp: int) -> None:
        ptr = self.ex.get_register("rdi")
        size = self.ex.get_register("rsi")
        nmemb = self.ex.get_register("rdx")
        handle = self.ex.get_register("rcx")
        f = self._files.get(handle)
        count = 0
        if f is not None:
            try:
                chunk = self.ex._uc.mem_read(ptr, size * nmemb)
            except Exception:
                chunk = b""
            f.buf.extend(chunk)
            f.pos += len(chunk)
            count = len(chunk) // size if size else 0
        self._return(rsp, count)

    def _f_fputc(self, rsp: int) -> None:
        char = self.ex.get_register("edi") & 0xFF
        handle = self.ex.get_register("rsi")
        f = self._files.get(handle)
        if f is not None:
            f.buf.append(char)
        self._return(rsp, char)

    def _f_fgets(self, rsp: int) -> None:
        buf = self.ex.get_register("rdi")
        n = self.ex.get_register("rsi")
        stream = self.ex.get_register("rdx")
        if stream == self._stdin_addr or stream == 0 or self._stdin_addr is None:
            data = self._input()
            line = bytearray()
            while data and len(line) < max(n - 1, 0):
                ch = data.pop(0)
                line.append(ch)
                if ch == 0x0A:
                    break
            self.ex._input = bytes(data)
            if line:
                try:
                    self.ex._uc.mem_write(buf, bytes(line) + b"\0")
                except Exception:
                    pass
                self._return(rsp, buf)
            else:
                self._return(rsp, 0)
        else:
            f = self._files.get(stream)
            if f is None:
                self._return(rsp, 0)
                return
            line = bytearray()
            while f.pos < len(f.buf) and len(line) < max(n - 1, 0):
                ch = f.buf[f.pos]
                f.pos += 1
                line.append(ch)
                if ch == 0x0A:
                    break
            if line:
                try:
                    self.ex._uc.mem_write(buf, bytes(line) + b"\0")
                except Exception:
                    pass
                self._return(rsp, buf)
            else:
                self._return(rsp, 0)

    def _f___libc_start_main(self, rsp: int) -> None:
        main = self.ex.get_register("rdi")
        argc = 1
        argv = 0x601F80
        self.ex._uc.mem_write(argv, struct.pack("<QQ", 0x601F90, 0))
        self.ex._uc.mem_write(0x601F90, b"./prog\0")
        self.ex.set_register("edi", argc)
        self.ex.set_register("rsi", argv)
        # push trampoline as main's return address
        self.ex._uc.reg_write(UC_X86_REG_RSP, rsp + 8 - 8)
        self.ex._uc.mem_write(rsp + 8 - 8, struct.pack("<Q", TRAMPOLINE))
        self.ex._uc.reg_write(UC_X86_REG_RIP, main)

    def _render(self, fmt: bytes, rsp: int) -> bytes:
        out = bytearray()
        i = 0
        arg_index = 1  # rdi holds the format; args start at rsi
        while i < len(fmt):
            ch = fmt[i]
            if ch != 0x25:
                out.append(ch)
                i += 1
                continue
            # parse flags/width/precision/length
            j = i + 1
            while j < len(fmt) and fmt[j] in b"-+ 0#":
                j += 1
            flags = fmt[i + 1 : j]
            digits = bytearray()
            while j < len(fmt) and fmt[j] in b"0123456789":
                digits.append(fmt[j])
                j += 1
            width = int(digits) if digits else 0
            length = b""
            if j < len(fmt) and fmt[j] in b"hljztL":
                length = bytes([fmt[j]])
                j += 1
                if length == b"l" and j < len(fmt) and fmt[j] == b"l":
                    length = b"ll"
                    j += 1
            if j >= len(fmt):
                break
            conv = chr(fmt[j])
            j += 1
            arg = self._arg(arg_index, rsp)
            arg_index += 1
            if conv == "s":
                if arg == 0:
                    text = b"(null)"
                else:
                    text = self._read_cstr(arg, _MAX_READAHEAD)
                out.extend(self._pad(text, width, flags))
            elif conv == "c":
                out.extend(self._pad(bytes([arg & 0xFF]), width, flags))
            elif conv in "di":
                val = self._signed(arg, length)
                text = str(val).encode()
                out.extend(self._pad(text, width, flags, numeric=True, value=val))
            elif conv in "uoxX":
                val = self._unsigned(arg, length)
                if conv == "u":
                    text = str(val).encode()
                else:
                    text = format(val, "x" if conv == "x" else "X").encode()
                    if conv == "o" and flags and b"#" in flags:
                        text = b"0" + text
                    elif conv in "xX" and flags and b"#" in flags and val:
                        text = (b"0x" if conv == "x" else b"0X") + text
                out.extend(self._pad(text, width, flags, numeric=True, value=val))
            elif conv == "p":
                text = ("0x%x" % arg).encode()
                out.extend(text)
            elif conv == "%":
                out.append(0x25)
                arg_index -= 1
            else:
                out.append(0x25)
                out.extend(bytes([ord(conv)]))
                arg_index -= 1
            i = j
        return bytes(out)

    def _signed(self, value: int, length: bytes) -> int:
        bits = {b"h": 16, b"hh": 8, b"l": 64, b"ll": 64, b"z": 64}.get(length, 32)
        mask = (1 << bits) - 1
        value &= mask
        if value & (1 << (bits - 1)):
            value -= 1 << bits
        return value

    def _unsigned(self, value: int, length: bytes) -> int:
        bits = {b"h": 16, b"hh": 8, b"l": 64, b"ll": 64, b"z": 64}.get(length, 32)
        return value & ((1 << bits) - 1)

    def _pad(
        self, text: bytes, width: int, flags: bytes, numeric: bool = False, value: int = 0
    ) -> bytes:
        if width <= len(text):
            return text
        pad = width - len(text)
        zero_flag = b"0" in flags and b"-" not in flags
        left = b"-" in flags
        if numeric and zero_flag and not left:
            if value < 0:
                return b"-" + b"0" * (pad - 1) + text[1:]
            return b"0" * pad + text
        if left:
            return text + b" " * pad
        return b" " * pad + text

    def _scan(self, rsp: int) -> None:
        fmt = self._read_cstr(self.ex.get_register("rdi"))
        data = self._input()
        items = 0
        arg_index = 1  # rdi holds the format; args start at rsi
        i = 0
        consumed = bytearray()
        while i < len(fmt) and data:
            ch = fmt[i]
            if ch in b" \t\n":
                while data and data[0] in b" \t\n":
                    consumed.append(data.pop(0))
                i += 1
                continue
            if ch != 0x25:
                if data and data[0] == ch:
                    consumed.append(data.pop(0))
                else:
                    break
                i += 1
                continue
            j = i + 1
            width = 0
            while j < len(fmt) and fmt[j] in b"0123456789":
                width = width * 10 + (fmt[j] - 0x30)
                j += 1
            length = b""
            if j < len(fmt) and fmt[j] in b"hljztL":
                length = bytes([fmt[j]])
                j += 1
                if length == b"l" and j < len(fmt) and fmt[j] == b"l":
                    length = b"ll"
                    j += 1
            if j >= len(fmt):
                break
            conv = chr(fmt[j])
            j += 1
            dest = self._arg(arg_index, rsp)
            arg_index += 1
            if conv == "s":
                while data and data[0] in b" \t\n":
                    consumed.append(data.pop(0))
                token = bytearray()
                while data and data[0] not in b" \t\n":
                    if width and len(token) >= width:
                        break
                    token.append(data.pop(0))
                    consumed.append(token[-1])
                if token:
                    self.ex._uc.mem_write(dest, bytes(token) + b"\0")
                    items += 1
            elif conv == "c":
                if data:
                    consumed.append(data.pop(0))
                    self.ex._uc.mem_write(dest, bytes([consumed[-1]]))
                    items += 1
            elif conv in "diuxXo":
                while data and data[0] in b" \t\n":
                    consumed.append(data.pop(0))
                token = bytearray()
                while data and data[0] not in b" \t\n":
                    if width and len(token) >= width:
                        break
                    token.append(data.pop(0))
                    consumed.append(token[-1])
                if token:
                    try:
                        if conv in "xX":
                            value = int(bytes(token), 16)
                        elif conv == "o":
                            value = int(bytes(token), 8)
                        elif conv == "u":
                            value = int(bytes(token), 10)
                        else:
                            value = int(bytes(token), 10)
                    except ValueError:
                        value = 0
                    bits = {b"h": 16, b"l": 64, b"ll": 64, b"z": 64}.get(length, 32)
                    self.ex._uc.mem_write(dest, struct.pack("<Q", value & ((1 << bits) - 1)))
                    items += 1
            elif conv == "[":
                negate = False
                if j < len(fmt) and fmt[j] == ord("^"):
                    negate = True
                    j += 1
                scan_set = bytearray()
                if j < len(fmt) and fmt[j] == ord("]"):
                    scan_set.append(fmt[j])
                    j += 1
                while j < len(fmt) and fmt[j] != ord("]"):
                    scan_set.append(fmt[j])
                    j += 1
                if j < len(fmt):
                    j += 1
                token = bytearray()
                while data:
                    ok = (data[0] in scan_set) != negate
                    if not ok or (width and len(token) >= width):
                        break
                    token.append(data.pop(0))
                    consumed.append(token[-1])
                if token:
                    self.ex._uc.mem_write(dest, bytes(token) + b"\0")
                    items += 1
            elif conv == "%":
                if data and data[0] == 0x25:
                    consumed.append(data.pop(0))
                arg_index -= 1
            i = j
        self.ex._input = bytes(data)
        self._return(rsp, items)


class _OpenFile:
    def __init__(self, path: str, buf: bytearray):
        self.path = path
        self.buf = buf
        self.pos = 0
