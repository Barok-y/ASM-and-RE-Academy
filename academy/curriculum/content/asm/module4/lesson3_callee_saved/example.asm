// Lesson: Callee-Saved vs Caller-Saved
// The callee must preserve RBX (callee-saved) even though it uses it.
        mov rbx, 42
        call clobber
        mov r8, rbx

        mov rax, 60
        mov rdi, 0
        syscall

clobber:
        push rbx
        mov rbx, 999
        pop rbx
        ret
