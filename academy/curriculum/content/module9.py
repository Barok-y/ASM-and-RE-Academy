from __future__ import annotations

import struct

from ..models import Lesson, LessonStep, Module
from ._asm import read_asm

# win() sits 0x30 bytes into the text segment of the L1 ret2win programs
# (0x400000 base + 0x30 = 0x400030).
_L1_WIN_ADDR = 0x400030
_L1_PAYLOAD = b"A" * 40 + struct.pack("<Q", _L1_WIN_ADDR)


def _step(kind: str, content: str = "", **kwargs) -> LessonStep:
    return LessonStep(kind=kind, content=content, **kwargs)


def lesson_ret2win() -> Lesson:
    return Lesson(
        id="module9.lesson1",
        module="module9",
        title="Return-to-Win (Stack Smash)",
        order=1,
        steps=[
            _step(
                "concept",
                "A ret2win is the gentlest introduction to stack smashing. The "
                "vulnerable function reads far more bytes than its stack buffer "
                "holds, so the input walks over the saved return address. The "
                "payload is: enough padding to reach the return address, then the "
                "address of a 'win' function that the normal control flow never "
                "calls. When the vulnerable function returns, RET pops that "
                "attacker-chosen address instead of the real one.",
            ),
            _step(
                "intuition",
                "The saved return address is just a value on the stack. If a "
                "buffer overflow reaches it, 'return' becomes 'jump wherever the "
                "attacker wants'. The layout to know by heart, low to high: the "
                "buffer, the saved frame pointer, then the return address.",
            ),
            _step(
                "analogy",
                "A train routed by a note pinned to the last carriage. The "
                "overflow lets you rewrite that note, so when the train 'returns' "
                "from the yard it takes the route you wrote - straight to win().",
            ),
            _step(
                "visualization",
                "vuln's stack frame (low -> high addresses):\n"
                "  +0   buffer[0..31]     32 bytes\n"
                "  +32  saved rbp         8 bytes\n"
                "  +40  return address    8 bytes   <- RET pops this\n"
                "payload = 40 bytes padding + pack('<Q', win_addr)\n"
                "win() at 0x400030 never runs in normal flow - the smash sends "
                "control there.",
            ),
            _step(
                "example",
                "vuln() reads 128 bytes into a 32-byte stack buffer, then "
                "returns. Run with no input: the read returns 0 and the function "
                "exits cleanly without overflowing.",
                high_level="char buf[32]; read(0, buf, 128); // overflow!",
                program=read_asm("module9/lesson1_ret2win/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step through: PUSH RBP saves the frame pointer, SUB RSP, 32 "
                "carves the buffer, and the SYS_READ fills it. The TEST RAX, RAX "
                "guard exits cleanly when nothing was read; with a real payload "
                "the LEAVE/RET would pop the saved rbp and then RET would pop the "
                "attacker's win() address into RIP.",
                program=read_asm("module9/lesson1_ret2win/example.asm"),
            ),
            _step(
                "prediction",
                "vuln's buffer is 32 bytes. Between the buffer and the saved "
                "return address sits the saved rbp. How many padding bytes must "
                "the payload place before the win() address?",
                program=read_asm("module9/lesson1_ret2win/example.asm"),
                options=["32", "40", "128", "8"],
                answer=1,
                feedback={
                    0: "32 fills only the buffer; the saved rbp and return "
                        "address still follow.",
                    2: "128 is the read() size, not the padding distance.",
                    3: "8 is the size of the saved rbp alone.",
                },
                hint="Buffer (32) + saved rbp (8) = 40 bytes before the return address.",
            ),
            _step(
                "response",
                "win() begins 0x30 bytes into the text segment. The emulator "
                "loads code at text base 0x400000. Type the hex runtime address "
                "of win() that the payload's trailing 8 bytes must encode "
                "(little-endian).",
                program=read_asm("module9/lesson1_ret2win/example.asm"),
                keywords=["0x400030", "400030"],
                model_answer="0x400030 - text base 0x400000 plus the 0x30-byte "
                    "offset of win(); the payload ends with pack('<Q', 0x400030).",
                hint="base + offset = 0x400000 + 0x30.",
            ),
            _step(
                "feedback",
                "win() is at 0x400030. The full payload is 40 'A' bytes followed "
                "by the 8-byte little-endian encoding of 0x400030 "
                "(bytes 30 00 40 00 00 00 00 00). Feeding that input makes the "
                "read return 48, the guard falls through, LEAVE/RET recover "
                "control from the overwritten stack, and RET lands in win(), "
                "which prints WIN!.",
            ),
            _step(
                "challenge",
                "Smash the stack: feed the payload 'A'*40 + pack('<Q', 0x400030) "
                "to vuln() so RET redirects control into win(), which prints "
                "WIN!. The reference payload is already wired into the step's "
                "expected input - verify it prints the win banner.",
                program=read_asm("module9/lesson1_ret2win/challenge.asm"),
                expected={"input": _L1_PAYLOAD, "output": b"WIN!"},
            ),
            _step(
                "reflection",
                "If the binary had a stack canary checked before RET, this exact "
                "payload would abort the program. What part of the exploit does a "
                "canary detect, and what primitive does an attacker need to leak "
                "one?",
            ),
        ],
    )


def lesson_format_leak() -> Lesson:
    return Lesson(
        id="module9.lesson2",
        module="module9",
        title="Format String / Offset Leak",
        order=2,
        steps=[
            _step(
                "concept",
                "Format-string and offset-read vulnerabilities give the attacker "
                "an arbitrary read: a user-supplied value selects which memory "
                "the program dereferences. Here the vulnerable routine reads one "
                "attacker-chosen byte and leaks the flag byte at "
                "[flag_base + offset] - the same primitive a %s or %n$x format "
                "bug provides in a real C binary.",
            ),
            _step(
                "intuition",
                "If the program uses your bytes as an address or index, you pick "
                "what it reads. The flag lives at a known address; choose the "
                "offset that lands on the byte you want.",
            ),
            _step(
                "analogy",
                "A librarian who fetches the book on shelf 'n' when you shout a "
                "number. Shout 12 and you get shelf 12 - even if you were only "
                "ever meant to choose from the first three shelves.",
            ),
            _step(
                "visualization",
                "flag base:  0x600010   \"ASM{fl4g_1s_fun_4_u}\"\n"
                "index:      f l 4 g _ 1 s _ f ...\n"
                "            0 1 2 3 4 5 6 7 8\n"
                "flag[12] = 'f' = 0x66\n"
                "input byte 0x0c -> read [0x600010 + 0x0c] -> leak 0x66",
            ),
            _step(
                "example",
                "The vuln reads one offset byte, then leaks the flag byte at "
                "[base + offset] into R8. With no input the offset is 0 and it "
                "leaks flag[0].",
                high_level="char o; read(0, &o, 1); leak(flag_base + o);",
                program=read_asm("module9/lesson2_format_leak/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: the SYS_READ takes one byte into the scratch cell, MOVZX "
                "loads the offset into R8, and the indexed load leaks "
                "[0x600000 + r8]. Run with no input and R8 ends up holding "
                "flag[0].",
                program=read_asm("module9/lesson2_format_leak/example.asm"),
            ),
            _step(
                "prediction",
                "The flag starts at 0x600010 and flag[12] is 'f' (0x66). What "
                "single input byte selects flag[12]?",
                program=read_asm("module9/lesson2_format_leak/example.asm"),
                options=["0x0c", "0x66", "0x00", "0x0f"],
                answer=0,
                feedback={
                    1: "0x66 is the VALUE leaked ('f'), not the offset.",
                    2: "0x00 would leak flag[0].",
                    3: "0x0f would land 15 bytes past flag[0] within the flag.",
                },
                hint="offset = index of the byte you want = 12 = 0x0c.",
            ),
            _step(
                "response",
                "Type the hex offset byte (with 0x) that makes the vuln leak "
                "flag[12] = 0x66 into R8.",
                program=read_asm("module9/lesson2_format_leak/example.asm"),
                keywords=["0x0c"],
                model_answer="0x0c - flag[12] sits 12 bytes after the flag base, "
                    "so offset 0x0c selects it and the leak returns 0x66.",
                hint="The index of 'f' in the flag is 12.",
            ),
            _step(
                "feedback",
                "Offset 0x0c leaks flag[12] = 0x66. One controlled index buys one "
                "arbitrary byte; looping it over the whole range would dump the "
                "entire flag. That is exactly why format strings are dangerous: "
                "%s reads whatever pointer sits where the attacker's format "
                "string wants one.",
            ),
            _step(
                "challenge",
                "Choose the offset byte that leaks flag[12]. Feed b'\\x0c' as the "
                "step's input and leave the leaked value 0x66 in R8.",
                program=read_asm("module9/lesson2_format_leak/challenge.asm"),
                expected={"input": b"\x0c", "registers": {"r8": 0x66}},
            ),
            _step(
                "reflection",
                "How would you locate the flag's address in a real binary - what "
                "two tools (one static, one dynamic) would you reach for?",
            ),
        ],
    )


def lesson_heap_overflow() -> Lesson:
    return Lesson(
        id="module9.lesson3",
        module="module9",
        title="Heap Overflow",
        order=3,
        steps=[
            _step(
                "concept",
                "Heap overflows write past the end of one heap allocation into "
                "whatever the allocator placed next to it. Here a 4-byte "
                "input_data buffer is filled by an unbounded read, and safe_var - "
                "a 4-byte flag initialized to 'bico' - sits directly after it at "
                "0x700004. Eight bytes of input spill into safe_var and replace "
                "its value.",
            ),
            _step(
                "intuition",
                "Adjacent heap objects are adjacent in memory. Exceeding an "
                "allocation is only a 'few bytes' for the attacker but a complete "
                "state rewrite for the neighboring object - here, a security "
                "flag.",
            ),
            _step(
                "analogy",
                "A row of mailboxes where each envelope must fit its box. Stuff "
                "a box too full and the paper spills into the neighbor's box - "
                "and the neighbor reads what you wrote, not what they expected.",
            ),
            _step(
                "visualization",
                "heap layout:\n"
                "  0x700000  input_data[0..3]   4 bytes\n"
                "  0x700004  safe_var[0..3]     init 'bico'\n"
                "input 'picopico' (8 bytes) written from 0x700000:\n"
                "  0x700000 'p' 'i' 'c' 'o'   <- fills input_data\n"
                "  0x700004 'p' 'i' 'c' 'o'   <- OVERFLOWED into safe_var\n"
                "safe_var now reads 'pico': first byte 'p' = 0x70",
            ),
            _step(
                "example",
                "The unbounded read pours stdin into the 4-byte buffer at "
                "0x700000. With no input, safe_var keeps its initialized value "
                "'bico' and R8 reads its first byte 0x62.",
                high_level="read(0, input_data /* 4 bytes */, 128);",
                program=read_asm("module9/lesson3_heap_overflow/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: the four MOVs seed safe_var ('bico'), SYS_READ targets "
                "0x700000 with size 128, and the final MOVZX copies safe_var's "
                "first byte into R8. Run with no input: R8 = 0x62 ('b'), the "
                "untouched value.",
                program=read_asm("module9/lesson3_heap_overflow/example.asm"),
            ),
            _step(
                "prediction",
                "safe_var sits at 0x700004 initialized to 'bico'. The input "
                "'picopico' (8 bytes) is written from 0x700000. After the "
                "overflow, what is safe_var's FIRST byte?",
                program=read_asm("module9/lesson3_heap_overflow/example.asm"),
                options=["'p'", "'b'", "'o'", "'i'"],
                answer=0,
                feedback={
                    1: "'b' is the ORIGINAL safe_var byte before the overflow.",
                    2: "'o' is the fourth input byte, at index 3.",
                    3: "'i' is the second input byte, at index 1.",
                },
                hint="Input bytes 0..3 fill input_data; bytes 4..7 land in safe_var.",
            ),
            _step(
                "response",
                "Type the hex value (with 0x) of safe_var's first byte after the "
                "overflow overwrites it with the first byte of the overflowing "
                "input.",
                program=read_asm("module9/lesson3_heap_overflow/example.asm"),
                keywords=["0x70"],
                model_answer="0x70 - the input 'picopico' fills input_data with "
                    "'pico' and overflows 'pico' into safe_var, whose first byte "
                    "becomes 'p' = 0x70.",
                hint="'p' is ASCII 0x70.",
            ),
            _step(
                "feedback",
                "R8 = 0x70. The four bytes of input at indexes 4..7 replaced "
                "safe_var entirely. In a real allocator the overflow would first "
                "corrupt the chunk header (size, flags) before touching the next "
                "object - which is exactly why heap exploitation usually starts "
                "by corrupting metadata, not just the payload of the next chunk.",
            ),
            _step(
                "challenge",
                "Overflow the 4-byte input_data buffer so the 8-byte input "
                "'picopico' rewrites safe_var and its first byte becomes 0x70. "
                "Feed b'picopico' as the step's input and leave 0x70 in R8.",
                program=read_asm("module9/lesson3_heap_overflow/challenge.asm"),
                expected={"input": b"picopico", "registers": {"r8": 0x70}},
            ),
            _step(
                "reflection",
                "Real heap chunks store size and 'previous-in-use' metadata "
                "around the user data. Why does corrupting that metadata give an "
                "attacker more power than simply rewriting the neighbor's bytes?",
            ),
        ],
    )


def lesson_pie_leak() -> Lesson:
    return Lesson(
        id="module9.lesson4",
        module="module9",
        title="PIE Base Leak",
        order=4,
        steps=[
            _step(
                "concept",
                "Position-Independent Executables (PIE) load at a random base "
                "address on every run (ASLR), so hardcoded absolute addresses "
                "inside the binary are useless. But offsets inside the binary are "
                "stable. If any bug leaks a single runtime pointer into the "
                "binary, the attacker subtracts the known offset to recover the "
                "base, then re-derives every other address as base + offset.",
            ),
            _step(
                "intuition",
                "base is the only unknown. pointer - offset = base, and base + "
                "any other offset = any other address. One leaked pointer makes "
                "the whole binary predictable.",
            ),
            _step(
                "analogy",
                "A hotel where every floor's rooms are numbered from the lobby. "
                "If a leak tells you room 128 is at the 0x80 mark, you can work "
                "out where the lobby is - and from there, the door number of "
                "every other room in the building.",
            ),
            _step(
                "visualization",
                "text segment (loads at random base B):\n"
                "  B + 0x00  vuln()\n"
                "  B + 0x80  win()          <- offset is fixed\n"
                "leaked pointer = 0x400080  (base happened to be 0x400000)\n"
                "base  = 0x400080 - 0x80    = 0x400000\n"
                "win() = base + 0x80        = 0x400080",
            ),
            _step(
                "example",
                "vuln() leaks win()'s runtime address into R8: it loads the fixed "
                "offset (0x80) and adds the text base 0x400000, so R8 ends up "
                "0x400080 - the pointer an ASLR leak would reveal.",
                high_level="printf(\"%p\", win); // base + 0x80",
                program=read_asm("module9/lesson4_pie_leak/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: MOV R8, win loads the label's offset (0x80) because "
                "relative code can only carry offsets, then ADD R8, 0x400000 "
                "adds the base. Run: R8 = 0x400080, exactly the runtime address "
                "of win().",
                program=read_asm("module9/lesson4_pie_leak/example.asm"),
            ),
            _step(
                "prediction",
                "win() lives at offset 0x80 from the text base. The binary "
                "happened to load at 0x400000. What pointer value does the leak "
                "reveal?",
                program=read_asm("module9/lesson4_pie_leak/example.asm"),
                options=["0x400080", "0x80", "0x400000", "0x40007f"],
                answer=0,
                feedback={
                    1: "0x80 is just the offset; the leak is base + offset.",
                    2: "0x400000 is the base itself, not the leaked pointer.",
                    3: "0x40007f is one byte short of win().",
                },
                hint="base + offset = 0x400000 + 0x80.",
            ),
            _step(
                "response",
                "Type the hex runtime address (with 0x) that the PIE leak "
                "reveals for win() when the text base is 0x400000 and win() is "
                "at offset 0x80.",
                program=read_asm("module9/lesson4_pie_leak/example.asm"),
                keywords=["0x400080"],
                model_answer="0x400080 - base 0x400000 plus the fixed offset 0x80 "
                    "of win(); subtracting the offset from the leak recovers the "
                    "base.",
                hint="0x400000 + 0x80.",
            ),
            _step(
                "feedback",
                "R8 = 0x400080. The same arithmetic works against a real PIE: "
                "subtract win()'s known offset from the leaked pointer to get "
                "base, then rebuild the address of every gadget you need. ASLR "
                "only helps while no pointer leaks.",
            ),
            _step(
                "challenge",
                "Recover win()'s runtime address from the leak. The vuln computes "
                "it as offset 0x80 plus the text base 0x400000; leave the "
                "revealed pointer 0x400080 in R8.",
                program=read_asm("module9/lesson4_pie_leak/challenge.asm"),
                expected={"registers": {"r8": 0x400080}},
            ),
            _step(
                "reflection",
                "Why does ASLR randomize only the base and not the offsets, and "
                "why is a single leaked pointer enough to bypass it entirely?",
            ),
        ],
    )


def lesson_tcache_poisoning() -> Lesson:
    return Lesson(
        id="module9.lesson5",
        module="module9",
        title="TCache Freelist Poisoning",
        order=5,
        steps=[
            _step(
                "concept",
                "glibc's tcache keeps a singly-linked freelist of freed chunks; "
                "the first qword of each freed chunk stores the 'next' pointer. "
                "If a use-after-free or overflow lets the attacker rewrite that "
                "qword, the next malloc() returns the poisoned value instead of "
                "a real chunk - the attacker can make malloc hand back memory "
                "anywhere writable, including inside another object.",
            ),
            _step(
                "intuition",
                "malloc() trusts the pointer stored in the freed chunk. A freed "
                "chunk is just data the allocator believes; rewrite that data "
                "and the allocator walks to wherever you pointed it.",
            ),
            _step(
                "analogy",
                "A coat-check that trusts the tag on a coat rather than its own "
                "log. Forge a tag that names a different peg, and the next "
                "person who 'allocates a coat' is handed the peg you chose.",
            ),
            _step(
                "visualization",
                "freed chunk at 0x700000:\n"
                "  +0  next pointer = 0x701000  (real freelist head)\n"
                "  +8  ...\n"
                "attacker overwrites +0 with 0x700080 (poison):\n"
                "  +0  next pointer = 0x700080\n"
                "next malloc() reads [0x700000] -> returns 0x700080",
            ),
            _step(
                "example",
                "The vuln 'frees' a chunk at 0x700000 whose first qword is the "
                "freelist head, then the attacker overwrites that qword with "
                "0x700080. The simulated malloc reads the poisoned next pointer "
                "into R8.",
                high_level="free(c); *(void**)c = 0x700080; p = malloc();",
                program=read_asm("module9/lesson5_tcache_poisoning/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: MOV QWORD [0x700000], 0x701000 plants the original head, "
                "the second MOV overwrites it with the poison 0x700080, and the "
                "final load reads the poisoned next into R8 = 0x700080.",
                program=read_asm("module9/lesson5_tcache_poisoning/example.asm"),
            ),
            _step(
                "prediction",
                "The freed chunk's next pointer starts as 0x701000 (the real "
                "head). What qword must the attacker write to make the next "
                "malloc return 0x700080?",
                program=read_asm("module9/lesson5_tcache_poisoning/example.asm"),
                options=["0x700080", "0x701000", "0x700000", "0x700004"],
                answer=0,
                feedback={
                    1: "0x701000 is the ORIGINAL head; overwriting with it changes "
                        "nothing.",
                    2: "0x700000 is the freed chunk's own address, not the target.",
                    3: "0x700004 is 4 bytes into the chunk - the size field in a "
                        "real header.",
                },
                hint="malloc returns whatever qword now sits at [0x700000].",
            ),
            _step(
                "response",
                "Type the hex poison value (with 0x) that overwrites the freed "
                "chunk's next pointer so the next malloc returns 0x700080.",
                program=read_asm("module9/lesson5_tcache_poisoning/example.asm"),
                keywords=["0x700080"],
                model_answer="0x700080 - writing it into [0x700000] makes the "
                    "freelist walk return that address on the next malloc.",
                hint="Poison = the address you want malloc to return.",
            ),
            _step(
                "feedback",
                "R8 = 0x700080. With the freelist poisoned, malloc hands out an "
                "attacker-chosen address. Modern glibc applies 'safe-linking' "
                "(the stored next is XORed with the chunk address >> 12) so the "
                "attacker must know a heap address to forge a valid pointer - "
                "and that is exactly why heap leaks and tcache poisoning are "
                "usually paired.",
            ),
            _step(
                "challenge",
                "Poison the freed chunk's next pointer at 0x700000 so the next "
                "malloc returns 0x700080; leave that target address in R8.",
                program=read_asm("module9/lesson5_tcache_poisoning/challenge.asm"),
                expected={"registers": {"r8": 0x700080}},
            ),
            _step(
                "reflection",
                "How would writing to the chunk's SIZE field (offset +8) instead "
                "of its next pointer change what the allocator does with the "
                "chunk?",
            ),
        ],
    )


def module9() -> Module:
    return Module(
        id="module9",
        title="Exploit Lab",
        order=9,
        lessons=[
            lesson_ret2win(),
            lesson_format_leak(),
            lesson_heap_overflow(),
            lesson_pie_leak(),
            lesson_tcache_poisoning(),
        ],
    )
