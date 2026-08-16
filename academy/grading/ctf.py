from __future__ import annotations

from typing import List

from .grading import Challenge

CTF_CHALLENGES: List[Challenge] = [
    Challenge(
        id="ctf1",
        challenge_type="reverse_engineering",
        difficulty="medium",
        title="Serial crackme #1",
        spec=(
            "A keygen checks your serial against this logic:\n"
            "  key ^ 0x1337  ==  0x4242\n"
            "Write assembly that computes and leaves the accepted serial in RAX "
            "(so the check passes)."
        ),
        program="mov rax, 0x4242\nxor rax, 0x1337",
        expected={"registers": {"rax": 0x4242 ^ 0x1337}},
        hints=[
            "XOR is its own inverse: a ^ b == c  means  c ^ b == a.",
            "The accepted key is the known value XOR'd with the mask.",
            "Load 0x4242 then xor rax, 0x1337.",
        ],
    ),
    Challenge(
        id="ctf2",
        challenge_type="reverse_engineering",
        difficulty="medium",
        title="Key derivation from flags",
        spec=(
            "A routine computes the key from flags. Re-trace it to find RAX:\n"
            "  1) mov rax, 1\n"
            "  2) add rax, 2        (rax = 3, flags set)\n"
            "  3) lea rax, [rax*2 + rax]   (triple it)\n"
            "  4) xor rax, 0xFF\n"
            "Write assembly that produces the final RAX (the key)."
        ),
        program=(
            "mov rax, 1\n"
            "add rax, 2\n"
            "lea rax, [rax*2 + rax]\n"
            "xor rax, 0xFF"
        ),
        expected={"registers": {"rax": (3 * 3) ^ 0xFF}},
        hints=[
            "Follow the value, ignore flags.",
            "After add, RAX is 3; lea multiplies by 3.",
            "9 ^ 0xFF is the final key.",
        ],
    ),
    Challenge(
        id="ctf3",
        challenge_type="patching",
        difficulty="hard",
        title="Path-swap patch",
        spec=(
            "Trace this bytecode: the branch is taken when the password match "
            "fails. What single-byte patch changes the branch so it is taken "
            "when the password matches?\n\n"
            "  cmp rax, expected\n  jne denied\n\n"
            "Answer: give the value that RAX must hold for 'jne' to fall through "
            "to the grant path (i.e. make the check pass by supplying RAX)."
        ),
        program=(
            "mov rax, 1\nmov rbx, 1\ncmp rax, rbx\njne fail\nmov rax, 0\n"
            "jmp done\nfail:\nmov rax, 99\ndone:"
        ),
        expected={"registers": {"rax": 0}},
        hints=[
            "Making the two operands equal makes 'jne' not jump.",
            "RAX must equal the comparison target.",
            "Load the same value the check compares against.",
        ],
    ),
    Challenge(
        id="ctf4",
        challenge_type="mini_ctf",
        difficulty="expert",
        title="Flag: stack mystery",
        spec=(
            "A flag is written to the stack top-down, one byte at a time:\n"
            "  mov rsp, 0x600000\n"
            "  mov byte [rsp],   'f'\n"
            "  mov byte [rsp+1], 'l'\n"
            "  mov byte [rsp+2], 'a'\n"
            "  mov byte [rsp+3], 'g'\n"
            "What value ends up at address 0x600000 as a 32-bit little-endian "
            "integer? Leave it in RAX."
        ),
        program="mov rax, 0x67616c66",
        expected={"registers": {"rax": 0x67616c66}},
        hints=[
            "Empty bytes are a problem — clear RAX first.",
            "Little-endian: the first byte is the low 8 bits.",
            "Assemble 'f','l','a','g' = 0x67616c66.",
        ],
    ),
    Challenge(
        id="ctf5",
        challenge_type="debugging",
        difficulty="easy",
        title="Find the off-by-one",
        spec=(
            "A sum routine is off by one. Given\n"
            "  mov rax, 10\n"
            "  dec rax\n"
            "  inc rax\n"
            "  add rax, 1\n"
            "What is RAX, and which single instruction is a no-op you can remove?"
        ),
        program="mov rax, 10\ndec rax\ninc rax\nadd rax, 1",
        expected={"registers": {"rax": 11}},
        hints=[
            "dec then inc cancel each other out.",
            "Only the final add changes the value.",
            "Result is 10 + 1 = 11.",
        ],
    ),
    Challenge(
        id="ctf6",
        challenge_type="reverse_engineering",
        difficulty="medium",
        title="Crack the serial: flag = key",
        spec=(
            "A crackme grants access when your serial equals:\n"
            "  (0x53454352 ^ 0x11111111)\n"
            "Compute the serial its check compares against and leave it in RAX. "
            "This is the classic 'license = constant XOR mask' crackme pattern."
        ),
        program="mov rax, 0x53454352\nxor rax, 0x11111111",
        expected={"registers": {"rax": 0x53454352 ^ 0x11111111}},
        hints=[
            "XOR with a constant is the crackme's favourite obfuscation.",
            "The accepted value is the constant XOR'd with the mask.",
            "0x53454352 ^ 0x11111111 is the serial.",
        ],
    ),
    Challenge(
        id="ctf7",
        challenge_type="patching",
        difficulty="hard",
        title="Binary surgeon",
        spec=(
            "A license checker does:\n"
            "  cmp rax, 0x1337\n  je  grant\n"
            "Rather than changing data, flip 'je' to 'jne'. Which condition "
            "should the CPU take so that a WRONG key is rejected but a RIGHT one "
            "still passes? Supply RAX = the only value the check accepts."
        ),
        program=(
            "mov rax, 0x1337\ncmp rax, 0x1337\nje grant\nmov rax, 0\n"
            "jmp done\ngrant:\nmov rax, 1\ndone:"
        ),
        expected={"registers": {"rax": 1}},
        hints=[
            "Match the value the check compares against.",
            "The check compares RAX to 0x1337.",
            "Set RAX = 0x1337 so 'je' is taken.",
        ],
    ),
    Challenge(
        id="ctf8",
        challenge_type="mini_ctf",
        difficulty="expert",
        title="FLAG: endian trap",
        spec=(
            "A packet stores the flag 'PWN\\x00' as a 32-bit little-endian word "
            "in memory. If the CPU reads it as little-endian into RAX, what is "
            "the raw integer value?"
        ),
        program="mov rax, 0x00574e57",
        expected={"registers": {"rax": 0x00574E57}},
        hints=[
            "PWN = 0x57 0x4e 0x57 0x00 in little-endian memory order.",
            "The address holds bytes 57 4E 57 00.",
            "As a little-endian word that is 0x00574E57.",
        ],
    ),
    Challenge(
        id="ctf9",
        challenge_type="reverse_engineering",
        difficulty="hard",
        title="Trace the stack canary",
        spec=(
            "A password routine stacks the letters of the password, then checks "
            "them back off top-down. Write assembly that reconstructs 'p', then "
            "'a', then 'ss' into RAX in one pops-worth logic:\n"
            "  mov rsp, 0x600000\n"
            "  mov   [rsp+0], 'p'\n"
            "  mov   [rsp+1], 'a'\n"
            "  mov   [rsp+2], 's'\n"
            "Compute the 32-bit little-endian integer that ends up at [rsp+0]."
        ),
        program="mov rax, 0x00736170",
        expected={"registers": {"rax": 0x00736170}},
        hints=[
            "Memory order: 'p','a','s' in ascending addresses.",
            "80x 'pas' little-endian = 0x00736170.",
            "The low byte is 'p' (0x70).",
        ],
    ),
    Challenge(
        id="ctf10",
        challenge_type="debugging",
        difficulty="easy",
        title="Find the bug",
        spec=(
            "Someone tried to set RAX=25 but messed up:\n"
            "  mov rax, 5\n  add rax, 5\n  add rax, 5\n"
            "They set RAX=15, but wanted 25? No—they actually wanted 15. "
            "Answer: what single (already present) value does the code reach?"
        ),
        program="mov rax, 5\nadd rax, 5\nadd rax, 5",
        expected={"registers": {"rax": 15}},
        hints=[
            "Start from 5, add 5 twice.",
            "5 + 5 + 5 = 15.",
            "The code is actually correct.",
        ],
    ),
    Challenge(
        id="ctf11",
        challenge_type="reverse_engineering",
        difficulty="expert",
        title="OracleVM bytecode decode",
        spec=(
            "The ADWA 'OracleVM' crackme (a stripped 64-bit ELF, see "
            "academy/curriculum/binaries/oracle_vm) installs a SIGILL handler "
            "that XOR-decodes a hidden 6-byte VM program against the key "
            "b'UUUUUU' before the VM runs it. Trace the handler and the VM to "
            "recover the decoded bytecode, then write assembly that implements "
            "that bytecode faithfully — including the 0x10 op, which loads its "
            "NEXT byte as an operand and skips it (so the '!' opcode at index 1 "
            "never executes and the input is never checked). The 0xff op checks "
            "the accumulator against 0xE4682EAE8. Leave the final accumulator "
            "in R8."
        ),
        program=(
            "mov rbx, 0x600000\n"
            "mov byte ptr [rbx], 0x10\n"
            "mov byte ptr [rbx+1], '!'\n"
            "mov byte ptr [rbx+2], '2'\n"
            "mov byte ptr [rbx+3], 'D'\n"
            "mov byte ptr [rbx+4], 'U'\n"
            "mov byte ptr [rbx+5], 0xff\n"
            "mov rax, 0x1337\n"
            "mov rcx, 0\n"
            "loop:\n"
            "    mov sil, byte ptr [rbx+rcx]\n"
            "    cmp sil, 0xff\n"
            "    je done\n"
            "    cmp sil, 0x10\n"
            "    je op_load\n"
            "    cmp sil, '2'\n"
            "    je op_two\n"
            "    cmp sil, 'D'\n"
            "    je op_d\n"
            "    cmp sil, 'U'\n"
            "    je op_u\n"
            "    jmp loop\n"
            "op_load:\n"
            "    add rcx, 2\n"
            "    jmp loop\n"
            "op_two:\n"
            "    add rax, 0x41424344\n"
            "    inc rcx\n"
            "    jmp loop\n"
            "op_d:\n"
            "    rol rax, 3\n"
            "    inc rcx\n"
            "    jmp loop\n"
            "op_u:\n"
            "    imul rax, 7\n"
            "    inc rcx\n"
            "    jmp loop\n"
            "done:\n"
            "    mov r8, rax\n"
            "    mov rax, 60\n"
            "    mov rdi, 0\n"
            "    syscall"
        ),
        expected={"registers": {"r8": 0xE4682EAE8}},
        hints=[
            "The SIGILL handler XORs 6 bytes of .data with the key at 0x404060.",
            "0x404060 = 'UUUUUU'; key bytes at 0x404070 are 45 74 67 11 00 AA.",
            "Decode: 45^55=10, 74^55=21, 67^55=32, 11^55=44, 00^55=55, AA^55=FF.",
            "0x10 is a load-operand op: it consumes the next byte ('!' at index "
            "1) and advances the pc by 2 — the XOR-input op never runs.",
            "The check ignores input: acc starts 0x1337, add 0x41424344, rol 3, "
            "*7, compare 0xE4682EAE8.",
        ],
        flag="ASM{10_21_32_44_55_ff}",
    ),
]


def ctf_challenges() -> List[Challenge]:
    return list(CTF_CHALLENGES)
