// Lesson: Process Memory Layout
// Store a byte in the data segment and read it back into RAX.
        mov rbx, 0x600000
        mov byte ptr [rbx], 42
        movzx rax, byte ptr [rbx]

        mov rax, 60
        mov rdi, 0
        syscall
