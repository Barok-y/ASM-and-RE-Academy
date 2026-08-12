from __future__ import annotations

from typing import Optional, Tuple

from capstone import CS_ARCH_X86, CS_MODE_64, Cs

from academy.emulator import Executor

from .re import ToyBinary


class PatchingLab:
    def apply_patch(self, code: bytes, offset: int, new_bytes: bytes) -> bytes:
        patched = bytearray(code)
        if offset < 0 or offset + len(new_bytes) > len(patched):
            raise ValueError("patch is out of range")
        patched[offset : offset + len(new_bytes)] = new_bytes
        return bytes(patched)

    def find_instruction(self, code: bytes, mnemonic: str) -> int:
        for insn in Cs(CS_ARCH_X86, CS_MODE_64).disasm(code, 0):
            if insn.mnemonic == mnemonic:
                return insn.address
        raise ValueError(f"no {mnemonic!r} instruction found in binary")

    def flip_jump(self, code: bytes, mnemonic: str) -> bytes:
        offset = self.find_instruction(code, mnemonic)
        opcode = code[offset]
        if 0x70 <= opcode <= 0x7F:
            return self.apply_patch(code, offset, bytes([opcode ^ 1]))
        if opcode == 0x0F and 0x80 <= code[offset + 1] <= 0x8F:
            return self.apply_patch(code, offset + 1, bytes([code[offset + 1] ^ 1]))
        raise ValueError(f"unsupported conditional jump encoding at offset {offset}")

    def run_binary(
        self, binary: ToyBinary, code: Optional[bytes] = None
    ) -> Tuple[bytes, Optional[int]]:
        ex = Executor()
        ex.load_bytes(code if code is not None else binary.code, entry=binary.entry)
        ex.write_memory(0x600000, binary.data)
        ex.run()
        return ex.output, ex.exit_code

    def verify(self, binary: ToyBinary, code: bytes) -> Tuple[bool, str]:
        output, exit_code = self.run_binary(binary, code)
        problems = []
        if binary.expected_output is not None and output != binary.expected_output:
            problems.append(
                f"output {output!r} != expected {binary.expected_output!r}"
            )
        if binary.expected_exit is not None and exit_code != binary.expected_exit:
            problems.append(f"exit code {exit_code!r} != expected {binary.expected_exit!r}")
        if problems:
            return False, "; ".join(problems)
        return True, f"behavior verified (output {output!r}, exit {exit_code})"
