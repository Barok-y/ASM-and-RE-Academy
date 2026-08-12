// Lesson: CMP and TEST
// Compare two equal values so the zero flag is set by CMP.
        mov rax, 9
        mov rbx, 9
        cmp rax, rbx

        mov rax, 60
        mov rdi, 0
        syscall
