// Lesson: Rebuild Pseudocode
// max(RAX, RBX) must end up in RBX. RAX = 3, RBX = 7.
        mov rax, 3
        mov rbx, 7
        cmp rax, rbx
        jge rax_bigger
        jmp done
rax_bigger:
        mov rbx, rax
done:

        mov rax, 60
        mov rdi, 0
        syscall
