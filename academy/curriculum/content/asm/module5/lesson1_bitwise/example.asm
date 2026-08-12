// Lesson: Bitwise Operations
// Mask with AND, set bits with OR, toggle bits with XOR.
        mov rax, 0xAB
        and rax, 0xF0        // keep high nibble: 0xA0
        or rax, 0x05         // set low nibble to 5: 0xA5
        xor rax, 0x0F        // toggle low nibble: 0xAA
        mov r8, rax

        mov rax, 60
        mov rdi, 0
        syscall
