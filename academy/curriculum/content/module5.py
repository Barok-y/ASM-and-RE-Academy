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
                "Press R to run the example: RAX walks 0xAB -> 0xA0 (AND mask) -> 0xA5 "
                "(OR mask) -> 0xAA (XOR toggle). Read the final panel — what value ends up "
                "in R8?",
                program=read_asm("module5/lesson1_bitwise/example.asm"),
                options=["0xAA", "0xA0", "0xA5", "0xAB"],
                answer=0,
                feedback={
                    1: "0xA0 is the intermediate AND result, before the OR and XOR.",
                    2: "0xA5 is the result after the OR, before the final XOR.",
                    3: "0xAB is the starting value, before any mask.",
                },
                hint="Press R — the final XOR toggles the low nibble to 0xAA.",
            ),
            _step(
                "response",
                "Run the challenge (press R): clear bit 2 (0x04) from 0xFF with AND, then "
                "toggle bit 0 (0x01) with XOR. Type the hex value (with 0x) that ends up "
                "in RBX.",
                program=read_asm("module5/lesson1_bitwise/challenge.asm"),
                keywords=["0xfa", "fa", "250"],
                model_answer="0xFA — 0xFF & 0xFB = 0xFB clears bit 2; 0xFB ^ 0x01 = 0xFA "
                    "toggles bit 0 (that is 250 decimal).",
                hint="After R, RBX shows 0xFA.",
            ),
            _step(
                "feedback",
                "RBX = 0xFA. AND with a 0 in bit 2's position forced that bit to 0 "
                "(0xFF -> 0xFB), and XOR toggled bit 0 (0xFB -> 0xFA). Masks clear, set, "
                "and flip individual bits this way.",
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
                "Press R to run the example: 3 is shifted left by 3 (multiply by 8), then "
                "right by 2 (divide by 4). Read the final panel — what value ends up in "
                "R8?",
                program=read_asm("module5/lesson2_shifts/example.asm"),
                options=["6", "8", "24", "3"],
                answer=0,
                feedback={
                    1: "8 is the result of the left shift alone (3*8).",
                    2: "24 is the value before the right shift divides it by 4.",
                    3: "3 is the starting value; the shifts always change it.",
                },
                hint="Press R — 3*8 = 24, then 24/4 = 6.",
            ),
            _step(
                "response",
                "Run the challenge (press R): it multiplies 7 by 10 without MUL, using "
                "(7<<3)+(7<<1). Type the total that ends up in RBX.",
                program=read_asm("module5/lesson2_shifts/challenge.asm"),
                keywords=["70"],
                model_answer="70 — SHL 7 by 3 gives 56 (x8), SHL by 1 gives 14 (x2), and "
                    "56+14 = 70; shift-and-add reproduces the multiplication.",
                hint="After R, RBX shows the shift-and-add total.",
            ),
            _step(
                "feedback",
                "RBX = 70. A left shift scales by a power of two (x8 and x2 here), and "
                "adding the two shifted copies multiplied by 10. Shifts buy cheap "
                "multiplication by constants — the technique compiled code uses.",
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
                "Press R to run the challenge: RAX = 1 (write), RDI = 1 (stdout), RSI = "
                "buffer, RDX = 3, and the buffer holds 'A', 'B', newline. Read the status "
                "line and OUTPUT — what did the program print?",
                program=read_asm("module5/lesson3_syscalls/challenge.asm"),
                options=["AB", "Hi", "BA", "nothing at all"],
                answer=0,
                feedback={
                    1: "'Hi' is the example's buffer, not this program's.",
                    2: "The bytes are sent in order — A then B, not reversed.",
                    3: "The write syscall (fd 1) captured three bytes of output.",
                },
                hint="Press R — the output panel shows the three bytes the program wrote.",
            ),
            _step(
                "response",
                "Run the example (press R) and read the output. The buffer bytes are 72, "
                "105, 10 — three characters sent to stdout. Type the two letters the "
                "program printed (the newline is not a letter).",
                program=read_asm("module5/lesson3_syscalls/example.asm"),
                keywords=["hi"],
                model_answer="Hi — byte 72 is 'H', byte 105 is 'i', byte 10 is the "
                    "newline; the write syscall captured exactly those three bytes.",
                hint="After R, the STATE panel shows the captured output.",
            ),
            _step(
                "feedback",
                "Output 'Hi': the write syscall used RAX = 1, RDI = 1 (stdout), RSI = "
                "buffer, RDX = 3, and the emulator appended the three bytes to its output "
                "buffer. System calls turn register setups into real I/O.",
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
                "Press R to run the example: the loop reads the null-terminated string "
                "'ABC' at 0x600000 and counts non-null bytes. Read the final panel — what "
                "length ends up in R8 (and RCX)?",
                program=read_asm("module5/lesson4_strings_arrays/example.asm"),
                options=["3", "4", "5", "0"],
                answer=0,
                feedback={
                    1: "4 bytes are WRITTEN, but the null terminator is not counted.",
                    2: "Only three characters exist before the terminator.",
                    3: "The loop stops at the first zero byte; it counts 3.",
                },
                hint="Press R — R8 shows the length, excluding the terminator.",
            ),
            _step(
                "response",
                "Run the challenge (press R): the program writes the string 'GO' plus its "
                "terminator, then counts the non-null bytes. Type the length that ends up "
                "in RBX.",
                program=read_asm("module5/lesson4_strings_arrays/challenge.asm"),
                keywords=["2"],
                model_answer="2 — the loop read 'G', then 'O', then hit the null byte and "
                    "stopped, so the length counts only the two letters.",
                hint="After R, RBX shows the number of characters before the zero.",
            ),
            _step(
                "feedback",
                "RBX = 2. Walking bytes until the null terminator (0x00) is the string "
                "loop: test each byte, advance the pointer, stop at zero. The length "
                "excludes the terminator that marks the end.",
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
                "Press R to run the challenge: element-wise add [1,2,3,4] + [4,3,2,1] "
                "gives [5,5,5,5]. Read the final panel — what sum (5+5+5+5) ends up in "
                "RBX?",
                program=read_asm("module5/lesson5_simd/challenge.asm"),
                options=["20", "14", "10", "5"],
                answer=0,
                feedback={
                    1: "14 is a partial total, not the sum of all four lanes.",
                    2: "10 is half the work; the four results are all added in.",
                    3: "5 is one lane's result, not the accumulated total.",
                },
                hint="Press R — RBX accumulates the four lane sums.",
            ),
            _step(
                "response",
                "Run the example (press R): the scalar loop processes four byte-pairs one "
                "at a time and RCX counts the iterations. Type the iteration count that "
                "ends up in RCX.",
                program=read_asm("module5/lesson5_simd/example.asm"),
                keywords=["4"],
                model_answer="4 — RCX counted 0 -> 1 -> 2 -> 3 and stopped when it reached "
                    "4; four scalar additions where one paddb would have done it in a "
                    "single instruction.",
                hint="After R, RCX shows the number of loop iterations.",
            ),
            _step(
                "feedback",
                "RCX = 4 — the scalar loop took four iterations to add four byte-pairs. "
                "That is exactly the work one SIMD paddb performs in a single "
                "instruction, which is where the speedup comes from.",
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
