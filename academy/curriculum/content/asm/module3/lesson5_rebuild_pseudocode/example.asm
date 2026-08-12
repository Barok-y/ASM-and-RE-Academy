// Lesson: Rebuild Pseudocode
// Compute the max of RAX and RBX into RCX (then copy to R8).
        mov rax, 6
        mov rbx, 2
        cmp rax, rbx
        jle smaller
        mov rcx, rax
        jmp done
smaller:
        mov rcx, rbx
done:
        mov r8, rcx

        mov rax, 60
        mov rdi, 0
        syscall
