// Lesson: The Stack and RSP
// Preserve RAX across a modification using the stack// the original value
// must end up in RBX.
        mov rax, 5
        push rax
        mov rax, 0
        pop rbx

        mov rax, 60
        mov rdi, 0
        syscall
