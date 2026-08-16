// Lesson: PIE Base Leak
// A PIE binary loads at a random base. The vuln leaks a pointer into the
// binary - here the address of win(), which is base + 0x80 - and a solver
// subtracts the known offset 0x80 to recover the base, then re-derives win()
// as base + 0x80. With text base 0x400000 the leaked pointer is 0x400080.
vuln:
        mov rbx, 0x600000
        mov rax, 0
        mov rdi, 0
        mov rsi, rbx
        mov rdx, 8
        syscall                              // read input (may be empty)
        mov r8, win                          // leaked pointer offset: 0x80
        add r8, 0x400000                     // base + offset = runtime address
        mov rax, 60
        mov rdi, 0
        syscall
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
win:
        mov byte ptr [rbx], 'w'
        mov byte ptr [rbx+1], 'i'
        mov byte ptr [rbx+2], 'n'
        mov rax, 60
        mov rdi, 0
        syscall