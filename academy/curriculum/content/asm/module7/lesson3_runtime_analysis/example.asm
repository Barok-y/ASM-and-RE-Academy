// Lesson: Runtime Analysis
// A small calculation to trace: 2 * 3 + 1.
        mov rax, 2
        mov rbx, 3
        imul rax, rbx
        add rax, 1

        mov rax, 60
        mov rdi, 0
        syscall
