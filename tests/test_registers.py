from unicorn import UC_ARCH_X86, UC_MODE_64, Uc

from academy.emulator import registers as regs


def test_subregister_table():
    assert regs.REGISTER_TABLE["eax"] == ("rax", 0xFFFFFFFF, 0)
    assert regs.REGISTER_TABLE["ax"] == ("rax", 0xFFFF, 0)
    assert regs.REGISTER_TABLE["ah"] == ("rax", 0xFF00, 8)
    assert regs.REGISTER_TABLE["al"] == ("rax", 0xFF, 0)
    assert regs.REGISTER_TABLE["sil"] == ("rsi", 0xFF, 0)
    assert regs.REGISTER_TABLE["spl"] == ("rsp", 0xFF, 0)
    assert regs.REGISTER_TABLE["r8b"] == ("r8", 0xFF, 0)
    assert regs.REGISTER_TABLE["r15d"] == ("r15", 0xFFFFFFFF, 0)
    assert regs.REGISTER_TABLE["rip"] == ("rip", 0xFFFFFFFFFFFFFFFF, 0)


def test_subregister_read_write():
    uc = Uc(UC_ARCH_X86, UC_MODE_64)
    regs.write_register(uc, "rax", 0x1122334455667788)
    assert regs.read_register(uc, "eax") == 0x55667788
    assert regs.read_register(uc, "ax") == 0x7788
    assert regs.read_register(uc, "ah") == 0x77
    assert regs.read_register(uc, "al") == 0x88
    regs.write_register(uc, "al", 0x11)
    assert regs.read_register(uc, "rax") == 0x1122334455667711
    regs.write_register(uc, "ax", 0x2233)
    assert regs.read_register(uc, "rax") == 0x1122334455662233


def test_32bit_write_zeroes_upper():
    uc = Uc(UC_ARCH_X86, UC_MODE_64)
    regs.write_register(uc, "rax", 0xFFFFFFFFFFFFFFFF)
    regs.write_register(uc, "eax", 0xDEADBEEF)
    assert regs.read_register(uc, "rax") == 0xDEADBEEF
