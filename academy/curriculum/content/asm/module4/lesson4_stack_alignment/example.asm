// Lesson: Stack Alignment and Prologues
// Keep RSP 16-byte aligned at the CALL by padding before it.
        sub rsp, 8
        mov rdi, 5
        call align_me
        add rsp, 8
        mov r8, rax

        mov rax, 60
        mov rdi, 0
        syscall

align_me:
        mov rax, rdi
        add rax, 1
        ret
