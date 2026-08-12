// Lesson: Sections and Symbols
// The .bss segment (0x610000) starts zeroed// write a global into it and read
// it back.
        mov rbx, 0x610000
        mov byte ptr [rbx], 7
        movzx rax, byte ptr [rbx]
        mov r8, rax

        mov rax, 60
        mov rdi, 0
        syscall
