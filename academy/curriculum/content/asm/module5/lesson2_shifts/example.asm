// Lesson: Shifts and Bit Tricks
// Shift left to multiply by 8, shift right to divide by 4.
        mov rax, 3
        shl rax, 3        // 3 * 8 = 24
        shr rax, 2        // 24 / 4 = 6
        mov r8, rax

        mov rax, 60
        mov rdi, 0
        syscall
