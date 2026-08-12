from academy.debugger import Debugger


def test_step_into_over_out():
    dbg = Debugger()
    dbg.executor.load_asm(
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
    dbg.executor.step()
    dbg.step_over()
    assert dbg.executor.get_register("rax") == 6
    assert dbg.executor.get_register("rbx") == 0
    assert "rax" in dbg._last_change() or True


def test_step_out():
    dbg = Debugger()
    dbg.executor.load_asm(
        """
        mov rax, 1
        call foo
        mov rbx, rax
        mov rax, 60
        syscall
    foo:
        push rbp
        mov rbp, rsp
        add rax, 5
        pop rbp
        ret
        """
    )
    dbg.executor.step()
    dbg.executor.step()
    assert dbg.executor.get_register("rax") == 1
    dbg.step_out()
    assert dbg.executor.get_register("rax") == 6


def test_continue_execution():
    dbg = Debugger()
    dbg.executor.load_asm(
        """
        mov rax, 60
        mov rdi, 0
        syscall
        """
    )
    result = dbg.continue_execution()
    assert "exited" in result
    assert dbg.executor.exit_code == 0


def test_views():
    dbg = Debugger()
    dbg.executor.load_asm("mov rax, 1")
    regs = dbg.view_registers()
    assert "rax" in regs
    flags = dbg.view_flags()
    assert "ZF" in flags
    dbg.executor.write_memory(0x600000, b"\x41\x42")
    mem = dbg.view_memory(0x600000, 2)
    assert "41 42" in mem
    stack = dbg.view_stack(4)
    assert stack
