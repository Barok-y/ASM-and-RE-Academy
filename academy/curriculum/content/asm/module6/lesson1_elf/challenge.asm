// Lesson: ELF Structure
// This 'function' computes rdi*3 + 2. Given RDI = 4, the result is 14// keep
// it in R8.
        mov rdi, 4
        mov rax, rdi
        shl rax, 1
        add rax, rdi
        add rax, 2
        mov r8, rax

        mov rax, 60
        mov rdi, 0
        syscall
