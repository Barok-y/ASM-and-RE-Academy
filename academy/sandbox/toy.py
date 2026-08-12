from __future__ import annotations

from keystone import KS_ARCH_X86, KS_MODE_64, Ks

from .re import ToyBinary

_DATA_BASE = 0x600000
_KEY_ADDR = _DATA_BASE
_MSG_DENIED_ADDR = _DATA_BASE + 0x10
_MSG_GRANTED_ADDR = _DATA_BASE + 0x20


def _assemble(source: str) -> bytes:
    encoding, _ = Ks(KS_ARCH_X86, KS_MODE_64).asm(source)
    return bytes(encoding)


def build_license_check() -> ToyBinary:
    code = _assemble(
        f"""
        mov rax, [0x{_KEY_ADDR:x}]
        cmp rax, 0x1337
        je granted
        mov rsi, 0x{_MSG_DENIED_ADDR:x}
        mov rdx, 14
        mov rax, 1
        mov rdi, 1
        syscall
        jmp done
    granted:
        mov rsi, 0x{_MSG_GRANTED_ADDR:x}
        mov rdx, 15
        mov rax, 1
        mov rdi, 1
        syscall
    done:
        mov rax, 60
        xor rdi, rdi
        syscall
        """
    )
    data = (
        (0xDEAD).to_bytes(8, "little")
        + b"\x00" * 8
        + b"Access denied\n".ljust(16, b"\x00")
        + b"Access granted\n".ljust(16, b"\x00")
    )
    return ToyBinary(
        name="license_check",
        code=code,
        data=data,
        entry=0x400000,
        description="A toy license check that rejects the hardcoded key 0xDEAD.",
        task="Patch the conditional jump so the program prints 'Access granted' "
        "even though the key is wrong.",
        expected_output=b"Access granted\n",
        expected_exit=0,
    )


def build_password_check() -> ToyBinary:
    code = _assemble(
        f"""
        mov rax, [0x{_KEY_ADDR:x}]
        cmp rax, 0x1337
        jne denied
        mov rsi, 0x{_MSG_GRANTED_ADDR:x}
        mov rdx, 9
        mov rax, 1
        mov rdi, 1
        syscall
        jmp done
    denied:
        mov rsi, 0x{_MSG_DENIED_ADDR:x}
        mov rdx, 15
        mov rax, 1
        mov rdi, 1
        syscall
    done:
        mov rax, 60
        xor rdi, rdi
        syscall
        """
    )
    data = (
        (0xDEAD).to_bytes(8, "little")
        + b"\x00" * 8
        + b"Wrong password\n".ljust(16, b"\x00")
        + b"Correct!\n".ljust(16, b"\x00")
    )
    return ToyBinary(
        name="password_check",
        code=code,
        data=data,
        entry=0x400000,
        description="A toy password check that rejects the current key.",
        task="Patch a conditional jump so 'Correct!' prints without changing the data.",
        expected_output=b"Correct!\n",
        expected_exit=0,
    )


def build_function_sample() -> ToyBinary:
    code = _assemble(
        """
        mov rax, 1
        call helper
        mov rbx, rax
        call helper
        add rax, rbx
        mov rax, 60
        syscall
    helper:
        add rax, 5
        ret
        """
    )
    return ToyBinary(
        name="function_sample",
        code=code,
        data=b"",
        entry=0x400000,
        description="A sample with two functions and call/ret for CFG practice.",
        task="Identify the functions and their boundaries.",
    )


CAMPAIGN_FLAG = "ASM{DUNGEON_HEART_7F1E}"


def build_flag_vault() -> ToyBinary:
    flag_addr = _DATA_BASE + 0x30
    code = _assemble(
        f"""
        mov rsi, 0x{flag_addr:x}
        mov rdx, 0x20
        mov rax, 1
        mov rdi, 1
        syscall
        mov rax, 60
        xor rdi, rdi
        syscall
        """
    )
    data = (
        (0xDEAD).to_bytes(8, "little")
        + b"\x00" * 8
        + b"A vault sleeps...\n".ljust(20, b"\x00")
        + CAMPAIGN_FLAG.encode("ascii").ljust(32, b"\x00")
    )
    return ToyBinary(
        name="flag_vault",
        code=code,
        data=data,
        entry=0x400000,
        description="The final vault: run it to discover the hidden campaign flag.",
        task="Find the hidden flag in the vault's data segment (auto-run to reveal).",
        expected_output=CAMPAIGN_FLAG.encode("ascii") + b"\x00" * 24,
        expected_exit=0,
    )


def toy_binaries() -> list:
    return [
        build_license_check(),
        build_password_check(),
        build_function_sample(),
        build_flag_vault(),
    ]
