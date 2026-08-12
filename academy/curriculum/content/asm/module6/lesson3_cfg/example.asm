// Lesson: Control Flow Graphs
// Two basic blocks: compare, then either swap or skip (a tiny CFG with 3
// nodes). RAX = 5, RBX = 10.
        mov rax, 5
        mov rbx, 10
        cmp rax, rbx
        jg swap
        jmp done
swap:
        mov rcx, rax
        mov rax, rbx
        mov rbx, rcx
done:
        mov r8, rax

        mov rax, 60
        mov rdi, 0
        syscall
