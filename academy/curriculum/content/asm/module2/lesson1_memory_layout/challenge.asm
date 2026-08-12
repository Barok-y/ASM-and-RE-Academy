// Lesson: Process Memory Layout
// Store the bytes 7 and 9 in the data segment and leave their sum in RBX.
        mov rbx, 0x600000
        mov byte ptr [rbx], 7
        mov byte ptr [rbx+1], 9
        movzx rax, byte ptr [rbx]
        movzx rcx, byte ptr [rbx+1]
        add rax, rcx
        mov rbx, rax

        mov rax, 60
        mov rdi, 0
        syscall
