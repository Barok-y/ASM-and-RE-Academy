// Lesson: Bitwise Operations
// Clear bit 2 (0x04) from 0xFF with AND, then toggle bit 0 (0x01) with XOR.
        mov rax, 0xFF
        and rax, 0xFB        // 11111111 & 11111011 -> 11111011 (0xFB)
        xor rax, 0x01        // 11111011 ^ 00000001 -> 11111010 (0xFA)
        mov rbx, rax

        mov rax, 60
        mov rdi, 0
        syscall
