from __future__ import annotations

from ..models import Lesson, LessonStep, Module
from ._asm import read_asm


def _step(kind: str, content: str = "", **kwargs) -> LessonStep:
    return LessonStep(kind=kind, content=content, **kwargs)


def lesson_elf() -> Lesson:
    return Lesson(
        id="module6.lesson1",
        module="module6",
        title="ELF Structure",
        order=1,
        steps=[
            _step(
                "concept",
                "An ELF file (Linux's executable format) starts with a header, "
                "then program headers (how the loader maps it into memory) and "
                "section headers (how tools describe its contents). ELF maps "
                "code into a read+execute .text, globals into .data/.bss, and "
                "so on - the segments from Module 2 are where the file's "
                "contents actually land.",
            ),
            _step(
                "intuition",
                "The ELF header is a map: program headers say where pieces go in "
                "memory at runtime, section headers say what each piece means to "
                "a disassembler or debugger.",
            ),
            _step(
                "analogy",
                "An ELF binary is a shipping crate with two manifests: one for "
                "the loader (program headers) telling dock workers which shelf "
                "(memory) each box goes to, and one for inspectors (section "
                "headers) naming the boxes.",
            ),
            _step(
                "visualization",
                "ELF file:\n"
                "  ELF header  (magic 7f 45 4c 46, arch, entry point)\n"
                "  program headers  ->  load into memory\n"
                "  .text  (code, R+X)\n"
                "  .data  (initialized globals, RW)\n"
                "  .bss   (zeroed globals, RW)\n"
                "  section headers  ->  describe each section",
            ),
            _step(
                "example",
                "The .text section is exactly this kind of code: a leaf "
                "function taking RDI and returning RDI + 1 in RAX.",
                high_level="long leaf(long x) { return x + 1; }",
                program=read_asm("module6/lesson1_elf/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step through the leaf: RDI holds the argument, ADD computes the "
                "result in RAX, and the exit syscall ends the process. A "
                "disassembler would show the same bytes in .text.",
                program=read_asm("module6/lesson1_elf/example.asm"),
            ),
            _step(
                "prediction",
                "Which section holds the executable code of an ELF binary?",
                options=[".text", ".data", ".bss", ".rodata"],
                answer=0,
                feedback={
                    1: ".data holds initialized, writable globals.",
                    2: ".bss holds zero-initialized globals.",
                    3: ".rodata holds read-only constants.",
                },
            ),
            _step(
                "response",
                "What do program headers describe to the OS loader?",
                answer=1,
                options=[
                    "the author's name",
                    "how file pieces map into memory at runtime",
                ],
            ),
            _step(
                "feedback",
                "Program headers drive the loader's memory mapping.",
            ),
            _step(
                "challenge",
                "This 'function' computes rdi*3 + 2. Given RDI = 4, run it and "
                "leave the result (14) in R8.",
                program=read_asm("module6/lesson1_elf/challenge.asm"),
                expected={"registers": {"r8": 14}},
            ),
            _step(
                "reflection",
                "Why does a stripped binary still run if it has no symbol or "
                "section information left?",
            ),
        ],
    )


def lesson_sections_symbols() -> Lesson:
    return Lesson(
        id="module6.lesson2",
        module="module6",
        title="Sections and Symbols",
        order=2,
        steps=[
            _step(
                "concept",
                "Sections group data by role: .text is code, .data holds "
                "initialized globals, .bss holds zero-initialized globals, and "
                ".rodata holds constants. Symbols are the names (functions, "
                "globals) recorded in a symbol table; stripping a binary removes "
                "them, which is why RE of stripped binaries works from "
                "addresses and strings instead.",
            ),
            _step(
                "intuition",
                "Sections answer 'what kind of bytes are these?' and symbols "
                "answer 'what is this thing called?'. Without symbols you lose "
                "the names but keep all the behavior.",
            ),
            _step(
                "analogy",
                "Sections are labeled bins in a hardware store (screws, nails, "
                "bolts); symbols are the part numbers on each item. Strip the "
                "part numbers and the bins still hold the right parts - you just "
                "have to identify each screw yourself.",
            ),
            _step(
                "visualization",
                ".text  0x400000  code        (R+X)\n"
                ".data  0x600000  globals     (RW)\n"
                ".bss   0x610000  zeroed glob (RW)\n"
                ".rodata         consts      (R)\n"
                "symtab: main, strcmp, global_flag  -> stripped => gone",
            ),
            _step(
                "example",
                "The .bss segment starts as all zeros - write a global into a "
                "bss slot and read it back.",
                high_level="static int counter; counter = 7;",
                program=read_asm("module6/lesson2_sections_symbols/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: RBX addresses .bss, the byte store writes 7 into it, and "
                "MOVZX reads it back - proving .bss was zero before the write.",
                program=read_asm("module6/lesson2_sections_symbols/example.asm"),
            ),
            _step(
                "prediction",
                "A global 'int g = 5;' with an initializer lives in which "
                "section?",
                options=[".data", ".bss", ".text", ".rodata"],
                answer=0,
                feedback={
                    1: ".bss is for globals WITHOUT an initializer (zeroed).",
                    2: ".text is code, not data.",
                    3: ".rodata is for constants, not writable globals.",
                },
            ),
            _step(
                "response",
                "What does stripping a binary remove?",
                answer=1,
                options=["the code bytes", "the symbol table names"],
            ),
            _step(
                "feedback",
                "Stripping removes symbol names; code and sections remain.",
            ),
            _step(
                "challenge",
                "Write 3 into a .bss slot, read the zero-initialized neighbor, "
                "add 5, and keep the sum (8) in RBX.",
                program=read_asm("module6/lesson2_sections_symbols/challenge.asm"),
                expected={"registers": {"rbx": 8}},
            ),
            _step(
                "reflection",
                "Why do RE tools look at string literals first when a binary has "
                "no symbols?",
            ),
        ],
    )


def lesson_cfg() -> Lesson:
    return Lesson(
        id="module6.lesson3",
        module="module6",
        title="Control Flow Graphs",
        order=3,
        steps=[
            _step(
                "concept",
                "A control flow graph models a function as nodes (basic blocks - "
                "straight-line runs with one entry and one exit) and edges "
                "(branches). Jumps become edges; falling through becomes an "
                "edge to the next block. Reconstructing the CFG is how RE tools "
                "recover a function's shape without symbols.",
            ),
            _step(
                "intuition",
                "A CFG is the 'skeleton' of a function: strip out the arithmetic "
                "and all that remains is the branching skeleton that says "
                "if/else/loop.",
            ),
            _step(
                "analogy",
                "A metro map: stations (basic blocks) and lines (jumps). You can "
                "read a city's structure from the map without riding every "
                "train - that is what a CFG does for a function.",
            ),
            _step(
                "visualization",
                "        [ entry: mov rax,5; mov rbx,10 ]\n"
                "                    |\n"
                "                    v cmp/jg\n"
                "   [ swap block ] --->-- [ done block ]\n"
                "          |                 ^\n"
                "          +-----------------+\n"
                "   3 nodes, 3 edges: a diamond CFG",
            ),
            _step(
                "example",
                "A tiny function with two paths: swap or skip.",
                high_level="if (rax > rbx) swap(&rax, &rbx);",
                program=read_asm("module6/lesson3_cfg/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step and watch the CFG path: CMP decides, JG is not taken (5 > "
                "10 is false), so control falls to the merge block and RAX "
                "stays 5.",
                program=read_asm("module6/lesson3_cfg/example.asm"),
            ),
            _step(
                "prediction",
                "A function whose CFG has a backward edge most likely contains "
                "which structure?",
                options=["a loop", "an if/else", "a switch", "a return"],
                answer=0,
                feedback={
                    1: "if/else is a forward diamond, not a backward edge.",
                    2: "A switch is many forward edges to case blocks.",
                    3: "A return ends a path; it does not loop back.",
                },
            ),
            _step(
                "response",
                "What is a basic block?",
                answer=0,
                options=[
                    "a run of instructions with one entry and one exit",
                    "any single instruction",
                    "a whole function",
                    "a block of memory",
                ],
            ),
            _step(
                "feedback",
                "A basic block is straight-line code ending in a branch.",
            ),
            _step(
                "challenge",
                "This CFG has two outcomes: if RAX > 0 double it, else zero it. "
                "RAX = 6, so the result (12) must land in RBX.",
                program=read_asm("module6/lesson3_cfg/challenge.asm"),
                expected={"registers": {"rbx": 12}},
            ),
            _step(
                "reflection",
                "How does a CFG help you find where an input value is validated "
                "in a crackme?",
            ),
        ],
    )


def lesson_crackmes() -> Lesson:
    return Lesson(
        id="module6.lesson4",
        module="module6",
        title="Crackmes and Patching",
        order=4,
        steps=[
            _step(
                "concept",
                "A crackme is a small binary that checks a password and grants "
                "or denies access. Reversing it means finding the comparison "
                "(often a strcmp or an immediate compare), and patching means "
                "altering bytes so the check always succeeds - commonly by "
                "flipping a conditional jump or NOP-padding the 'deny' path. "
                "Patching is verified by re-running the binary and observing "
                "the new behavior.",
            ),
            _step(
                "intuition",
                "Every password check is a CMP plus a conditional jump. Find "
                "that one decision point and you can bend it either way.",
            ),
            _step(
                "analogy",
                "A guard with one yes/no question at the door. Bypass him by "
                "rewriting his answer sheet (patch the jump) so 'no' becomes "
                "'yes' before he can open his mouth.",
            ),
            _step(
                "visualization",
                "original:  cmp rax, 1337\n"
                "           jne deny        ; wrong password -> denied\n"
                "patched:   cmp rax, 1337\n"
                "           je  deny        ; flipped: equal -> denied!\n"
                "with rax = 0, the patched 'je' is NOT taken -> access granted.",
            ),
            _step(
                "example",
                "A password check that grants access when the candidate equals "
                "42.",
                high_level="if (password == 42) grant(); else deny();",
                program=read_asm("module6/lesson4_crackmes/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: the candidate 42 is compared to the expected 42, JE is "
                "taken, and RBX becomes 1 (granted).",
                program=read_asm("module6/lesson4_crackmes/example.asm"),
            ),
            _step(
                "prediction",
                "Which single-byte change to a conditional jump most directly "
                "defeats a password check?",
                options=[
                    "flip the jump condition",
                    "change the password literal",
                    "add a NOP to the grant path",
                    "change the CMP to MOV",
                ],
                answer=0,
                feedback={
                    1: "You may not know the real password to substitute.",
                    2: "That does not make the check pass.",
                    3: "That makes the grant path do nothing useful.",
                },
            ),
            _step(
                "response",
                "What instruction flips the condition of a jump during a patch?",
                answer=1,
                options=["MOV", "changing je to jne (or jg to jle, etc.)"],
            ),
            _step(
                "feedback",
                "Changing the condition code flips the branch semantics.",
            ),
            _step(
                "challenge",
                "The original check was 'jne deny'. It has been patched to "
                "'je deny', so a WRONG password (RAX = 0) is granted. Verify "
                "the bypass lands RBX = 1.",
                program=read_asm("module6/lesson4_crackmes/challenge.asm"),
                expected={"registers": {"rbx": 1}},
            ),
            _step(
                "reflection",
                "Why is automatic verification (re-running the patched binary "
                "and checking behavior) essential when patching, rather than "
                "just checking the changed bytes?",
            ),
        ],
    )


def module6() -> Module:
    return Module(
        id="module6",
        title="Reverse Engineering",
        order=6,
        lessons=[
            lesson_elf(),
            lesson_sections_symbols(),
            lesson_cfg(),
            lesson_crackmes(),
        ],
    )
