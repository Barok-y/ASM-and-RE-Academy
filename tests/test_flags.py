from unicorn import UC_ARCH_X86, UC_MODE_64, Uc

from academy.emulator import flags as fflags


def test_read_flags_from_rflags():
    uc = Uc(UC_ARCH_X86, UC_MODE_64)
    fflags.write_rflags(uc, 0b0000000001000001)
    flags = fflags.read_flags(uc)
    assert flags["cf"] is True
    assert flags["zf"] is True
    assert flags["sf"] is False
    assert flags["of"] is False
