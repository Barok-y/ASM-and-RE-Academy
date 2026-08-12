// Lesson: Conditional Jumps
// If RAX >= 10, RBX = 100// otherwise RBX = 50. RAX starts at 10.
        mov rax, 10
        cmp rax, 10
        jge big
        mov rbx, 50
        jmp done
big:
        mov rbx, 100
done:

        mov rax, 60
        mov rdi, 0
        syscall
