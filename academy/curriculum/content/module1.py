from __future__ import annotations

from ..models import Lesson, LessonStep, Module


def _step(kind: str, content: str = "", **kwargs) -> LessonStep:
    return LessonStep(kind=kind, content=content, **kwargs)


def lesson_fde() -> Lesson:
    return Lesson(
        id="module1.lesson1",
        module="module1",
        title="Fetch-Decode-Execute and the CPU",
        order=1,
        steps=[
            _step(
                "concept",
                "The CPU runs every instruction through the same three-stage loop.\n\n"
                "FETCH — the CPU reads the next instruction's bytes from memory, using the "
                "instruction pointer (RIP) to know where to read.\n"
                "DECODE — a decoder translates those raw bytes into an internal operation, "
                "such as 'copy the value 5 into the RAX register'.\n"
                "EXECUTE — the CPU carries that operation out, updating registers, memory, "
                "or flags.\n\n"
                "RIP then advances and the loop repeats. A whole program is just millions of "
                "these three steps run one after another.",
                program="mov rax, 1",
                options=[
                    "fetch -> decode -> execute",
                    "compile -> link -> run",
                    "read -> decode -> store",
                    "execute -> fetch -> decode",
                ],
                answer=0,
                feedback={
                    1: "Compiling and linking happen before the program runs, outside the CPU.",
                    2: "The loop always begins with fetch (reading from memory), "
                       "not a generic read.",
                    3: "Execution always comes last; you cannot execute before you decode.",
                },
                hint="The first stage reads the next instruction from memory using RIP.",
            ),
            _step(
                "intuition",
                "A recipe is only a list of words until you cook it, one step at a time. "
                "The CPU has no idea of the 'big picture' — it can hold only one tiny step in "
                "its head at any moment and it never skips ahead.\n\n"
                "This is why a single wrong instruction changes everything that follows: "
                "the CPU blindly obeys whatever byte is next. Small assembly mistakes rarely "
                "error immediately — they silently corrupt state that is read much later.",
            ),
            _step(
                "analogy",
                "Picture a chef at a service window with a stack of cards. She picks the next "
                "card off the pile (fetch), reads what verb it names — 'chop', 'stir', 'bake' "
                "(decode) — and then performs exactly that action (execute). Only when the "
                "action is finished does she take the next card. She never peeks two cards "
                "ahead, and she never skips a card.",
            ),
            _step(
                "visualization",
                "RIP -> [fetch] -> [decode] -> [execute]\n"
                "                 ^                    |\n"
                "                 +--------------------+\n\n"
                "RIP always points at the card currently being read. After execute, RIP moves "
                "forward so the next fetch reads the following instruction.",
                program="mov rax, 2",
            ),
            _step(
                "example",
                "Take the instruction 'mov rax, 5'.\n\n"
                "FETCH: the CPU reads the instruction's encoded bytes from the address RIP "
                "points at.\n"
                "DECODE: the decoder recognizes the bytes as 'copy the immediate value 5 "
                "into RAX'.\n"
                "EXECUTE: the copy happens, and RAX becomes 5. RIP then advances past those "
                "bytes so the next fetch reads the instruction that follows.",
                high_level="long x = 5;",
                program="mov rax, 5",
            ),
            _step(
                "walkthrough",
                "Run this program and watch the STATE panel: RAX takes the value 5 and RIP "
                "advances past the instruction. That is the execute stage in action.",
                program="mov rax, 5",
            ),
            _step(
                "prediction",
                "During the fetch stage, which register tells the CPU which instruction to "
                "read next?",
                options=["RAX", "RIP", "RSP", "RBP"],
                answer=1,
                feedback={
                    0: "RAX is a general-purpose data register — it holds values, not the "
                       "location of code.",
                    2: "RSP is the stack pointer. It tracks the stack, not the current "
                       "instruction.",
                    3: "RBP is the frame pointer used to navigate stack frames; it does not "
                       "point at code.",
                },
                hint="The register's name literally starts with the word 'instruction'.",
            ),
            _step(
                "response",
                "In your own words, what happens during the decode stage?",
                answer=None,
                hint="Think about what the CPU needs to work out before it can perform an "
                     "action — the bytes alone are meaningless until translated.",
                model_answer=(
                    "During decode, the CPU's decoder translates the raw instruction bytes "
                    "into a concrete operation, such as 'copy the value 5 into RAX'."
                ),
                keywords=["decode", "translate", "instruction", "bytes"],
            ),
            _step(
                "feedback",
                "During decode, the CPU's decoder translates the raw instruction bytes into a "
                "concrete operation — for example, 'copy the number 5 into RAX'. Decode is "
                "what turns raw bytes into an action the CPU can perform.",
            ),
            _step(
                "challenge",
                "After executing 'mov rax, 5', what value does RAX hold?",
                program="mov rax, 5",
                expected={"registers": {"rax": 5}},
                hint="MOV copies its second operand (the source) into its first operand "
                     "(the destination).",
            ),
            _step(
                "reflection",
                "Why must the CPU repeat fetch-decode-execute instead of executing a whole "
                "program at once?",
                hint="The CPU's pipeline is tiny and fixed in size — it can only hold and "
                     "process one instruction at a time.",
            ),
        ],
    )


def lesson_registers() -> Lesson:
    return Lesson(
        id="module1.lesson2",
        module="module1",
        title="Registers and the RAX family",
        order=2,
        steps=[
            _step(
                "concept",
                "A register is a tiny storage cell inside the CPU — a few dozen cells that "
                "the CPU reads and writes constantly because they are hundreds of times "
                "faster than main memory.\n\n"
                "RAX is 64 bits wide, but the same physical cell can be addressed through "
                "several overlapping names:\n"
                "  RAX — all 64 bits\n"
                "  EAX — the low 32 bits\n"
                "  AX  — the low 16 bits\n"
                "  AH  — the high 8 bits of AX (bits 8-15)\n"
                "  AL  — the low 8 bits of AX (bits 0-7)",
                program="mov rax, 0x1122334455667788",
                options=[
                    "64 bits",
                    "32 bits",
                    "16 bits",
                    "8 bits",
                ],
                answer=0,
                feedback={
                    1: "32 bits is EAX — that is only the low half of RAX.",
                    2: "16 bits is AX — the low quarter of RAX.",
                    3: "8 bits is AL or AH — just the low byte of AX.",
                },
                hint="The 'R' prefix marks a 64-bit register; RAX is the full, native-width "
                     "register.",
            ),
            _step(
                "intuition",
                "One physical mailbox with many labels. You can drop a letter through the "
                "'EAX' slot and it lands inside the same box as the 'RAX' slot, but a letter "
                "through 'AL' only touches the tiny bottom drawer.\n\n"
                "Writing through a smaller name changes only that slice of the storage; the "
                "bits above it keep their old values — except EAX, which is special (see the "
                "example step).",
            ),
            _step(
                "analogy",
                "Think of RAX as a four-row parking garage, 64 spaces wide in total:\n"
                "  RAX parks in all four rows.\n"
                "  EAX parks in the bottom two rows.\n"
                "  AX parks in the two spaces at the bottom-left.\n"
                "  AL parks in one bottom-left space; AH parks in the space directly above it.\n\n"
                "Parking in a space never evicts cars from the other rows.",
            ),
            _step(
                "visualization",
                "RAX = 0x1122334455667788 (bytes, most significant first)\n\n"
                "                | 11 | 22 | 33 | 44 | 55 | 66 | 77 | 88 |\n"
                "RAX (64 bits)   +-----------------------------------------+\n"
                "EAX (low 32)                         | 55 | 66 | 77 | 88 |\n"
                "AX  (low 16)                                    | 77 | 88 |\n"
                "AH  (bits 8-15)                                | 77 |\n"
                "AL  (bits 0-7)                                       | 88 |",
                program="mov eax, 0x12345678\nmov ax, 0xABCD",
            ),
            _step(
                "example",
                "Writing to EAX clears the upper 32 bits of RAX; writing to AX, AH, or AL "
                "leaves the untouched bits exactly as they were.\n\n"
                "Start with RAX = 0x0000000012345678. 'mov eax, 0x12345678' is a no-op on "
                "the upper half. 'mov ax, 0xABCD' replaces only the low 16 bits, giving "
                "RAX = 0x000000001234ABCD.",
                high_level="x = 0x12345678;  x = (x & 0xffff0000) | 0xabcd;",
                program="mov eax, 0x12345678\nmov ax, 0xABCD",
            ),
            _step(
                "walkthrough",
                "Run and watch EAX, AX, AH, and AL each update as the sub-registers are "
                "written. Notice which bits change and which stay untouched.",
                program="mov eax, 0x12345678\nmov ax, 0xABCD\nmov ah, 0x7F",
            ),
            _step(
                "prediction",
                "RAX holds 0x0000000012345678. After 'mov ax, 0xABCD', what is RAX?",
                options=[
                    "0x000000001234ABCD",
                    "0xABCD5678",
                    "0x00000000ABCD5678",
                    "0x123456780000ABCD",
                ],
                answer=0,
                program="mov eax, 0x12345678\nmov ax, 0xABCD",
                feedback={
                    1: "The upper 32 bits are not overwritten by mov ax.",
                    2: "Only the low 16 bits change — the upper 32 bits stay exactly as they were.",
                    3: "mov ax writes the low 16 bits of AX, not the high 16.",
                },
                hint="Only the low 16 bits of RAX change; every bit above bit 15 stays the "
                     "same.",
            ),
            _step(
                "response",
                "Which of AH and AL is the more significant 8-bit half of AX?",
                answer=0,
                options=["AH", "AL"],
                feedback={
                    1: "AL is the low byte (bits 0-7); AH is the high byte.",
                },
                hint="The 'H' in AH stands for 'high'.",
            ),
            _step(
                "feedback",
                "AH is the high byte of AX — bits 8 through 15 — so it is the more "
                "significant half. AL covers bits 0 through 7, the least significant byte.",
            ),
            _step(
                "challenge",
                "Make RAX equal 0x0000000012347F05 by writing only sub-registers.",
                program="mov eax, 0x12345678\nmov ax, 0xABCD\nmov al, 0x05\nmov ah, 0x7F",
                expected={"registers": {"rax": 0x0000000012347F05}},
                hint="Start RAX with EAX, then patch the low 16 bits with AX, and finally "
                     "set AL and AH.",
            ),
            _step(
                "reflection",
                "Why does writing to EAX zero the upper 32 bits, while writing to AX does not?",
                hint="x86-64 makes 32-bit writes automatically extend to 64 bits, but 16-bit "
                     "and 8-bit writes leave the upper bits alone.",
            ),
        ],
    )


def lesson_mov() -> Lesson:
    return Lesson(
        id="module1.lesson3",
        module="module1",
        title="MOV: moving data",
        order=3,
        steps=[
            _step(
                "concept",
                "MOV copies a value from a source into a destination. The source is never "
                "modified — MOV is pure copying, never moving.\n\n"
                "Common forms:\n"
                "  mov rax, 5          immediate -> register\n"
                "  mov rbx, rax        register -> register\n"
                "  mov rax, [rbx]      memory -> register\n"
                "  mov [rbx], rax      register -> memory\n\n"
                "MOV cannot compute — it never adds, subtracts, or transforms data.",
                program="mov rax, 7",
                options=[
                    "Nothing — it keeps its value",
                    "It is cleared to zero",
                    "It is emptied (cut-paste)",
                    "It is swapped with the destination",
                ],
                answer=0,
                feedback={
                    1: "MOV does not clear the source; it only reads it.",
                    2: "MOV is copy-paste, not cut-paste — the source is not emptied.",
                    3: "MOV copies one way; it never swaps.",
                },
                hint="Copy-paste, not cut-paste: the source keeps its value.",
            ),
            _step(
                "intuition",
                "MOV never invents or transforms data. Whatever value the source holds is "
                "written, bit-for-bit, into the destination. This makes MOV the safest and "
                "most predictable instruction — and the foundation every other instruction "
                "is built on.",
            ),
            _step(
                "analogy",
                "MOV is copy-paste, not cut-paste. After 'mov rax, rbx', both RAX and RBX "
                "hold the same value — exactly like Ctrl+C then Ctrl+V leaves the original "
                "text in place.",
            ),
            _step(
                "visualization",
                "before:  rax = 3   rbx = 9\n\n"
                "after 'mov rax, rbx':\n\n"
                "         rax = 9   rbx = 9",
                program="mov rax, 3\nmov rbx, 9\nmov rax, rbx",
            ),
            _step(
                "example",
                "Copy an immediate into RAX, then copy RAX into RBX. The first MOV seeds "
                "RAX; the second copies RAX's value into RBX without disturbing RAX.",
                high_level="long a = 5; long b = a;",
                program="mov rax, 5\nmov rbx, rax",
            ),
            _step(
                "walkthrough",
                "Run this two-instruction program and watch the STATE panel: first RAX "
                "becomes 5, then RBX is copied from RAX — both end at 5.",
                program="mov rax, 5\nmov rbx, rax",
            ),
            _step(
                "prediction",
                "After 'mov rax, 7' and then 'mov rbx, rax', what is RBX?",
                options=["0", "7", "undefined", "14"],
                answer=1,
                program="mov rax, 7\nmov rbx, rax",
                feedback={
                    0: "MOV always writes the destination; it is never left as the old zero.",
                    2: "MOV always produces a defined value — the source's value.",
                    3: "MOV copies; it does not add. Two values are not summed.",
                },
                hint="RBX is simply set to whatever RAX holds at that moment.",
            ),
            _step(
                "response",
                "Does 'mov rax, rbx' change the value of RBX?",
                answer=0,
                options=["No, RBX keeps its value", "Yes, RBX becomes 0"],
                feedback={
                    1: "MOV copies from the source; the source register is never modified.",
                },
                hint="Re-read the analogy: MOV is copy-paste.",
            ),
            _step(
                "feedback",
                "Correct: MOV is a copy. The source register keeps its value — only the "
                "destination is written.",
            ),
            _step(
                "challenge",
                "Set RAX to 42 and RBX to 42 using exactly two MOV instructions.",
                program="mov rax, 42\nmov rbx, rax",
                expected={"registers": {"rax": 42, "rbx": 42}},
                hint="One instruction seeds RAX with the immediate; a second copies RAX "
                     "into RBX.",
            ),
            _step(
                "reflection",
                "If MOV only copies, how does a value ever get destroyed or overwritten?",
                hint="Every MOV overwrites its destination — a value is lost when a new MOV "
                     "writes over it.",
            ),
        ],
    )


def lesson_add_sub() -> Lesson:
    return Lesson(
        id="module1.lesson4",
        module="module1",
        title="ADD and SUB: arithmetic",
        order=4,
        steps=[
            _step(
                "concept",
                "ADD and SUB add or subtract an immediate or a register into a destination, "
                "replacing the destination with the result.\n\n"
                "  add rax, 3    rax = rax + 3\n"
                "  sub rbx, rcx  rbx = rbx - rcx\n\n"
                "Unlike MOV, they update the processor flags — the zero flag (ZF) is set when "
                "the result is zero, and the sign flag (SF) reflects the sign of the result. "
                "Later instructions (like jumps) read those flags.",
                program="mov rax, 5\nadd rax, 3",
                options=[
                    "add rax, 1",
                    "mov rax, 1",
                    "lea rax, [rbx]",
                    "nop",
                ],
                answer=0,
                feedback={
                    1: "MOV only copies data; it never touches flags.",
                    2: "LEA computes an address; it is documented as not affecting flags.",
                    3: "NOP does nothing at all.",
                },
                hint="Arithmetic changes flags; MOV, LEA, and NOP do not.",
            ),
            _step(
                "intuition",
                "ADD and SUB are how the CPU does math. Every other operation — counting "
                "loops, indexing arrays, comparing values — is eventually built from "
                "additions and subtractions. Get comfortable with them and everything else "
                "gets easier.",
            ),
            _step(
                "analogy",
                "Imagine a running total on a whiteboard. ADD erases the old number and "
                "writes a new, larger total. SUB writes a smaller one. The flags are the "
                "small notes the CPU leaves next to the total: 'this is now zero' (ZF) or "
                "'this went negative' (SF).",
            ),
            _step(
                "visualization",
                "rax = 5\n"
                "'add rax, 3'   ->   rax = 8,   ZF = 0\n"
                "'sub rax, 8'   ->   rax = 0,   ZF = 1\n\n"
                "ZF (zero flag) is set only when the result is exactly zero.",
                program="mov rax, 5\nadd rax, 3\nsub rax, 8",
            ),
            _step(
                "example",
                "Add 5 to RAX, then subtract 2. The first instruction makes RAX 5; ADD "
                "makes it 8; SUB makes it 6. Each instruction overwrites the destination "
                "with the new total.",
                high_level="long x = 0; x += 5; x -= 2;",
                program="mov rax, 0\nadd rax, 5\nsub rax, 2",
            ),
            _step(
                "walkthrough",
                "Run and watch RAX change 0 -> 5 -> 3 through the three instructions, and "
                "watch the flags update when the result hits zero later in the lesson.",
                program="mov rax, 0\nadd rax, 5\nsub rax, 2",
            ),
            _step(
                "prediction",
                "Starting with RAX = 5, after 'sub rax, 5' what is RAX and what is ZF?",
                options=["RAX=0, ZF=1", "RAX=0, ZF=0", "RAX=-5, ZF=1", "RAX=5, ZF=0"],
                answer=0,
                program="mov rax, 5\nsub rax, 5",
                feedback={
                    1: "A zero result sets the zero flag to 1.",
                    2: "5 - 5 is exactly zero, not a negative number.",
                    3: "SUB always writes the destination with the new result; it is not a no-op.",
                },
                hint="5 - 5 equals zero, and a zero result sets ZF to 1.",
            ),
            _step(
                "response",
                "After 'add rax, 1' on RAX = 0, is ZF set or cleared?",
                answer=1,
                options=["set", "cleared"],
                feedback={
                    0: "ZF is set only when the result is zero; here the result is 1.",
                },
                hint="The result is 1, which is not zero.",
            ),
            _step(
                "feedback",
                "Cleared: the result is 1, which is non-zero, so ZF = 0. ZF is the 'did it "
                "come out to zero?' flag.",
            ),
            _step(
                "challenge",
                "Reach RAX = 8 starting from RAX = 0 with exactly two instructions.",
                program="mov rax, 0\nadd rax, 8",
                expected={"registers": {"rax": 8}},
                hint="A MOV seeds RAX with 0 (or skip it), then one ADD brings it to 8.",
            ),
_step(
                "reflection",
                "How would you use SUB and ZF to test whether two values are equal?",
                hint="Subtract one from the other: the result is zero only when they are "
                     "equal, which sets ZF.",
            ),
        ],
    )


def lesson_lea() -> Lesson:
    return Lesson(
        id="module1.lesson5",
        module="module1",
        title="LEA: computing addresses",
        order=5,
        steps=[
            _step(
                "concept",
                "LEA (Load Effective Address) computes an address expression and stores the "
                "address itself — not the data stored at that address.\n\n"
                "  lea rax, [rbx + rcx * 2 + 4]\n\n"
                "calculates rbx + rcx*2 + 4 and puts that number into RAX. It performs the "
                "address math without ever touching memory, and — unlike ADD — it does not "
                "change any flags.",
                program="mov rbx, 0x1000\nlea rax, [rbx + 4]",
                options=[
                    "An address",
                    "The data stored at an address",
                    "A flag value",
                    "The length of an instruction",
                ],
                answer=0,
                feedback={
                    1: "Reading the data would be a memory load (like MOV) — LEA never "
                       "dereferences.",
                    2: "LEA does not touch flags at all.",
                    3: "LEA stores the result of the address math, not instruction lengths.",
                },
                hint="LEA computes WHERE something is, not what is stored there.",
            ),
            _step(
                "intuition",
                "LEA answers 'where would this location be?' and puts that location into a "
                "register. It is like asking the post office for a mailing address rather "
                "than asking them to open the mailbox.",
            ),
            _step(
                "analogy",
                "LEA is asking for a street address. MOV, by contrast, would walk to the "
                "house and read the mail inside. Same address math, completely different "
                "question being answered.",
            ),
            _step(
                "visualization",
                "rbx = 100, rcx = 8\n"
                "'lea rax, [rbx + rcx * 2]'\n\n"
                "rax = 100 + 8 * 2 = 116\n\n"
                "The brackets look like a memory access, but LEA only does the arithmetic.",
                program="mov rbx, 100\nmov rcx, 8\nlea rax, [rbx + rcx * 2]",
            ),
            _step(
                "example",
                "Compute the address rbx + 4 without dereferencing it. LEA stores 0x1004 "
                "into RAX; the memory at 0x1004 is never read.",
                high_level="long *ptr = base + 4;",
                program="mov rbx, 0x1000\nlea rax, [rbx + 4]",
            ),
            _step(
                "walkthrough",
                "Run and note that LEA changes RAX (to 0x1004) while memory is completely "
                "untouched — the STATE panel shows registers moving but no memory writes.",
                program="mov rbx, 0x1000\nlea rax, [rbx + 4]",
            ),
            _step(
                "prediction",
                "rbx = 0x1000. After 'lea rax, [rbx + 0x10]', what is RAX?",
                options=["0x1010", "0x1000", "the data at 0x1010", "0x0010"],
                answer=0,
                program="mov rbx, 0x1000\nlea rax, [rbx + 0x10]",
                feedback={
                    1: "LEA includes the base; it does not discard it.",
                    2: "LEA stores an address, never the data at an address.",
                    3: "0x10 is the displacement, but the base 0x1000 is added to it.",
                },
                hint="LEA keeps the base (0x1000) and adds the displacement (0x10).",
            ),
            _step(
                "response",
                "Does LEA read any memory?",
                answer=0,
                options=["No", "Yes"],
                feedback={
                    1: "LEA only computes an address; reading memory would be a MOV load.",
                },
                hint="The 'L' is for 'Load Effective Address', not 'Load from memory'.",
            ),
            _step(
                "feedback",
                "No. LEA only computes an address; it never dereferences. That is exactly "
                "why compilers use it for simple arithmetic like x*4+1 without disturbing "
                "the flags.",
            ),
            _step(
                "challenge",
                "Put the address 0x2004 into RAX using LEA.",
                program="mov rbx, 0x2000\nlea rax, [rbx + 4]",
                expected={"registers": {"rax": 0x2004}},
                hint="Use a base register set to 0x2000 and add a displacement of 4.",
            ),
            _step(
                "reflection",
                "LEA is often used for arithmetic (like x*4+1) without touching flags. Why "
                "is that useful right before a comparison?",
                hint="Comparisons read the flags — so you want the flags to reflect only "
                     "the comparison, not earlier arithmetic.",
            ),
        ],
    )


def lesson_flags() -> Lesson:
    return Lesson(
        id="module1.lesson6",
        module="module1",
        title="Flags: ZF and SF",
        order=6,
        steps=[
            _step(
                "concept",
                "Flags are single bits set by arithmetic and comparison instructions, kept "
                "inside the CPU's status register (RFLAGS).\n\n"
                "  ZF (zero flag) — set to 1 when the result is zero.\n"
                "  SF (sign flag) — mirrors the most significant bit of the result, so it "
                "is 1 when the result is negative.\n\n"
                "MOV, LEA, and NOP leave flags untouched. Jumps and conditional branches "
                "later read these bits to make decisions.",
                program="mov rax, 5\nsub rax, 5",
                options=[
                    "zero",
                    "negative",
                    "odd",
                    "overflow",
                ],
                answer=0,
                feedback={
                    1: "A negative result sets SF, not ZF.",
                    2: "Oddness is not tracked by ZF.",
                    3: "Overflow is tracked by OF, a different flag.",
                },
                hint="Z is for 'zero' — ZF reports whether the result came out to zero.",
            ),
            _step(
                "intuition",
                "Flags are the CPU's post-it notes after doing arithmetic. The instruction "
                "that computes the result also scribbles a note ('the answer was zero', "
                "'the answer was negative'), and a later jump reads the note to decide "
                "where to go. Without the notes, branches would have nothing to decide on.",
            ),
            _step(
                "analogy",
                "A calculator that leaves a sticky note on its screen after every "
                "calculation: 'the answer was zero' (ZF) or 'the answer was negative' (SF). "
                "The note stays until the next calculation overwrites it.",
            ),
            _step(
                "visualization",
                "'sub rax, rax'  ->  RAX = 0,   ZF = 1,   SF = 0\n\n"
                "'mov rax, 0'\n'sub rax, 1'  ->  RAX = -1,  ZF = 0,   SF = 1\n\n"
                "Notice: subtracting a register from itself is a classic way to write a "
                "zero while setting ZF.",
                program="mov rax, 5\nsub rax, 5\nsub rax, 1",
            ),
            _step(
                "example",
                "Subtract a number from itself: RAX becomes 0 and ZF becomes 1. Then "
                "decrement to see SF turn on when the value goes negative.",
                high_level="long x = 5; x = x - 5;",
                program="mov rax, 5\nsub rax, 5",
            ),
            _step(
                "walkthrough",
                "Run and read the STATE panel: after the first SUB, ZF is 1; after the "
                "second SUB (which goes below zero), SF becomes 1.",
                program="mov rax, 5\nsub rax, 5\nsub rax, 1",
            ),
            _step(
                "prediction",
                "After 'mov rax, 1; sub rax, 2', which flags are set?",
                options=["SF only", "ZF only", "SF and ZF", "neither"],
                answer=0,
                program="mov rax, 1\nsub rax, 2",
                feedback={
                    1: "The result is -1, not zero, so ZF is cleared.",
                    2: "ZF and SF can never both be set for a single result: -1 is not zero.",
                    3: "A negative result does set SF — but the zero flag stays clear, so "
                       "'SF only' is correct.",
                },
                hint="1 - 2 = -1. Is -1 zero? Is it negative?",
            ),
            _step(
                "response",
                "MOV leaves flags untouched. True or false?",
                answer=0,
                options=["True", "False"],
                feedback={
                    1: "MOV only copies data; flags are changed only by arithmetic and "
                       "comparison instructions.",
                },
                hint="Which instructions change flags — copies or math?",
            ),
            _step(
                "feedback",
                "True. MOV does not affect flags; only arithmetic and comparison "
                "instructions do. This is why LEA is useful for math before a compare.",
            ),
            _step(
                "challenge",
                "End with ZF = 1 by doing arithmetic that zeroes RAX.",
                program="mov rax, 5\nsub rax, 5",
                expected={"registers": {"rax": 0}, "flags": {"zf": True}},
                hint="Subtract a register from itself (sub rax, rax) — a guaranteed zero "
                     "with ZF set.",
            ),
            _step(
                "reflection",
                "Why is ZF useful for loops? What would happen if SUB did not set flags?",
                hint="Loops need to know when to stop; if SUB did not set ZF, checking for "
                     "zero would need an extra comparison.",
            ),
        ],
    )


def lesson_bits() -> Lesson:
    return Lesson(
        id="module1.lesson7",
        module="module1",
        title="Bitwise logic and shifts",
        order=7,
        steps=[
            _step(
                "concept",
                "The CPU also does bit-by-bit math. AND, OR, and XOR compare each bit of "
                "its two operands independently:\n\n"
                "  AND — the result bit is 1 only where both inputs are 1 (a mask that "
                "keeps selected bits).\n"
                "  OR  — the result bit is 1 where either input is 1 (a bit setter).\n"
                "  XOR — the result bit is 1 where the inputs differ (a toggle).\n\n"
                "XORing a register with itself is the classic idiom for a fast zero: "
                "'xor rax, rax' clears RAX beautifully.",
                program="xor rax, rax",
            ),
            _step(
                "intuition",
                "Think of AND as a stencil: it lets exactly the bits you want pass and "
                "blanks the rest. XOR is a light switch: flip once and you change the "
                "room, flip twice and you are back where you started.",
            ),
            _step(
                "analogy",
                "XOR is unbreakable message passing in disguise: if you know the mask, "
                "XOR recovers the original message. That single property is the seed of "
                "nearly every cipher and every crc.",
            ),
            _step(
                "visualization",
                "  AND  0b1100 & 0b1010 = 0b1000\n"
                "  OR   0b1100 | 0b1010 = 0b1110\n"
                "  XOR  0b1100 ^ 0b1010 = 0b0110\n\n"
                "Each column of depth is decided independently of its neighbours.",
                program="mov rax, 0b1100\nand rax, 0b1010",
            ),
            _step(
                "example",
                "Shifts slide the bits. 'shl rax, 1' doubles RAX and fills the low bit "
                "with 0; 'shr rax, 1' halves it. A left shift is multiplication by 2; a "
                "right shift is division. Compilers use shifts wherever a multiply or "
                "divide by a power of two is cheap.",
                high_level="x <<= n;   x >>= n;",
                program="mov rax, 0x0F\nshl rax, 4",
            ),
            _step(
                "walkthrough",
                "Run this: RAX starts 0x0F, then shl by 4 gives 0xF0. The bit pattern "
                "literally walked left across the byte.",
                program="mov rax, 0x0F\nshl rax, 4",
            ),
            _step(
                "prediction",
                "After 'mov rax, 0b1100; shr rax, 2', what is RAX?",
                options=["0b0011", "0b110000", "0b1100", "0b0000"],
                answer=0,
                program="mov rax, 0b1100\nshr rax, 2",
                feedback={
                    1: "shr moves bits right, toward the least-significant end, and drops "
                       "the ones that fall off.",
                    2: "shr halves and discards the low bits rather than keeping them.",
                    3: "A right shift by 2 always reduces the value; 0b1100 is not zero.",
                },
                hint="Shift right by two: each bit moves two positions toward bit 0.",
            ),
            _step(
                "response",
                "Fast way to clear RAX to zero using one register?",
                answer=0,
                options=["xor rax, rax", "mov rax, 1", "and rax, rax"],
                feedback={
                    1: "mov rax, 1 sets RAX to 1, not zero.",
                    2: "ANDing RAX with itself leaves it unchanged.",
                },
                hint="XOR a register with itself: every differing-bit position becomes 0.",
            ),
            _step(
                "feedback",
                "Correct: 'xor rax, rax' clears RAX. It is shorter and often faster than "
                "'mov rax, 0', because the XOR does not need to encode an immediate.",
            ),
            _step(
                "challenge",
                "Write a single instruction that clears RAX (set it to 0) using only "
                "registers.",
                program="mov rax, 5\nxor rax, rax",
                expected={"registers": {"rax": 0}},
                hint="XOR the register with itself.",
            ),
            _step(
                "reflection",
                "How does shifting left twice relate to multiplying by 4? Why might a "
                "compiler prefer 'shl' over 'imul'?",
                hint="Each left shift multiplies by 2, so two shifts multiply by 4; a "
                     "single shift instruction is cheaper than a full multiply.",
            ),
        ],
    )


def module1() -> Module:
    return Module(
        id="module1",
        title="CPU Architecture and Registers",
        order=1,
        lessons=[
            lesson_fde(),
            lesson_registers(),
            lesson_mov(),
            lesson_add_sub(),
            lesson_lea(),
            lesson_flags(),
            lesson_bits(),
        ],
    )
