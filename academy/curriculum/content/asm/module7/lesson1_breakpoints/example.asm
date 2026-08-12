// Lesson: Breakpoints
// A straight-line program// a breakpoint on 'mov rbx, rax' would pause with
// RAX = 8.
        mov rax, 5
        add rax, 3
        mov rbx, rax

        mov rax, 60
        mov rdi, 0
        syscall
