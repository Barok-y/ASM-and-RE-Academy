// Lesson: Format String / Buffer Offset Leak
// A format-style vuln lets the attacker choose a byte offset into a region
// that holds the flag at [0x600010]. The flag is "ASM{fl4g_1s_fun_4_u}",
// so flag[12] is 'f' (0x66). The vuln reads one attacker-chosen offset byte,
// then leaks the flag byte at [base + offset] into R8.
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