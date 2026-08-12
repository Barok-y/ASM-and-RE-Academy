from __future__ import annotations

from ..models import Lesson, LessonStep, Module
from ._asm import read_asm


def _step(kind: str, content: str = "", **kwargs) -> LessonStep:
    return LessonStep(kind=kind, content=content, **kwargs)


def lesson_bitwise() -> Lesson:
    return Lesson(
        id="module5.lesson1",
        module="module5",
        title="Bitwise Operations",
        order=1,
        steps=[
            _step(
                "concept",
                "AND, OR, XOR, and NOT operate bit by bit. AND is used to clear "
                "bits (masking), OR to set bits, XOR to toggle bits, and NOT to "
                "flip everything. They are the building blocks of flags, masks, "
                "and every low-level data structure.",
            ),
            _step(
                "intuition",
                "Each bit is an independent on/off switch. AND keeps a switch "
                "only if the mask also has it on; OR turns it on; XOR flips it.",
            ),
            _step(
                "analogy",
                "A light panel with 64 switches. AND holds down only the switches "
                "that are on in both patterns, OR turns on any that is on in "
                "either, XOR flips any that is on in exactly one.",
            ),
            _step(
                "visualization",
                "0xAB & 0xF0 = 0xA0     (keep high nibble)\n"
                "0xA0 | 0x05 = 0xA5     (set low nibble)\n"
                "0xA5 ^ 0x0F = 0xAA     (toggle low nibble)\n"
                "~0x00       = 0xFF...  (invert all bits)",
            ),
            _step(
                "example",
                "Clear, set, and toggle bits with masks.",
                high_level="x &= 0xF0; x |= 0x05; x ^= 0x0F;",
                program=read_asm("module5/lesson1_bitwise/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step and watch RAX: 0xAB -> 0xA0 (AND mask) -> 0xA5 (OR mask) "
                "-> 0xAA (XOR toggle).",
                program=read_asm("module5/lesson1_bitwise/example.asm"),
            ),
            _step(
                "prediction",
                "What does 'xor rax, rax' do?",
                options=["zeroes RAX", "sets RAX to -1", "flips all bits once", "no-op"],
                answer=0,
                feedback={
                    1: "NOT would make -1; XOR of a value with itself is always 0.",
                    2: "XOR toggles twice per bit, returning to the original - 0.",
                    3: "It changes every bit, and it is the fastest way to zero.",
                },
            ),
            _step(
                "response",
                "Which operation clears a selected bit?",
                answer=1,
                options=["OR", "AND with a mask that has a 0 there"],
            ),
            _step(
                "feedback",
                "AND with a 0 in that position forces the bit to 0.",
            ),
            _step(
                "challenge",
                "Clear bit 2 (0x04) from 0xFF with AND, then toggle bit 0 "
                "(0x01) with XOR. Leave the result in RBX.",
                program=read_asm("module5/lesson1_bitwise/challenge.asm"),
                expected={"registers": {"rbx": 0xFA}},
            ),
            _step(
                "reflection",
                "XOR with itself zeroes a register faster than MOV. What other "
                "tricks does XOR enable?",
            ),
        ],
    )


def lesson_shifts() -> Lesson:
    return Lesson(
        id="module5.lesson2",
        module="module5",
        title="Shifts and Bit Tricks",
        order=2,
        steps=[
            _step(
                "concept",
                "SHL shifts bits left, filling with zeros (multiply by 2^N); SHR "
                "shifts right, filling with zeros (unsigned divide by 2^N); SAR "
                "shifts right, preserving the sign bit (signed divide). Shifts "
                "often replace multiply/divide by powers of two and combine into "
                "faster arithmetic.",
            ),
            _step(
                "intuition",
                "Shifting is like sliding digits on an abacus: one position left "
                "multiplies by the base (2 for binary), one position right "
                "divides. SAR keeps the sign so negative numbers survive.",
            ),
            _step(
                "analogy",
                "Decimal 45 shifted left one place becomes 450 (x10); binary 45 "
                "shifted left one place becomes 90 (x2). SAR is the signed "
                "variant that drags the minus sign along.",
            ),
            _step(
                "visualization",
                "rax = 3\n"
                "shl rax, 3  ->  3 * 8 = 24\n"
                "shr rax, 2  ->  24 / 4 = 6\n"
                "sar rax, 1  ->  signed: -6 / 2 = -3",
            ),
            _step(
                "example",
                "Multiply by 8 and divide by 4 using shifts.",
                high_level="x = x * 8; x = x / 4;",
                program=read_asm("module5/lesson2_shifts/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: SHL moves the 3 left three places (24), then SHR moves it "
                "right two places (6).",
                program=read_asm("module5/lesson2_shifts/example.asm"),
            ),
            _step(
                "prediction",
                "What is 'shl rax, 4' equivalent to?",
                options=["rax * 16", "rax / 16", "rax + 4", "rax & 0xF"],
                answer=0,
                feedback={
                    1: "Shifting right divides; shifting left multiplies.",
                    2: "SHL does not add; it scales by a power of two.",
                    3: "That would mask the low nibble, not scale.",
                },
            ),
            _step(
                "response",
                "Which shift keeps the sign bit for signed values?",
                answer=1,
                options=["SHR", "SAR"],
            ),
            _step(
                "feedback",
                "SAR (shift arithmetic right) copies the sign bit; SHR zero-fills.",
            ),
            _step(
                "challenge",
                "Multiply 7 by 10 without MUL, using only shifts and an add: "
                "(7<<3) + (7<<1). Leave the result in RBX.",
                program=read_asm("module5/lesson2_shifts/challenge.asm"),
                expected={"registers": {"rbx": 70}},
            ),
            _step(
                "reflection",
                "Compilers emit shifts for multiply-by-constant. Why might a "
                "hardware multiplier still be faster for large arbitrary "
                "multiplications?",
            ),
        ],
    )


def lesson_syscalls() -> Lesson:
    return Lesson(
        id="module5.lesson3",
        module="module5",
        title="Syscalls",
        order=3,
        steps=[
            _step(
                "concept",
                "A syscall is how user code asks the kernel for service: number "
                "in RAX, arguments in RDI/RSI/RDX/R10/R8/R9, followed by "
                "'syscall'. The kernel switches to privileged mode, does the "
                "work, and returns. write (1) sends bytes to a file descriptor; "
                "exit (60) terminates the process.",
            ),
            _step(
                "intuition",
                "The CPU runs in a sandbox; any real work (printing, files, "
                "network) is done by the kernel, and syscall is the one door "
                "out of the sandbox.",
            ),
            _step(
                "analogy",
                "A customer at a bank window: RAX is the form number (withdraw, "
                "deposit), RDI-RDX are the filled-in fields, and the teller "
                "(kernel) is the only one allowed inside the vault.",
            ),
            _step(
                "visualization",
                "write:  rax=1 rdi=fd rsi=buffer rdx=count -> syscall\n"
                "exit:   rax=60 rdi=status -> syscall\n"
                "on x86-64 the syscall number goes in rax (System V).",
            ),
            _step(
                "example",
                "Write three bytes ('H', 'i', newline) to stdout.",
                high_level='write(1, "Hi\\n", 3);',
                program=read_asm("module5/lesson3_syscalls/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: build the bytes in the data segment, load fd=1, buffer, "
                "and length, then SYSCALL - the emulator appends the bytes to "
                "its output buffer.",
                program=read_asm("module5/lesson3_syscalls/example.asm"),
            ),
            _step(
                "prediction",
                "Which register carries the syscall number on x86-64?",
                options=["RAX", "RDI", "RSI", "RSP"],
                answer=0,
                feedback={
                    1: "RDI is the first argument, e.g. the file descriptor.",
                    2: "RSI is the second argument, e.g. the buffer pointer.",
                    3: "RSP is the stack pointer, never a syscall number.",
                },
            ),
            _step(
                "response",
                "What does the exit syscall use for the process status code?",
                answer=1,
                options=["RSI", "RDI"],
            ),
            _step(
                "feedback",
                "Exit puts the status in RDI (the first argument slot).",
            ),
            _step(
                "challenge",
                "Write the bytes 'A', 'B', newline to stdout.",
                program=read_asm("module5/lesson3_syscalls/challenge.asm"),
                expected={"output": "AB\n"},
            ),
            _step(
                "reflection",
                "Why must a process go through the kernel instead of printing "
                "directly to hardware?",
            ),
        ],
    )


def lesson_strings_arrays() -> Lesson:
    return Lesson(
        id="module5.lesson4",
        module="module5",
        title="Strings and Arrays",
        order=4,
        steps=[
            _step(
                "concept",
                "Strings are arrays of bytes ending in a null terminator (0). "
                "Arrays are contiguous memory blocks addressed by "
                "[base + index * element_size]. Walking them is a loop that "
                "moves a pointer and tests the byte at each position.",
            ),
            _step(
                "intuition",
                "There is no 'string' in assembly - just a start address and the "
                "promise that a zero byte marks the end. Everything else is "
                "pointer arithmetic.",
            ),
            _step(
                "analogy",
                "A train with cars (bytes) and a caboose: the terminator. You "
                "walk car to car until you reach the caboose to learn the "
                "train's length.",
            ),
            _step(
                "visualization",
                "address  0x600000  0x600001  0x600002  0x600003\n"
                "byte     65 ('A')   66 ('B')   67 ('C')   0\n"
                "length loop:  movzx -> test -> je done -> inc ptr -> jump back\n"
                "rcx counts 3 non-zero bytes.",
            ),
            _step(
                "example",
                "Build 'ABC' in memory and count its length.",
                high_level='char s[] = "ABC"; int len = strlen(s);',
                program=read_asm("module5/lesson4_strings_arrays/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: each MOVZX loads one byte, TEST sees whether it is zero, "
                "and the loop counts and advances until the null byte stops it.",
                program=read_asm("module5/lesson4_strings_arrays/example.asm"),
            ),
            _step(
                "prediction",
                "A string occupies bytes 0x600000..0x600003, ending with a null "
                "byte. How many bytes does the string data use?",
                options=["3", "4", "0", "unlimited"],
                answer=0,
                feedback={
                    1: "4 bytes are WRITTEN, but the string content is 3 chars.",
                    3: "The null terminator is required; it cannot be omitted.",
                },
            ),
            _step(
                "response",
                "What byte marks the end of a C string?",
                answer=1,
                options=["newline (10)", "null (0)"],
            ),
            _step(
                "feedback",
                "The null terminator (0x00) marks the end.",
            ),
            _step(
                "challenge",
                "Write the null-terminated string 'GO' to memory and count its "
                "length (not counting the terminator) into RBX.",
                program=read_asm("module5/lesson4_strings_arrays/challenge.asm"),
                expected={"registers": {"rbx": 2}},
            ),
            _step(
                "reflection",
                "What happens if code reads past a missing terminator? How do "
                "buffer overflows begin with exactly this pattern?",
            ),
        ],
    )


def lesson_simd() -> Lesson:
    return Lesson(
        id="module5.lesson5",
        module="module5",
        title="SIMD Overview",
        order=5,
        steps=[
            _step(
                "concept",
                "SIMD (Single Instruction, Multiple Data) operates on vectors "
                "instead of scalars. xmm0-xmm15 hold 16 bytes each, and one "
                "instruction like paddb adds 16 bytes at once. Code that "
                "processes audio, video, or arrays is often 'vectorized' this "
                "way for large speedups.",
            ),
            _step(
                "intuition",
                "A scalar loop processes one array element per iteration; SIMD "
                "processes a whole row per iteration. Same result, far fewer "
                "round trips through the fetch/decode loop.",
            ),
            _step(
                "analogy",
                "Scalar work is paying each item at a single checkout line; SIMD "
                "is a highway with 16 lanes all processing items at once.",
            ),
            _step(
                "visualization",
                "xmm0 = [02][04][06][08][00][00]...\n"
                "xmm1 = [01][01][01][01][00][00]...\n"
                "paddb xmm0, xmm1\n"
                "xmm0 = [03][05][07][09][00][00]...   (one instruction, 4 adds)\n"
                "the scalar loop below does the same four adds one at a time.",
            ),
            _step(
                "example",
                "A scalar loop that simulates what a vectorized add would do in "
                "one instruction.",
                high_level="for (i=0;i<4;i++) out[i] = a[i] + b[i];",
                program=read_asm("module5/lesson5_simd/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step the loop and watch the element-wise adds accumulate; note "
                "how many instructions the 'SIMD-style' work takes when done "
                "scalarly.",
                program=read_asm("module5/lesson5_simd/example.asm"),
            ),
            _step(
                "prediction",
                "With SIMD, how many bytes can paddb add in a single xmm0 "
                "instruction?",
                options=["16", "1", "4", "64"],
                answer=0,
                feedback={
                    1: "That is scalar work, one byte at a time.",
                    2: "xmm registers are 128 bits = 16 bytes.",
                    3: "64 bytes would need ymm (AVX) or zmm (AVX-512).",
                },
            ),
            _step(
                "response",
                "Do xmm registers hold one scalar value or a vector of values?",
                answer=1,
                options=["one scalar value", "a vector of values"],
            ),
            _step(
                "feedback",
                "xmm registers are 128-bit vectors of packed values.",
            ),
            _step(
                "challenge",
                "Element-wise add [1,2,3,4] and [4,3,2,1] - the vectorized "
                "result is [5,5,5,5]. Leave the sum (20) in RBX.",
                program=read_asm("module5/lesson5_simd/challenge.asm"),
                expected={"registers": {"rbx": 20}},
            ),
            _step(
                "reflection",
                "Vectorization gives speed, but SIMD adds complexity. When is the "
                "scalar loop the better engineering choice despite being slower?",
            ),
        ],
    )


def module5() -> Module:
    return Module(
        id="module5",
        title="Advanced Assembly",
        order=5,
        lessons=[
            lesson_bitwise(),
            lesson_shifts(),
            lesson_syscalls(),
            lesson_strings_arrays(),
            lesson_simd(),
        ],
    )
