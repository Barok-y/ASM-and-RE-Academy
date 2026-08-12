// Lesson: CMP and TEST
// Compare two equal values and test RAX against itself, watching flags.
        mov rax, 5
        mov rbx, 5
        cmp rax, rbx
        test rax, rax

        mov rax, 60
        mov rdi, 0
        syscall
