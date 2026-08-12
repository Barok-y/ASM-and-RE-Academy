// Lesson: Loops
// Sum the integers from 5 down to 1 into RAX.
        mov rax, 0
        mov rcx, 5
loop_start:
        add rax, rcx
        sub rcx, 1
        jne loop_start
        mov r8, rax

        mov rax, 60
        mov rdi, 0
        syscall
