// Lesson: Format String / Buffer Offset Leak - challenge
// The flag sits at [0x600010] and flag[12] is 'f' (0x66). Choose the offset
// byte (input) that leaks flag[12] into R8: feed b"\x0c" so r8 = 0x66.
        mov rbx, 0x600000
        mov byte ptr [rbx+12], 0x66          // flag[12] = 'f'
        mov rsi, 0x600100
        mov byte ptr [rsi], 0
        mov rax, 0
        mov rdi, 0
        mov rdx, 1
        syscall                              // read attacker offset byte
        movzx r8, byte ptr [rsi]
        movzx r9, byte ptr [rbx+r8]          // leak flag byte at offset
        mov r8, r9
        mov rax, 60
        mov rdi, 0
        syscall