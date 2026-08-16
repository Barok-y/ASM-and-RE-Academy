from __future__ import annotations

from ..models import Lesson, LessonStep, Module
from ._asm import read_asm


def _step(kind: str, content: str = "", **kwargs) -> LessonStep:
    return LessonStep(kind=kind, content=content, **kwargs)


def lesson_xor_decode() -> Lesson:
    return Lesson(
        id="module8.lesson1",
        module="module8",
        title="XOR Obfuscation",
        order=1,
        steps=[
            _step(
                "concept",
                "A common crackme trick is to hide the password so it does not "
                "appear as a plain string in the binary: the author XORs each "
                "character with a single key byte and ships only the ciphertext "
                "plus a tiny decode routine that restores the string in memory "
                "right before the strcmp. A real crackme we reversed did exactly "
                "this - check_username and check_password each ran a decode() "
                "loop that XORed a stack buffer with the key 0x5a.",
            ),
            _step(
                "intuition",
                "XOR with a constant key is symmetric: xor(ciphertext, key) "
                "restores the plaintext, so the 'protection' only hides the "
                "string from a casual strings dump - not from anyone who reads "
                "the routine and inverts it.",
            ),
            _step(
                "analogy",
                "A coded locker note where every letter is shifted by the same "
                "secret offset. Anyone who knows the offset can read it - and "
                "reading the note tells you the offset was just a single value.",
            ),
            _step(
                "visualization",
                "ciphertext bytes:  0x28 0x3f 0x2c 0x6b 0x68 0x69 0x7b\n"
                "          xor 0x5a\n"
                "plaintext bytes:   0x72 0x65 0x76 0x31 0x32 0x33 0x21\n"
                "                  = 'r' 'e' 'v' '1' '2' '3' '!'",
            ),
            _step(
                "example",
                "decode() XORs three bytes with the key 0x5a and reads back the "
                "first restored byte.",
                high_level="for (i = 0; i < 3; i++) buf[i] ^= 0x5a;",
                program=read_asm("module8/lesson1_xor_decode/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step the loop: each MOV loads a ciphertext byte, XOR applies the "
                "key, and the byte is written back - 0x2c becomes 0x76 ('v'), "
                "0x6b becomes 0x31, 0x68 becomes 0x32.",
                program=read_asm("module8/lesson1_xor_decode/example.asm"),
            ),
            _step(
                "prediction",
                "Press R to run the example: the loop XORs 0x2c, 0x6b, 0x68 with the "
                "key 0x5a. What hex value ends up in R8 (the first restored byte)?",
                program=read_asm("module8/lesson1_xor_decode/example.asm"),
                options=["0x76", "0x5a", "0x2c", "0x7a"],
                answer=0,
                feedback={
                    1: "0x5a is the KEY, not a decoded byte.",
                    2: "0x2c is the ciphertext byte before the XOR.",
                    3: "0x7a would need a different key; 0x2c ^ 0x5a = 0x76.",
                },
                hint="Press R - 0x2c ^ 0x5a = 0x76, the ASCII 'v'.",
            ),
            _step(
                "response",
                "Run the example (press R): it decodes the first three bytes of the "
                "crackme's password ('v','1','2'). Type the hex value (with 0x) of the "
                "first restored byte that lands in R8.",
                program=read_asm("module8/lesson1_xor_decode/example.asm"),
                keywords=["0x76"],
                model_answer="0x76 - 0x2c ^ 0x5a = 0x76, the ASCII 'v'; XOR with a "
                    "constant key is its own inverse, so decoding is just re-XORing.",
                hint="After R, R8 holds 0x2c ^ 0x5a.",
            ),
            _step(
                "feedback",
                "R8 = 0x76. Repeating the decode over all seven ciphertext bytes "
                "reveals the full password 'rev123!'. Because the key is a single "
                "byte, one known plaintext byte would have been enough to recover "
                "it - single-byte XOR is quick to spot and trivial to invert.",
            ),
            _step(
                "challenge",
                "Decode the crackme's full 7-byte XOR password (ciphertext 0x28 0x3f "
                "0x2c 0x6b 0x68 0x69 0x7b, key 0x5a) and leave the FIRST decoded byte "
                "in R8.",
                program=read_asm("module8/lesson1_xor_decode/challenge.asm"),
                expected={"registers": {"r8": 0x72}},
            ),
            _step(
                "reflection",
                "If the key were two bytes (XORing every other byte) instead of one, "
                "how would the decode routine and your reversing approach change?",
            ),
        ],
    )


def lesson_nop_patch() -> Lesson:
    return Lesson(
        id="module8.lesson2",
        module="module8",
        title="Patching a Check with NOPs",
        order=2,
        steps=[
            _step(
                "concept",
                "Patching a crackme means changing its bytes so the password check "
                "behaves differently. Besides flipping the jump condition (JE -> "
                "JNE), the classic trick is to NOP-pad the conditional jump: "
                "overwriting the 2-byte jcc with two 0x90 bytes makes control fall "
                "through both outcomes, so the branch is gone entirely. A real "
                "crackme we reversed was already patched this way - its main "
                "function had 'test eax, eax' followed by two NOPs where a "
                "conditional jump used to be, so it printed Access Granted for "
                "every input.",
            ),
            _step(
                "intuition",
                "A conditional jump is a fork in the road. NOP-padding deletes the "
                "fork and leaves a single straight road - both 'outcomes' collapse "
                "into the fall-through path, which is the one you want.",
            ),
            _step(
                "analogy",
                "A turnstile that only opens for a valid ticket. Instead of breaking "
                "the lock, a patcher welds the mechanism so the gate always stands "
                "open - the ticket check is still there, it just can't stop you.",
            ),
            _step(
                "visualization",
                "original:  test eax, eax\n"
                "           jne  denied   ; 75 1f\n"
                "patched:   test eax, eax\n"
                "           nop            ; 90\n"
                "           nop            ; 90\n"
                "           ; falls into the 'granted' path no matter what",
            ),
            _step(
                "example",
                "The patched check: a wrong password (RAX = 0) still reaches the "
                "grant block because the two NOPs replaced the branch that used to "
                "skip it.",
                high_level="if (password == 1337) grant(); // je patched to nop nop",
                program=read_asm("module8/lesson2_nop_patch/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: CMP sets flags, the two NOPs change nothing, and control "
                "simply falls into the block that writes 1 to R8 - the 'wrong "
                "password' case grants access exactly like the right one.",
                program=read_asm("module8/lesson2_nop_patch/example.asm"),
            ),
            _step(
                "prediction",
                "Press R to run the patched example: RAX = 0 is a WRONG password and "
                "the old 'je grant' is now two NOPs. Read the final panel — what "
                "value ends up in R8?",
                program=read_asm("module8/lesson2_nop_patch/example.asm"),
                options=["1", "0", "1337", "2"],
                answer=0,
                feedback={
                    1: "0 would mean denied; the NOPs removed the branch that could deny.",
                    2: "1337 is the expected password, never stored in a register.",
                    3: "2 is the number of NOP bytes, not a result value.",
                },
                hint="Press R - with the branch gone, the grant block always runs.",
            ),
            _step(
                "response",
                "Run the patched example (press R): the wrong password RAX = 0 falls "
                "through the two NOPs into the grant block. Type the value that ends "
                "up in R8.",
                program=read_asm("module8/lesson2_nop_patch/example.asm"),
                keywords=["1"],
                model_answer="1 - the conditional jump was replaced by two NOPs, so "
                    "control cannot branch away; the grant block writes 1 to R8 for "
                    "any password.",
                hint="After R, R8 shows the grant flag: 1.",
            ),
            _step(
                "feedback",
                "R8 = 1. The two 0x90 bytes removed the only decision point in the "
                "check. Note the pattern to look for when reversing patched "
                "binaries: a test/cmp immediately followed by NOPs where a short or "
                "near jcc should sit, with the 'denied' message becoming dead code.",
            ),
            _step(
                "challenge",
                "Verify the patched crackme: the 'jne denied' that used to follow "
                "'test rax, rax' has been overwritten with two NOPs. With a wrong "
                "password (RAX = 0) the grant block must still run, leaving R8 = 1.",
                program=read_asm("module8/lesson2_nop_patch/challenge.asm"),
                expected={"registers": {"r8": 1}},
            ),
            _step(
                "reflection",
                "Why is NOP-padding a conditional jump more robust than just "
                "inverting its condition when the goal is 'always grant'?",
            ),
        ],
    )


def lesson_immediate_strings() -> Lesson:
    return Lesson(
        id="module8.lesson3",
        module="module8",
        title="Recovering Strings from Immediates",
        order=3,
        steps=[
            _step(
                "concept",
                "Compilers often load short ASCII constants as single 64-bit "
                "immediates ('movabs rax, imm') instead of storing them in a data "
                "section. The characters appear REVERSED inside the constant "
                "because x86 is little-endian: the first character is the "
                "low-order byte of the immediate. A picoCTF-style binary we reversed "
                "hid its flag this way - 'movabs' instructions embedded "
                "'ASM{3lf_r3v3r5ing_succe55ful_2f0131a4}' directly in main.",
            ),
            _step(
                "intuition",
                "An immediate is just bytes packed into a number. Read the number "
                "back as little-endian bytes and you get the string - no "
                "disassembly of data sections needed.",
            ),
            _step(
                "analogy",
                "Writing the word 'TEXT' on a receipt from right to left so it "
                "reads left to right when the cashier flips the slip. The "
                "immediate is the receipt; flipping the byte order is flipping "
                "the slip.",
            ),
            _step(
                "visualization",
                "movabs rax, 0x5f666c337b4d5341\n"
                "memory bytes (little-endian):\n"
                "  41 53 4d 7b 33 6c 66 5f\n"
                "  'A' 'S' 'M' '{' '3' 'l' 'f' '_'\n"
                "=> 'ASM{3lf_'",
            ),
            _step(
                "example",
                "The 'ASM{3lf_' chunk is loaded as one immediate and its first byte "
                "is read back.",
                high_level="const char s[8] = \"ASM{3lf_\"; char c = s[0];",
                program=read_asm("module8/lesson3_immediate_strings/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: the 64-bit immediate lands in memory, and MOVZX reads the "
                "byte at index 0 - the low-order byte 0x41, which is 'A'.",
                program=read_asm("module8/lesson3_immediate_strings/example.asm"),
            ),
            _step(
                "prediction",
                "Press R to run the example: 'ASM{3lf_' was stored as the immediate "
                "0x5f666c337b4d5341. What hex byte ends up in R8 (the character at "
                "index 0)?",
                program=read_asm("module8/lesson3_immediate_strings/example.asm"),
                options=["0x41", "0x53", "0x4d", "0x5f"],
                answer=0,
                feedback={
                    1: "0x53 is index 1 ('S'), the second character.",
                    2: "0x5f is index 7 ('_'), the highest-order byte.",
                    3: "0x4d is index 2 ('M'), the third character.",
                },
                hint="Press R - the low-order byte of the immediate is the first character.",
            ),
            _step(
                "response",
                "Run the example (press R): the chunk 'ASM{3lf_' is stored as one "
                "immediate, and the byte at index 0 is copied into R8. Type the hex "
                "value (with 0x) in R8.",
                program=read_asm("module8/lesson3_immediate_strings/example.asm"),
                keywords=["0x41"],
                model_answer="0x41 - 'A' is the low-order byte of 0x5f666c337b4d5341; "
                    "reading the immediate as little-endian bytes spells 'ASM{3lf_'.",
                hint="After R, R8 holds the first ASCII byte of the chunk.",
            ),
            _step(
                "feedback",
                "R8 = 0x41. One immediate is an 8-byte window of the flag: "
                "0x5f666c337b4d5341, 0x6e69357233763372, ... read back byte-by-byte "
                "recover the whole string. When a binary has no .rodata strings, "
                "scan the immediates - flags often hide there.",
            ),
            _step(
                "challenge",
                "The flag chunk 'r3v3r5in' was stored as the immediate "
                "0x6e69357233763372. Read the bytes back little-endian and leave "
                "the character at index 4 in R8.",
                program=read_asm("module8/lesson3_immediate_strings/challenge.asm"),
                expected={"registers": {"r8": 0x72}},
            ),
            _step(
                "reflection",
                "Why does reading an immediate as little-endian bytes recover the "
                "string, and how would the byte order differ on a big-endian "
                "architecture?",
            ),
        ],
    )


def lesson_byte_transform() -> Lesson:
    return Lesson(
        id="module8.lesson4",
        module="module8",
        title="Byte Transform Loops",
        order=4,
        steps=[
            _step(
                "concept",
                "Some challenges transform the flag byte-by-byte and ship the "
                "transformed file, expecting you to invert the loop. The picoCTF "
                "'rev' binary read flag.txt and rewrote it as rev_this: characters "
                "at indexes 8..22 gained 5 at even indexes and lost 2 at odd "
                "indexes, and the boundary characters were copied unchanged. "
                "Recovering the flag means reading that loop and writing its "
                "inverse.",
            ),
            _step(
                "intuition",
                "A transform loop is just a per-character arithmetic rule. Write "
                "the rule down, flip every + to - and - to +, and the same loop "
                "now undoes itself.",
            ),
            _step(
                "analogy",
                "A cipher that adds 5 to every even shelf and removes 2 from every "
                "odd shelf. To restock the shelves you run the same tour of the "
                "aisles but do the opposite at each stop.",
            ),
            _step(
                "visualization",
                "forward (rev):   index even -> byte + 5\n"
                "                 index odd  -> byte - 2\n"
                "inverse (you):   index even -> byte - 5\n"
                "                 index odd  -> byte + 2\n"
                "'w'(0x77) at index 8 --forward(+5)--> '|'(0x7c)\n"
                "'|'(0x7c) at index 8 --inverse(-5)--> 'w'(0x77)",
            ),
            _step(
                "example",
                "The forward transform from the 'rev' binary: index 8 is even, so "
                "the byte is increased by 5.",
                high_level="if (i >= 8 && i <= 22) buf[i] += (i % 2) ? -2 : 5;",
                program=read_asm("module8/lesson4_byte_transform/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: the index 8 test sets the odd/even decision, the even path "
                "adds 5, and 'w' (0x77) becomes 0x7c ('|') - exactly the byte that "
                "ends up in rev_this.",
                program=read_asm("module8/lesson4_byte_transform/example.asm"),
            ),
            _step(
                "prediction",
                "Press R to run the example: index 8 is even so the forward "
                "transform adds 5 to 'w' (0x77). What hex byte ends up in R8?",
                program=read_asm("module8/lesson4_byte_transform/example.asm"),
                options=["0x7c", "0x77", "0x72", "0x75"],
                answer=0,
                feedback={
                    1: "0x77 is the ORIGINAL byte before the +5.",
                    2: "0x72 would be a -5; the forward transform adds.",
                    3: "0x75 would be -2, the odd-index transform.",
                },
                hint="Press R - 0x77 + 5 = 0x7c.",
            ),
            _step(
                "response",
                "Run the inverse transform (press R): rev_this[8] = '|' (0x7c) at the "
                "even index 8, so the inverse subtracts 5. Type the hex value (with "
                "0x) that ends up in R8 - the recovered original byte.",
                program=read_asm("module8/lesson4_byte_transform/challenge.asm"),
                keywords=["0x77"],
                model_answer="0x77 - the inverse of the even-index +5 is -5, so "
                    "0x7c - 5 = 0x77, the original 'w'.",
                hint="After R, R8 shows the byte recovered from rev_this.",
            ),
            _step(
                "feedback",
                "R8 = 0x77. Applying the inverse over the whole 8..22 range turns "
                "rev_this back into the original flag. The lesson: when a binary "
                "produces one file from another with a visible loop, you rarely "
                "need to fully understand it - you need to invert it.",
            ),
            _step(
                "challenge",
                "rev_this[8] = 0x7c at the even index 8. Apply the INVERSE transform "
                "(-5 for even indexes, +2 for odd) to recover the original byte and "
                "leave it in R8.",
                program=read_asm("module8/lesson4_byte_transform/challenge.asm"),
                expected={"registers": {"r8": 0x77}},
            ),
            _step(
                "reflection",
                "The transform only touches indexes 8..22 while the flag's "
                "opening chunk and closing brace pass through unchanged. Why does the "
                "loop's index range itself leak useful structure about the flag?",
            ),
        ],
    )


def lesson_vm_bytecode() -> Lesson:
    return Lesson(
        id="module8.lesson5",
        module="module8",
        title="VM Bytecode Obfuscation",
        order=5,
        steps=[
            _step(
                "concept",
                "The strongest anti-analysis trick in this lab is a custom "
                "interpreter: instead of comparing the password directly, the "
                "binary embeds bytecode and a small VM that walks it, mutating an "
                "accumulator. The ADWA 'oracle' challenge does exactly this - its "
                "opcodes are 'D' (rotate left 3), 'U' (multiply by 7), '2' (add "
                "0x41424344) and '!' (XOR with each input byte), and the VM "
                "finally compares the accumulator to a constant. Reversing the "
                "VM means decoding each opcode and running the program yourself.",
            ),
            _step(
                "intuition",
                "A VM hides the algorithm behind an interpreter loop. Once you "
                "decode the opcode table, the 'program' is just arithmetic again - "
                "you can emulate it by hand, in a spreadsheet, or in your head.",
            ),
            _step(
                "analogy",
                "A vending machine that reads a card with holes punched in it. You "
                "do not need the machine's manual - punch a card of your own, "
                "watch each hole's effect, and soon you can predict the outcome "
                "for any card.",
            ),
            _step(
                "visualization",
                "bytecode:  '2'  'D'  'U'  0\n"
                "acc start:      0x1337\n"
                "'2': acc += 0x41424344\n"
                "'D': acc = rol(acc, 3)\n"
                "'U': acc *= 7\n"
                "final acc:      0xe4682eae8   <- the oracle's check constant",
            ),
            _step(
                "example",
                "A toy VM that interprets 'U' and 'D' against an accumulator "
                "initialized to 0x1337 - the same start value the oracle uses.",
                high_level="acc = 0x1337; acc *= 7; acc = rol(acc, 3);",
                program=read_asm("module8/lesson5_vm_bytecode/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: the interpreter reads a bytecode byte, dispatches on it, and "
                "updates the accumulator - IMUL for 'U', ROL for 'D' - until the "
                "0 halt byte ends the program with acc = 0x43408 in R8.",
                program=read_asm("module8/lesson5_vm_bytecode/example.asm"),
            ),
            _step(
                "prediction",
                "Press R to run the example VM: the accumulator starts at 0x1337 and "
                "the first opcode is 'U' (multiply by 7). What hex value does acc "
                "hold right after that single op, before the 'D' rotate?",
                program=read_asm("module8/lesson5_vm_bytecode/example.asm"),
                options=["0x8681", "0x1337", "0x99b8", "0x43408"],
                answer=0,
                feedback={
                    1: "0x1337 is the accumulator BEFORE any opcode runs.",
                    2: "0x99b8 is 0x1337 rotated left by 3, not multiplied.",
                    3: "0x43408 is the final value after both 'U' and 'D'.",
                },
                hint="Press R - 0x1337 * 7 = 0x8681.",
            ),
            _step(
                "response",
                "Run the example VM (press R): bytecode 'U','D',0 drives acc from "
                "0x1337 to its final value. Type the final hex value (with 0x) that "
                "lands in R8.",
                program=read_asm("module8/lesson5_vm_bytecode/example.asm"),
                keywords=["0x43408"],
                model_answer="0x43408 - 0x1337 * 7 = 0x8681, then rol 3 moves the "
                    "three low bits into the high positions: 0x43408.",
                hint="After R, R8 shows the accumulator after 'U' then 'D'.",
            ),
            _step(
                "feedback",
                "R8 = 0x43408. Now the payoff: running the extended opcode set over "
                "'2','D','U' from 0x1337 produces 0xe4682eae8 - the exact constant "
                "the real oracle compares against. The oracle's flag bytecode is "
                "literally the instruction sequence that drives its accumulator to "
                "that value. One VM, decoded, is just arithmetic.",
            ),
            _step(
                "challenge",
                "Extend the toy VM with the oracle's remaining op '2' (add "
                "0x41424344). Run bytecode '2','D','U',0 from acc = 0x1337 and "
                "leave the final accumulator value in R8.",
                program=read_asm("module8/lesson5_vm_bytecode/challenge.asm"),
                expected={"registers": {"r8": 0xE4682EAE8}},
            ),
            _step(
                "reflection",
                "The oracle also had a '!' opcode that XORs the accumulator with "
                "each character of your input. How would you use a known or "
                "guessed prefix ('ASM{') to recover the rest of a VM-protected "
                "flag?",
            ),
        ],
    )


def module8() -> Module:
    return Module(
        id="module8",
        title="Crackme Lab",
        order=8,
        lessons=[
            lesson_xor_decode(),
            lesson_nop_patch(),
            lesson_immediate_strings(),
            lesson_byte_transform(),
            lesson_vm_bytecode(),
        ],
    )
