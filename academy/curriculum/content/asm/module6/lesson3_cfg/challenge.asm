// Lesson: Control Flow Graphs
// CFG with two outcomes: if RAX > 0 double it, else zero it. RAX = 6, so the
// result is 12 in RBX.
        mov rax, 6
        cmp rax, 0
        jle zero
        shl rax, 1
        mov rbx, rax
        jmp done
zero:
        mov rbx, 0
done:

        mov rax, 60
        mov rdi, 0
        syscall
