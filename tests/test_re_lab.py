import pytest

from academy.debugger import build_cfg, find_functions, find_strings
from academy.emulator import Executor
from academy.sandbox import PatchingLab, ReverseEngineeringLab
from academy.sandbox.toy import (
    build_function_sample,
    build_license_check,
    build_password_check,
    toy_binaries,
)


def test_license_check_original_behavior():
    lab = PatchingLab()
    binary = build_license_check()
    output, exit_code = lab.run_binary(binary)
    assert output == b"Access denied\n"
    assert exit_code == 0


def test_license_check_patch_flip_je():
    lab = PatchingLab()
    binary = build_license_check()
    ok, _ = lab.verify(binary, binary.code)
    assert not ok
    patched = lab.flip_jump(binary.code, "je")
    ok, message = lab.verify(binary, patched)
    assert ok, message


def test_password_check_patch_flip_jne():
    lab = PatchingLab()
    binary = build_password_check()
    assert lab.run_binary(binary)[0] == b"Wrong password\n"
    patched = lab.flip_jump(binary.code, "jne")
    ok, message = lab.verify(binary, patched)
    assert ok, message


def test_apply_patch_range_validation():
    lab = PatchingLab()
    with pytest.raises(ValueError):
        lab.apply_patch(b"\x90", 5, b"\x00")
    with pytest.raises(ValueError):
        lab.apply_patch(b"\x90", 0, b"\x00\x00")


def test_find_instruction():
    lab = PatchingLab()
    binary = build_license_check()
    assert lab.find_instruction(binary.code, "je") >= 0
    with pytest.raises(ValueError):
        lab.find_instruction(binary.code, "vpunop")


def test_cfg_blocks_and_successors():
    binary = build_license_check()
    cfg = build_cfg(binary.code, binary.entry)
    assert len(cfg.blocks) >= 4
    entry_block = cfg.block_at(binary.entry)
    assert entry_block is not None
    assert any(s > binary.entry for s in entry_block.successors)
    terminal = [b for b in cfg.blocks if not b.successors]
    assert terminal, "expected a terminal block"


def test_find_functions():
    binary = build_function_sample()
    functions = find_functions(binary.code, binary.entry)
    names = [f.name for f in functions]
    assert len(functions) == 2
    assert "func_400000" in names
    assert "func_400020" in names


def test_find_strings():
    data = b"\x00hello\x00world\x00\x00\xff"
    assert find_strings(data) == ["hello", "world"]


def test_re_lab_analysis():
    lab = ReverseEngineeringLab()
    result = lab.analyze(build_license_check())
    assert "je" in result.disassembly
    assert "Access granted" in result.strings
    assert "functions:" in result.summary()


def test_toy_binaries_all_verifiable():
    binaries = toy_binaries()
    assert len(binaries) == 4
    for binary in binaries:
        ex = Executor()
        ex.load_bytes(binary.code, entry=binary.entry)
        ex.write_memory(0x600000, binary.data)
        state = ex.run(max_steps=1000)
        assert state.status in ("running", "exited", "error")
