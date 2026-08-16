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
                "Press R to run the challenge: two equal values (9 and 9) are compared "
                "with CMP. Read the final STATE panel — which flag ends up set?",
                program=read_asm("module3/lesson1_cmp_test/challenge.asm"),
                options=["ZF", "SF", "CF", "OF"],
                answer=0,
                feedback={
                    1: "9 - 9 is zero, not negative, so SF stays clear.",
                    2: "An equality produces no borrow, so CF stays clear.",
                    3: "The signs never crossed, so OF stays clear.",
                },
                hint="Press R — equal operands make the zero flag 1.",
            ),
            _step(
                "response",
                "Run the example (press R): 'cmp rax, rbx' (both 5) is followed by 'test "
                "rax, rax'. The TEST of the non-zero value 5 recomputes the flags. Is the "
                "zero flag set or cleared at the end? Type: set or cleared.",
                program=read_asm("module3/lesson1_cmp_test/example.asm"),
                keywords=["cleared"],
                model_answer="Cleared — the last flag-writing instruction is TEST rax, rax; "
                    "5 is non-zero, so it clears ZF even though the earlier CMP of equal "
                    "values had set it.",
                hint="After R, the STATE panel shows ZF = 0.",
            ),
            _step(
                "feedback",
                "ZF = 0 at the end. CMP 5, 5 set ZF = 1, but the following TEST overwrote "
                "the flags with its own result (5 is non-zero), clearing ZF. Both looked "
                "like the same question, but the flags always reflect the most recent "
                "flag-writing instruction.",
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
                "Press R to run the example: RAX = 3 is compared to 5, and the code reads "
                "'if rax >= 5 goto else_branch'. Read the final STATE panel — which fall-"
                "through mov wrote RBX?",
                program=read_asm("module3/lesson2_conditional_jumps/example.asm"),
                options=["rbx = 1", "rbx = 2", "rbx = 3", "rbx = 5"],
                answer=0,
                feedback={
                    1: "The 'rbx = 2' block only runs when RAX >= 5; here 3 < 5.",
                    2: "The branches write 1 or 2; the compared operands stay untouched.",
                    3: "The branches write 1 or 2; the compared operands stay untouched.",
                },
                hint="Press R — 3 < 5, so JGE is not taken and the fall-through sets RBX=1.",
            ),
            _step(
                "response",
                "Run this program (press R): RAX = 7 is compared to 5 and 'jge big' is "
                "taken because 7 >= 5. Type the value that ends up in RBX.",
                program="mov rax, 7\ncmp rax, 5\njge big\nmov rbx, 1\njmp done\n"
                        "big:\nmov rbx, 2\ndone:\nmov rax, 60\nmov rdi, 0\nsyscall",
                keywords=["2"],
                model_answer="2 — CMP computed 7 - 5 with no borrow, so JGE took the branch "
                    "to 'big', which wrote 2 into RBX.",
                hint="After R, RBX shows 2 — the branch condition held.",
            ),
            _step(
                "feedback",
                "RBX = 2. The flags from CMP (7 >= 5) made JGE jump to the 'big' block. A "
                "conditional jump either moves RIP to its target or falls through — here it "
                "took the target, and RBX proves which mov ran.",
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
                "Press R to run the example: the loop counter starts at 5 and adds itself "
                "into RAX each pass (5+4+3+2+1). Read the final panel — what total ends up "
                "in R8 (RAX's copy)?",
                program=read_asm("module3/lesson3_loops/example.asm"),
                options=["15", "5", "0", "20"],
                answer=0,
                feedback={
                    1: "5 is just the starting counter value, not the sum.",
                    2: "RAX accumulates; the loop never clears it.",
                    3: "The counter runs 5..1, and 1+2+3+4+5 = 15, not 20.",
                },
                hint="Press R — R8 shows the accumulated sum 0+5+4+3+2+1.",
            ),
            _step(
                "response",
                "Run the challenge (press R): it sums the integers from 10 down to 1. "
                "Type the total that ends up in RBX.",
                program=read_asm("module3/lesson3_loops/challenge.asm"),
                keywords=["55"],
                model_answer="55 — each pass adds the counter (10, 9, ..., 1) into RBX, "
                    "then decrements and jumps back until the counter reaches 0.",
                hint="After R, RBX shows the sum of 1..10.",
            ),
            _step(
                "feedback",
                "RBX = 55. The backward edge is the loop: 'add rbx, rcx' accumulates, "
                "'sub rcx, 1' counts down, and 'jne' jumps back while RCX is non-zero. "
                "When RCX hits zero the JNE falls through and the loop ends.",
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
                "Press R to run the example: RAX = 2 enters a CMP/JE chain and finds "
                "'case 2'. Read the final panel — which value ends up in R8 (the copy of "
                "RBX)?",
                program=read_asm("module3/lesson4_switches/example.asm"),
                options=["20", "10", "0", "40"],
                answer=0,
                feedback={
                    1: "10 belongs to case 1, which is skipped when RAX = 2.",
                    2: "0 is the default path; a matching case takes priority.",
                    3: "The chain picks one case; it does not double the value.",
                },
                hint="Press R — RBX takes the value of the matched case (2 -> 20).",
            ),
            _step(
                "response",
                "Run the challenge (press R): the same switch style with RAX = 3 chooses "
                "case 3, which stores 300 into RBX. Type the value that ends up in RBX.",
                program=read_asm("module3/lesson4_switches/challenge.asm"),
                keywords=["300"],
                model_answer="300 — the CMP/JE chain fell through cases 1 and 2, matched "
                    "case 3, and that block wrote 300 before jumping to the merge point.",
                hint="After R, RBX shows 300.",
            ),
            _step(
                "feedback",
                "RBX = 300 — reading the chain as a dispatch: each CMP tests one case, the "
                "matched JE transfers to that block, and the trailing JMP reaches the "
                "merge. That is the machine shape of a switch, whether a chain or a jump "
                "table.",
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
                "Press R to run the example and read the final STATE panel: it reads as "
                "'rcx = max(rax, rbx)' with RAX = 6, RBX = 2. What value ends up in R8 "
                "(RCX's copy)?",
                program=read_asm("module3/lesson5_rebuild_pseudocode/example.asm"),
                options=["6", "2", "8", "4"],
                answer=0,
                feedback={
                    1: "2 is the smaller operand; the max keeps the larger.",
                    2: "The function selects a value; it does not add them.",
                    3: "Neither operand shrinks; the compare only picks the larger.",
                },
                hint="Press R — RCX holds the larger of the two inputs.",
            ),
            _step(
                "response",
                "Run the challenge (press R): it computes max(RAX, RBX) with RAX = 3, "
                "RBX = 7 and must keep the larger in RBX. Type the value that ends up in "
                "RBX.",
                program=read_asm("module3/lesson5_rebuild_pseudocode/challenge.asm"),
                keywords=["7"],
                model_answer="7 — since 3 < 7 the branch that copies RAX into RBX is not "
                    "taken, so RBX keeps its larger input: 'if (rax > rbx) rbx = rax;'.",
                hint="After R, RBX shows the larger of the two inputs.",
            ),
            _step(
                "feedback",
                "RBX = 7 — a conditional copy, read back as 'if (rax > rbx) then rbx = "
                "rax'. Reconstructing that decision from a CMP/JG pair is exactly the "
                "pseudocode-recovery skill the lesson is teaching.",
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
