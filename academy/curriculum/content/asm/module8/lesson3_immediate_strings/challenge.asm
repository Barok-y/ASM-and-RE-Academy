// Lesson: Recovering Strings from Immediates
// The flag chunk 'r3v3r5in' was stored as the immediate 0x6e69357233763372.
// Little-endian memory bytes: 72 33 76 33 72 35 69 6e = 'r3v3r5in'.
// Recover the byte at index 4 - the 'r' (0x72) - into R8.
        mov rbx, 0x600000
        mov rax, 0x6e69357233763372
        mov qword ptr [rbx], rax
        movzx r8, byte ptr [rbx+4]      // index 4 -> 'r' (0x72)
        mov rax, 60
        mov rdi, 0
        syscall
