import pytest

from academy.emulator import ExecutionHalted, Executor

DATA_ADDR = 0x600000


def test_single_step_arithmetic_and_flags():
    ex = Executor()
    ex.load_asm(
        """
        mov rax, 5
        sub rax, 5
        sub rax, 1
        """
    )
    s0 = ex.snapshot()
    s1 = ex.step()
    assert ex.get_register("rax") == 5
    assert s1.diff(s0).registers["rax"] == (0, 5)
    assert ex.get_flag("zf") is False
    s2 = ex.step()
    assert ex.get_register("rax") == 0
    assert ex.get_flag("zf") is True
    assert s2.diff(s1).flags["zf"] == (False, True)
    s3 = ex.step()
    assert ex.get_register("rax") == 0xFFFFFFFFFFFFFFFF
    assert ex.get_flag("sf") is True
    assert ex.get_flag("zf") is False
    assert s3.diff(s2).flags["sf"] == (False, True)


def test_subregister_execution():
    ex = Executor()
    ex.load_asm(
        """
        mov eax, 0x12345678
        mov ax, 0xABCD
        mov al, 0x05
        mov ah, 0x7F
        """
    )
    for _ in range(4):
        ex.step()
    assert ex.get_register("rax") == 0x0000000012347F05
    assert ex.get_register("eax") == 0x12347F05
    assert ex.get_register("ax") == 0x7F05
    assert ex.get_register("ah") == 0x7F
    assert ex.get_register("al") == 0x05


def test_memory_store_load():
    ex = Executor()
    ex.load_asm(
        """
        mov rax, 0xDEADBEEF
        mov rdi, 0x600010
        mov [rdi], rax
        mov rbx, [rdi]
        """
    )
    ex.step()
    ex.step()
    ex.step()
    ex.step()
    assert ex.get_register("rbx") == 0xDEADBEEF
    assert ex.read_memory(0x600010, 8) == (0xDEADBEEF).to_bytes(8, "little")


def test_memory_diff():
    ex = Executor()
    ex.load_asm(
        """
        mov rdi, 0x600000
        mov QWORD PTR [rdi], 42
        """
    )
    s0 = ex.snapshot()
    ex.step()
    ex.step()
    s1 = ex.snapshot()
    diff = s1.diff(s0)
    assert "data" in diff.memory
    assert any(offset == 0 for offset, _, _ in diff.memory["data"])


def test_stack_push_pop():
    ex = Executor()
    ex.load_asm(
        """
        mov rax, 0xCAFE
        push rax
        mov rbx, 0
        pop rbx
        """
    )
    sp0 = ex.get_register("rsp")
    ex.step()
    ex.step()
    assert ex.get_register("rsp") == sp0 - 8
    assert int.from_bytes(ex.read_memory(ex.get_register("rsp"), 8), "little") == 0xCAFE
    ex.step()
    ex.step()
    assert ex.get_register("rbx") == 0xCAFE
    assert ex.get_register("rsp") == sp0


def test_syscall_write_and_exit():
    ex = Executor()
    ex.load_asm(
        f"""
        mov rax, 1
        mov rdi, 1
        mov rsi, {DATA_ADDR}
        mov rdx, 13
        syscall
        mov rax, 60
        xor rdi, rdi
        syscall
        """
    )
    ex.write_string("data", "Hello, World!")
    ex.run()
    assert ex.status == "exited"
    assert ex.exit_code == 0
    assert ex.output == b"Hello, World!"


def test_breakpoint():
    ex = Executor()
    ex.load_asm(
        """
        mov rax, 1
        mov rbx, 2
        mov rcx, 3
        """
    )
    ex.step()
    addr = ex.get_register("rip")
    ex.add_breakpoint(addr)
    ex.step()
    assert ex.status == "breakpoint"
    assert ex.get_register("rbx") == 0
    ex.remove_breakpoint(addr)
    ex.step()
    assert ex.get_register("rbx") == 2


def test_run_stops_at_breakpoint():
    ex = Executor()
    ex.load_asm(
        """
        mov rax, 1
        mov rbx, 2
        mov rcx, 3
        """
    )
    ex.step()
    addr = ex.get_register("rip")
    ex.add_breakpoint(addr)
    ex.run()
    assert ex.status == "breakpoint"
    assert ex.get_register("rbx") == 0


def test_reverse_step():
    ex = Executor()
    ex.load_asm(
        """
        mov rax, 1
        add rax, 2
        """
    )
    ex.step()
    ex.step()
    assert ex.get_register("rax") == 3
    previous = ex.step_back()
    assert previous is not None
    assert ex.get_register("rax") == 1
    ex.step_back()
    assert ex.get_register("rax") == 0
    assert ex.step_back() is None


def test_watchpoint():
    ex = Executor()
    ex.load_asm(
        """
        mov rax, 0xDEADBEEF
        mov QWORD PTR [0x600000], rax
        """
    )
    ex.add_watch(0x600000, 8)
    ex.step()
    assert ex.watch_events == []
    ex.step()
    assert len(ex.watch_events) == 1
    addr, old, new = ex.watch_events[0]
    assert addr == 0x600000
    assert new == (0xDEADBEEF).to_bytes(8, "little")


def test_falling_off_code_halts():
    ex = Executor()
    ex.load_asm("mov rax, 1")
    ex.run(max_steps=2)
    assert ex.status in ("error", "halted")


def test_disassemble():
    ex = Executor()
    ex.load_asm(
        """
        mov rax, 1
        add rbx, 2
        """
    )
    lines = ex.disassemble(count=2)
    assert len(lines) == 2
    assert "add" in lines[1]


def test_step_after_exit_raises():
    ex = Executor()
    ex.load_asm(
        """
        mov rax, 60
        syscall
        """
    )
    ex.step()
    ex.step()
    assert ex.status == "exited"
    with pytest.raises(ExecutionHalted):
        ex.step()
