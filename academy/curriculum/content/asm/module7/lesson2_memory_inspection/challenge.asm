// Lesson: Memory Inspection
// Write 0x10, 0x20, 0x30 to three consecutive bytes, then load the SECOND
// byte (0x20) into RBX.
        mov rbx, 0x600000
        mov byte ptr [rbx], 0x10
        mov byte ptr [rbx+1], 0x20
        mov byte ptr [rbx+2], 0x30
        movzx rbx, byte ptr [rbx+1]

        mov rax, 60
        mov rdi, 0
        syscall
