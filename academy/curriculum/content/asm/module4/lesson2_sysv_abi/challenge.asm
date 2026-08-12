// Lesson: System V Calling Convention
// Pass 6 and 4 in RDI/RSI, call a function returning rdi*rsi+1, and keep the
// result in RBX.
        mov rdi, 6
        mov rsi, 4
        call product_plus_one
        mov rbx, rax

        mov rax, 60
        mov rdi, 0
        syscall

product_plus_one:
        mov rax, rdi
        imul rax, rsi
        add rax, 1
        ret
