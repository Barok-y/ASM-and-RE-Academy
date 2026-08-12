// Lesson: Syscalls
// Write "Hi\n" to stdout (fd 1) with the write syscall.
        mov rbx, 0x600000
        mov byte ptr [rbx], 72
        mov byte ptr [rbx+1], 105
        mov byte ptr [rbx+2], 10
        mov rax, 1
        mov rdi, 1
        mov rsi, 0x600000
        mov rdx, 3
        syscall

        mov rax, 60
        mov rdi, 0
        syscall
