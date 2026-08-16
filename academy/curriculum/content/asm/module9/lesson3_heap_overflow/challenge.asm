// Lesson: Heap Overflow - challenge
// Overflow the 4-byte input_data buffer at 0x700000 so that 8 bytes of input
// ("picopico") overwrite safe_var at 0x700004 and its first byte becomes 'p'
// (0x70). Verify by feeding b"picopico" and checking R8.
        mov rbx, 0x700000
        mov byte ptr [rbx+4], 'b'
        mov byte ptr [rbx+5], 'i'
        mov byte ptr [rbx+6], 'c'
        mov byte ptr [rbx+7], 'o'
        mov rax, 0
        mov rdi, 0
        mov rsi, 0x700000
        mov rdx, 128
        syscall                              // read into input_data (overflows)
        mov rcx, 0x700004
        movzx r8, byte ptr [rcx]             // safe_var's first byte
        mov rax, 60
        mov rdi, 0
        syscall