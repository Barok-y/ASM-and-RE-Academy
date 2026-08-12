// Lesson: Loops
// Sum the integers from 10 down to 1 into RBX (1+2+...+10 = 55).
        mov rbx, 0
        mov rcx, 10
loop_start:
        add rbx, rcx
        sub rcx, 1
        jne loop_start

        mov rax, 60
        mov rdi, 0
        syscall
