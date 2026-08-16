"""Native ELF loading + libc shim, exercised against the bundled OracleVM crackme."""

import os

from academy.emulator import Executor
from academy.emulator.elf import ElfError, load_elf

ORACLE = os.path.join(
    os.path.dirname(__file__),
    "..",
    "academy",
    "curriculum",
    "binaries",
    "oracle_vm",
)


def test_elf_load_parses_oracle_metadata():
    binary = load_elf(ORACLE)
    assert binary.load_range[0] <= 0x401160 <= binary.load_range[1]
    assert "puts" in binary.imports.values()
    assert "signal" in binary.imports.values()
    assert "raise" in binary.imports.values()
    # the SIGILL handler XOR-decodes against these two .data tables
    assert binary.read_at(0x404060, 6) == b"UUUUUU"
    assert binary.read_at(0x404070, 6) == bytes([0x45, 0x74, 0x67, 0x11, 0x00, 0xAA])


def test_elf_load_missing_file_raises():
    import pytest

    with pytest.raises(ElfError):
        load_elf("/nonexistent/oracle_vm")


def test_elf_run_oracle_blesses_any_flag():
    ex = Executor(max_history=50)
    ex.load_elf(ORACLE, input=b"anything_works\n")
    ex.run(max_steps=500_000)
    assert ex.status == "exited"
    assert ex.exit_code == 0
    assert b"[+] Signal handler triggered" in ex.output
    assert b"Correct flag!" in ex.output


def test_elf_run_oracle_decodes_hidden_bytecode():
    ex = Executor(max_history=50)
    ex.load_elf(ORACLE, input=b"\n")
    ex.run(max_steps=500_000)
    assert ex.status == "exited"
    # handler XOR-decodes 6 bytes of .data into 0x404090
    decoded = ex.memory_read(0x404090, 6)
    assert decoded == bytes([0x10, 0x21, 0x32, 0x44, 0x55, 0xFF])
    # the whole VM check runs regardless of input (0x10 consumes '!' as operand)
    assert b"Correct flag!" in ex.output


def test_elf_elf_strings_reads_rodata():
    ex = Executor(max_history=50)
    ex.load_elf(ORACLE)
    assert ex.elf_strings(0x402058) == "=== OracleVM ==="
