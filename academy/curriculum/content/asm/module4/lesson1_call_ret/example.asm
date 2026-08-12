// Lesson: CALL and RET
// Call a function that adds 10 to RAX and returns.
        mov rax, 5
        call myfunc
        mov r8, rax

        mov rax, 60
        mov rdi, 0
        syscall

myfunc:
        add rax, 10
        ret
