// Lesson: Heap Overflow
// An unbounded read pours user input into a tiny 4-byte heap buffer at
// 0x700000. The safe_var flag at 0x700004 (initialized "bico") sits right
// after it. 8 bytes of input overflow into safe_var: "picopico" makes
// safe_var read "pico", so its first byte 'p' (0x70) lands in R8.
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