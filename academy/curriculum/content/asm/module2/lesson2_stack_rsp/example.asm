// Lesson: The Stack and RSP
// Save RAX on the stack, disturb RAX, then pop the old value into RBX.
        mov rax, 7
        push rax
        mov rax, 99
        pop rbx

        mov rax, 60
        mov rdi, 0
        syscall
