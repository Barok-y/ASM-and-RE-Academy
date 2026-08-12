// Lesson: Breakpoints
// Pause on 'mov rbx, rax' after the second ADD: at that point RAX is 8, so
// RBX takes the value 8.
        mov rax, 5
        add rax, 3
        mov rbx, rax

        mov rax, 60
        mov rdi, 0
        syscall
