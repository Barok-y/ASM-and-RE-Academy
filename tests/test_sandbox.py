import pytest

from academy.sandbox import Sandbox


def test_execute_steps_with_explanation():
    sb = Sandbox()
    sb.executor.load_asm(
        """
        mov rax, 5
        add rax, 2
        """
    )
    r = sb.execute("step")
    assert "rax" in r.text
    r = sb.execute("step")
    assert "rax" in r.text
    assert sb.executor.get_register("rax") == 7


def test_execute_registers_and_flags():
    sb = Sandbox()
    sb.executor.load_asm(
        """
        mov rax, 1
        sub rax, 1
        """
    )
    sb.execute("step")
    sb.execute("step")
    r = sb.execute("registers")
    assert "rax" in r.text
    f = sb.execute("flags")
    assert "ZF=1" in f.text


def test_execute_unknown_command():
    sb = Sandbox()
    with pytest.raises(ValueError):
        sb.execute("bogus")


def test_run_with_output():
    sb = Sandbox()
    sb.executor.load_asm(
        """
        mov rax, 1
        mov rdi, 1
        mov rsi, 0x600000
        mov rdx, 4
        syscall
        mov rax, 60
        mov rdi, 3
        syscall
        """
    )
    sb.executor.write_string("data", "ab cd")
    r = sb.execute("run")
    assert sb.executor.output == b"ab c"
    assert "exited" in r.text
    assert sb.executor.exit_code == 3


def test_hexdump_command():
    sb = Sandbox()
    sb.executor.load_asm("mov rax, 1")
    sb.executor.write_memory(0x600000, b"\x00\x01\x02\xff\x41")
    r = sb.execute("memory 0x600000 5")
    assert "0000000000600000" in r.text
    assert "41" in r.text


def test_break_and_watch_commands():
    sb = Sandbox()
    sb.executor.load_asm(
        """
        mov rax, 1
        mov rbx, 2
        """
    )
    sb.execute("step")
    addr = sb.executor.get_register("rip")
    sb.execute(f"break 0x{addr:x}")
    assert sb.executor.breakpoints == [addr]
    r = sb.execute("break")
    assert f"0x{addr:016x}" in r.text
    sb.execute("watch 0x600000 8")
    r = sb.execute("watch")
    assert f"0x{0x600000:016x}" in r.text


def test_trace():
    sb = Sandbox()
    sb.executor.load_asm(
        """
        mov rax, 1
        add rax, 2
        """
    )
    r = sb.execute("trace 5")
    assert "rax" in r.text
    assert sb.executor.get_register("rax") == 3


def test_explain_command():
    sb = Sandbox()
    sb.executor.load_asm("mov rax, 7")
    r = sb.execute("explain")
    assert "initial state" in r.text
    sb.execute("step")
    r = sb.execute("explain")
    assert "rax" in r.text


def test_next_steps_over_call():
    sb = Sandbox()
    sb.executor.load_asm(
        """
        mov rax, 1
        call foo
        mov rbx, rax
        mov rax, 60
        syscall
    foo:
        add rax, 5
        ret
        """
    )
    sb.execute("step")
    r = sb.execute("next")
    assert sb.executor.get_register("rax") == 6
    assert r.command == "next"
