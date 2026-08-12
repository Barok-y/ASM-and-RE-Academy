// Lesson: Shifts and Bit Tricks
// Multiply RAX by 10 without MUL: (x << 3) + (x << 1) for x = 7.
        mov rax, 7
        mov rbx, rax
        shl rbx, 3        // 7 * 8 = 56
        mov rcx, rax
        shl rcx, 1        // 7 * 2 = 14
        add rbx, rcx      // 56 + 14 = 70

        mov rax, 60
        mov rdi, 0
        syscall
