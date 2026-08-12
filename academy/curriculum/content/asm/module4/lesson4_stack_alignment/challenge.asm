// Lesson: Stack Alignment and Prologues
// Build a compliant frame: align the stack, pass 3 in RDI, call a function
// returning rdi*7, and leave the result in RBX.
        sub rsp, 8
        mov rdi, 3
        call times_seven
        add rsp, 8
        mov rbx, rax

        mov rax, 60
        mov rdi, 0
        syscall

times_seven:
        mov rax, rdi
        imul rax, 7
        ret
