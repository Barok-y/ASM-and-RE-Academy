// Lesson: System V Calling Convention
// Pass arguments in RDI/RSI and read the result from RAX.
        mov rdi, 4
        mov rsi, 3
        call add_args
        mov r8, rax

        mov rax, 60
        mov rdi, 0
        syscall

add_args:
        mov rax, rdi
        add rax, rsi
        ret
