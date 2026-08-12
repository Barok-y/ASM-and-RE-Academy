// Lesson: Runtime Analysis
// A loop whose body executes 4 times// leave the iteration count in RBX.
        mov rcx, 4
        mov rbx, 0
loop_start:
        inc rbx
        sub rcx, 1
        jne loop_start

        mov rax, 60
        mov rdi, 0
        syscall
