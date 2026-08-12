// Lesson: Conditional Jumps
// If RAX >= 5 take the else branch, otherwise take the then branch.
        mov rax, 3
        cmp rax, 5
        jge else_branch
        mov rbx, 1
        jmp done
else_branch:
        mov rbx, 2
done:
        mov r8, rbx

        mov rax, 60
        mov rdi, 0
        syscall
