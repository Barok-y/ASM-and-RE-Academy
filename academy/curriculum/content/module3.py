from __future__ import annotations

from ..models import Lesson, LessonStep, Module
from ._asm import read_asm


def _step(kind: str, content: str = "", **kwargs) -> LessonStep:
    return LessonStep(kind=kind, content=content, **kwargs)


def lesson_cmp_test() -> Lesson:
    return Lesson(
        id="module3.lesson1",
        module="module3",
        title="CMP and TEST",
        order=1,
        steps=[
            _step(
                "concept",
                "CMP compares two operands by subtracting them internally and "
                "setting flags, WITHOUT storing the difference. TEST does the same "
                "with a bitwise AND. Both exist so you can inspect a relationship "
                "without destroying the values.",
            ),
            _step(
                "intuition",
                "CMP and TEST are like asking the CPU 'how do these relate?' - "
                "the answer is written in the flags (ZF, SF, CF, OF), not in a "
                "register.",
            ),
            _step(
                "analogy",
                "A judge who compares two numbers on scrap paper, then only "
                "announces the verdict (equal, less, greater) without showing the "
                "arithmetic: that is CMP.",
            ),
            _step(
                "visualization",
                "'cmp rax, 5'  computes rax - 5:\n"
                "  rax = 5  ->  ZF = 1\n"
                "  rax = 9  ->  ZF = 0, CF = 0 (9 - 5 positive)\n"
                "  rax = 2  ->  ZF = 0, CF = 1 (2 - 5 borrows)\n"
                "'test rax, rax'  ->  ZF = 1 if rax == 0.",
            ),
            _step(
                "example",
                "Compare two equal registers, then test RAX against itself.",
                high_level="if (a == b) {}   if (x != 0) {}",
                program=read_asm("module3/lesson1_cmp_test/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: CMP sets ZF=1 for two equal values, then TEST against "
                "nonzero RAX clears ZF. Neither instruction changes RAX or RBX.",
                program=read_asm("module3/lesson1_cmp_test/example.asm"),
            ),
            _step(
                "prediction",
                "RAX = 9. After 'cmp rax, 5', which flag is set?",
                options=["ZF", "SF", "CF", "none are set"],
                answer=2,
                feedback={
                    0: "9 - 5 is not zero.",
                    1: "The result is positive; SF reflects the sign bit.",
                    3: "A borrow occurred, so CF is set.",
                },
            ),
            _step(
                "response",
                "Does CMP modify RAX or RBX?",
                answer=0,
                options=["No, only flags change", "Yes, RAX gets the difference"],
            ),
            _step(
                "feedback",
                "Correct: CMP only sets flags; the subtraction result is discarded.",
            ),
            _step(
                "challenge",
                "Compare two equal values with CMP so that ZF becomes 1, without "
                "changing the registers.",
                program=read_asm("module3/lesson1_cmp_test/challenge.asm"),
                expected={"flags": {"zf": True}},
            ),
            _step(
                "reflection",
                "Why does TEST often use a register against itself ('test rax, "
                "rax') instead of a CMP against zero?",
            ),
        ],
    )


def lesson_conditional_jumps() -> Lesson:
    return Lesson(
        id="module3.lesson2",
        module="module3",
        title="Conditional Jumps",
        order=2,
        steps=[
            _step(
                "concept",
                "Conditional jumps transfer control based on flags. JE/JNE use ZF; "
                "JG/JGE and JL/JLE use SF/OF and CF for signed comparisons; JA/JB "
                "use CF for unsigned. A jump is either taken (RIP moves to the "
                "target) or not (RIP advances to the next instruction).",
            ),
            _step(
                "intuition",
                "CMP is the question and a conditional jump is the decision. "
                "Together they implement every if/else in your programs.",
            ),
            _step(
                "analogy",
                "A railway switch: the train (CPU) always runs to a junction, the "
                "signal (flags) decides which track (next instruction) it takes.",
            ),
            _step(
                "visualization",
                "cmp rax, 5\n"
                "je  equal    ; taken only if rax == 5\n"
                "jg  greater  ; taken only if rax >  5\n"
                "jl  less     ; taken only if rax <  5\n"
                "next:        ; reached when no jump was taken",
            ),
            _step(
                "example",
                "An if/else: if RAX >= 5 pick branch A, else branch B.",
                high_level="if (x >= 5) { rbx = 1; } else { rbx = 2; }",
                program=read_asm("module3/lesson2_conditional_jumps/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: CMP sets flags, JGE is not taken (3 < 5), so RBX becomes 1 "
                "and JMP skips the else branch.",
                program=read_asm("module3/lesson2_conditional_jumps/example.asm"),
            ),
            _step(
                "prediction",
                "RAX = 7. After 'cmp rax, 5', which jump is taken?",
                options=["jl target", "je target", "jg target", "jne target"],
                answer=2,
                feedback={
                    0: "7 is greater than 5, so the less-than jump falls through.",
                    1: "7 is not equal to 5.",
                    3: "JNE would be taken, but JNE is not signed-greater.",
                },
            ),
            _step(
                "response",
                "Which flag does JE check?",
                answer=0,
                options=["ZF", "CF", "SF", "OF"],
            ),
            _step(
                "feedback",
                "JE (jump if equal) is taken when ZF = 1.",
            ),
            _step(
                "challenge",
                "If RAX >= 10 put 100 in RBX, else put 50 in RBX. RAX starts at 10.",
                program=read_asm("module3/lesson2_conditional_jumps/challenge.asm"),
                expected={"registers": {"rbx": 100}},
            ),
            _step(
                "reflection",
                "JG and JA both mean 'greater than', but for different kinds of "
                "numbers. What breaks if you use the wrong one?",
            ),
        ],
    )


def lesson_loops() -> Lesson:
    return Lesson(
        id="module3.lesson3",
        module="module3",
        title="Loops",
        order=3,
        steps=[
            _step(
                "concept",
                "A loop is a backward conditional jump plus a counter. The classic "
                "pattern loads a counter, runs a body, decrements the counter, and "
                "jumps back while the counter is nonzero. Every for/while loop "
                "compiles to this shape.",
            ),
            _step(
                "intuition",
                "A loop is just a branch that points backward. The CPU still "
                "executes one instruction at a time - it simply keeps revisiting "
                "the same address until a condition stops it.",
            ),
            _step(
                "analogy",
                "Walking laps around a track: you run the same loop body each lap, "
                "count each lap on a tally (the counter), and stop when the tally "
                "reaches your goal.",
            ),
            _step(
                "visualization",
                "mov rcx, 5        ; counter = 5\n"
                "top:              ; <-- loop back here\n"
                "  add rax, rcx    ; body\n"
                "  sub rcx, 1      ; decrement\n"
                "  jne top         ; if counter != 0, repeat",
            ),
            _step(
                "example",
                "Sum the integers from 5 down to 1.",
                high_level="int total = 0; for (int i = 5; i >= 1; i--) total += i;",
                program=read_asm("module3/lesson3_loops/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step and watch RAX grow 0 -> 5 -> 9 -> 12 -> 14 -> 15 as RCX "
                "counts 5,4,3,2,1; when RCX hits 0 the JNE falls through.",
                program=read_asm("module3/lesson3_loops/example.asm"),
            ),
            _step(
                "prediction",
                "After the loop 'mov rcx, 3; top: add rax, rcx; sub rcx, 1; jne "
                "top', what is the final RCX?",
                options=["3", "1", "0", "-1"],
                answer=2,
                feedback={
                    0: "The counter decreases, it does not stay at its start.",
                    1: "The loop exits only after the decrement to zero.",
                    3: "JNE stops when RCX == 0, before going negative.",
                },
            ),
            _step(
                "response",
                "Which instruction sends control back to the top of a counter loop?",
                answer=1,
                options=["sub rcx, 1", "jne top"],
            ),
            _step(
                "feedback",
                "JNE is the conditional jump back to the loop label.",
            ),
            _step(
                "challenge",
                "Sum the integers from 10 down to 1 into RBX.",
                program=read_asm("module3/lesson3_loops/challenge.asm"),
                expected={"registers": {"rbx": 55}},
            ),
            _step(
                "reflection",
                "A loop that never makes progress toward its exit condition is "
                "infinite. In the emulator, what happens when a program never "
                "stops?",
            ),
        ],
    )


def lesson_switches() -> Lesson:
    return Lesson(
        id="module3.lesson4",
        module="module3",
        title="Switches and Jump Tables",
        order=4,
        steps=[
            _step(
                "concept",
                "A switch dispatches on an integer value. Sparse cases compile to "
                "a chain of CMP/JE; dense, consecutive cases can compile to a jump "
                "table - an array of target addresses indexed by the value, "
                "jumped through via 'jmp [table + index*8]'.",
            ),
            _step(
                "intuition",
                "A switch is an if/else written as a table: instead of asking many "
                "questions in sequence, you compute the answer's slot directly.",
            ),
            _step(
                "analogy",
                "A hotel front desk with a row of mail slots: find the room number "
                "and grab the key from that exact slot (jump table), instead of "
                "checking every room one by one (CMP chain).",
            ),
            _step(
                "visualization",
                "case 1 -> address A\n"
                "case 2 -> address B\n"
                "case 3 -> address C\n"
                "value = 2  ->  jmp jump_table[2]  ->  address B",
            ),
            _step(
                "example",
                "A three-way switch implemented as a CMP/JE chain on RAX = 2.",
                high_level="switch (x) { case 1: rbx = 10; break; case 2: rbx = 20; "
                "break; default: rbx = 0; }",
                program=read_asm("module3/lesson4_switches/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: the first JE (RAX == 1) falls through, the second JE "
                "(RAX == 2) is taken, RBX becomes 20, and JMP skips the rest.",
                program=read_asm("module3/lesson4_switches/example.asm"),
            ),
            _step(
                "prediction",
                "For a switch on dense values 0..255, which implementation is "
                "usually faster?",
                options=["a CMP/JE chain", "a jump table", "they are identical", "a loop"],
                answer=1,
                feedback={
                    0: "A chain checks cases one at a time - up to 256 comparisons.",
                    2: "A table is one indexed memory jump, not a scan.",
                    3: "Switches do not iterate; they dispatch.",
                },
            ),
            _step(
                "response",
                "When do compilers typically emit a jump table instead of a CMP "
                "chain?",
                answer=0,
                options=[
                    "dense, consecutive case values",
                    "very sparse case values",
                    "only two cases",
                    "never, only chains are legal",
                ],
            ),
            _step(
                "feedback",
                "Dense consecutive values index the table cleanly; sparse values "
                "would waste table space.",
            ),
            _step(
                "challenge",
                "Implement a three-way switch: case 1 -> RBX=100, case 2 -> "
                "RBX=200, case 3 -> RBX=300, default -> RBX=0. RAX starts at 3.",
                program=read_asm("module3/lesson4_switches/challenge.asm"),
                expected={"registers": {"rbx": 300}},
            ),
            _step(
                "reflection",
                "A jump table stores CODE ADDRESSES in memory. How is that a "
                "security risk in a real binary?",
            ),
        ],
    )


def lesson_rebuild_pseudocode() -> Lesson:
    return Lesson(
        id="module3.lesson5",
        module="module3",
        title="Rebuild Pseudocode",
        order=5,
        steps=[
            _step(
                "concept",
                "Reading assembly 'for what it does' means recovering the "
                "high-level shape: match CMP/JCC patterns to if/else, backward "
                "jumps to loops, and straight-line code to assignment. This "
                "reconstruction is the core skill of reverse engineering.",
            ),
            _step(
                "intuition",
                "A compiler turns structure into jump patterns; the RE reads "
                "jump patterns back into structure. CMP+JCC = decision, backward "
                "JCC = repetition.",
            ),
            _step(
                "analogy",
                "Like reading sheet music backward into a composer's intent: the "
                "notes (instructions) are exact, but you want the phrase "
                "(the if/else, the loop) they were written to express.",
            ),
            _step(
                "visualization",
                "cmp rax, rbx      ; compare two values\n"
                "jle smaller       ; if rax <= rbx go smaller\n"
                "mov rcx, rax      ; then-branch: rcx = rax\n"
                "jmp done\n"
                "smaller:\n"
                "mov rcx, rbx      ; else-branch: rcx = rbx\n"
                "done:\n"
                "; reconstructs as:  rcx = (rax > rbx) ? rax : rbx;",
            ),
            _step(
                "example",
                "Read this blob and name what it computes.",
                high_level="rcx = max(rax, rbx);",
                program=read_asm("module3/lesson5_rebuild_pseudocode/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step through: CMP compares 6 and 2, JLE falls through, RCX takes "
                "RAX (6), so the result is the maximum.",
                program=read_asm("module3/lesson5_rebuild_pseudocode/example.asm"),
            ),
            _step(
                "prediction",
                "A function ends with 'jne loop_top' jumping backward. What "
                "structure does it contain?",
                options=["an if/else", "a loop", "a function call", "a switch"],
                answer=1,
                feedback={
                    0: "Forward jumps with a merge point suggest if/else.",
                    2: "Function calls use CALL/RET, not JNE.",
                    3: "Switches use many forward CMP/JE branches.",
                },
            ),
            _step(
                "response",
                "What does 'cmp rax, rbx; jg target' most directly express in "
                "pseudocode?",
                answer=1,
                options=["a loop", "an if (rax > rbx)"],
            ),
            _step(
                "feedback",
                "CMP + JG is the machine-code form of 'if (rax > rbx)'.",
            ),
            _step(
                "challenge",
                "This function computes max(RAX, RBX) and must leave it in RBX. "
                "RAX = 3, RBX = 7.",
                program=read_asm("module3/lesson5_rebuild_pseudocode/challenge.asm"),
                expected={"registers": {"rbx": 7}},
            ),
            _step(
                "reflection",
                "Why does understanding jump structure matter when reading a "
                "binary with no source code?",
            ),
        ],
    )


def module3() -> Module:
    return Module(
        id="module3",
        title="Control Flow",
        order=3,
        lessons=[
            lesson_cmp_test(),
            lesson_conditional_jumps(),
            lesson_loops(),
            lesson_switches(),
            lesson_rebuild_pseudocode(),
        ],
    )
