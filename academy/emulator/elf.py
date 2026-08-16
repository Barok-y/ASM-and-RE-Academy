"""Minimal ELF64 parser for loading real crackme binaries into the emulator.

Supports ET_EXEC and ET_DYN (PIE) x86-64 files: extracts PT_LOAD segments,
symbol tables, dynamic relocations, and the GOT->import mapping used by the
libc shim to trap calls into the PLT.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

EI_CLASS = 4
EI_DATA = 5
ELFCLASS64 = 2
ELFDATA2LSB = 1
EM_X86_64 = 62
ET_EXEC = 2
ET_DYN = 3
PT_LOAD = 1
SHT_SYMTAB = 2
SHT_STRTAB = 3
SHT_RELA = 4
SHT_DYNSYM = 11
STT_FUNC = 2


class ElfError(ValueError):
    pass


@dataclass
class ElfSegment:
    offset: int
    vaddr: int
    filesz: int
    memsz: int
    flags: int
    name: str = ""

    @property
    def perms(self) -> int:
        from unicorn import UC_PROT_EXEC, UC_PROT_READ, UC_PROT_WRITE

        perms = 0
        if self.flags & 0x4:
            perms |= UC_PROT_READ
        if self.flags & 0x2:
            perms |= UC_PROT_WRITE
        if self.flags & 0x1:
            perms |= UC_PROT_EXEC
        return perms


@dataclass
class ElfBinary:
    path: str
    data: bytes
    entry: int
    is_pie: bool
    segments: List[ElfSegment] = field(default_factory=list)
    imports: Dict[int, str] = field(default_factory=dict)
    symbols: Dict[str, int] = field(default_factory=dict)
    sections: Dict[str, Tuple[int, int, int, int]] = field(default_factory=dict)

    @property
    def load_range(self) -> Tuple[int, int]:
        """Lowest and highest mapped byte of any load segment."""
        if not self.segments:
            return (0, 0)
        low = min(s.vaddr for s in self.segments)
        high = max(s.vaddr + s.memsz for s in self.segments)
        return (low, high)

    def read_at(self, addr: int, size: int) -> bytes:
        for seg in self.segments:
            if seg.vaddr <= addr < seg.vaddr + seg.filesz:
                off = seg.offset + (addr - seg.vaddr)
                return self.data[off : off + size]
        return b""

    def strings(self, addr: int, limit: int = 256) -> str:
        raw = self.read_at(addr, limit)
        end = raw.find(b"\0")
        if end == -1:
            end = len(raw)
        return raw[:end].decode("latin1")

    def section(self, name: str) -> Optional[Tuple[int, int, int, int]]:
        return self.sections.get(name)


def load_elf(path: str) -> ElfBinary:
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError as exc:
        raise ElfError(f"cannot open ELF: {path}: {exc}") from exc
    if len(data) < 64 or data[:4] != b"\x7fELF":
        raise ElfError(f"not an ELF file: {path}")
    if data[EI_CLASS] != ELFCLASS64:
        raise ElfError("only 64-bit ELF is supported")
    if data[EI_DATA] != ELFDATA2LSB:
        raise ElfError("only little-endian ELF is supported")
    e_type, e_machine = struct.unpack_from("<HH", data, 0x10)
    if e_machine != EM_X86_64:
        raise ElfError(f"unsupported machine {e_machine:#x}")
    if e_type not in (ET_EXEC, ET_DYN):
        raise ElfError(f"unsupported ELF type {e_type:#x}")
    (entry,) = struct.unpack_from("<Q", data, 0x18)
    (phoff,) = struct.unpack_from("<Q", data, 0x20)
    (shoff,) = struct.unpack_from("<Q", data, 0x28)
    phentsize, phnum = struct.unpack_from("<HH", data, 0x36)
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", data, 0x3A)

    binary = ElfBinary(
        path=path,
        data=data,
        entry=entry,
        is_pie=e_type == ET_DYN,
    )

    for i in range(phnum):
        off = phoff + i * phentsize
        if off + 56 > len(data):
            break
        p_type, p_flags = struct.unpack_from("<II", data, off)
        p_offset, p_vaddr = struct.unpack_from("<QQ", data, off + 8)
        p_filesz, p_memsz = struct.unpack_from("<QQ", data, off + 32)
        if p_type == PT_LOAD:
            binary.segments.append(
                ElfSegment(p_offset, p_vaddr, p_filesz, p_memsz, p_flags)
            )

    if not binary.segments:
        raise ElfError("no PT_LOAD segments found")

    sections_raw = []
    shstr = b""
    for i in range(shnum):
        off = shoff + i * shentsize
        if off + 64 > len(data):
            break
        sh_name, sh_type = struct.unpack_from("<II", data, off)
        sh_flags, sh_addr = struct.unpack_from("<QQ", data, off + 8)
        sh_offset, sh_size = struct.unpack_from("<QQ", data, off + 24)
        sections_raw.append((sh_name, sh_type, sh_addr, sh_offset, sh_size))
        if i == shstrndx:
            shstr = data[sh_offset : sh_offset + sh_size]

    def secname(n: int) -> str:
        if n >= len(shstr):
            return ""
        end = shstr.index(b"\0", n) if b"\0" in shstr[n:] else len(shstr)
        return shstr[n:end].decode("latin1")

    for sh_name, sh_type, sh_addr, sh_offset, sh_size in sections_raw:
        name = secname(sh_name)
        if name:
            binary.sections[name] = (sh_type, sh_addr, sh_offset, sh_size)

    def read_section(name: str) -> bytes:
        sec = binary.sections.get(name)
        if sec is None:
            return b""
        _ty, _addr, offset, size = sec
        return data[offset : offset + size]

    def str_at(tab: bytes, n: int) -> str:
        if n >= len(tab):
            return ""
        end = tab.find(b"\0", n)
        if end == -1:
            end = len(tab)
        return tab[n:end].decode("latin1")

    dynsym = read_section(".dynsym")
    dynstr = read_section(".dynstr")
    symtab = read_section(".symtab")
    strtab = read_section(".strtab")

    # imports: every SHT_RELA relocation (lazy .rela.plt and eager .rela.dyn)
    for name, (sh_type, _addr, offset, size) in binary.sections.items():
        if sh_type != SHT_RELA:
            continue
        for off in range(offset, offset + size, 24):
            if off + 24 > len(data):
                break
            r_offset, r_info = struct.unpack_from("<QQ", data, off)
            sym = r_info >> 32
            if sym * 24 + 4 <= len(dynsym):
                st_name = struct.unpack_from("<I", dynsym, sym * 24)[0]
            else:
                st_name = 0
            import_name = str_at(dynstr, st_name)
            if import_name:
                binary.imports[r_offset] = import_name

    # symbols from symtab (preferred) then dynsym
    for entries, tab in ((symtab, strtab), (dynsym, dynstr)):
        for off in range(0, len(entries), 24):
            if off + 24 > len(entries):
                break
            st_name, st_info = struct.unpack_from("<II", entries, off)
            st_shndx = struct.unpack_from("<H", entries, off + 6)[0]
            (st_value,) = struct.unpack_from("<Q", entries, off + 8)
            if st_name and st_shndx != 0 and (st_info >> 4) == STT_FUNC:
                name = str_at(tab, st_name)
                if name and name not in binary.symbols:
                    binary.symbols[name] = st_value

    return binary
