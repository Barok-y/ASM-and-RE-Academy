// Lesson: Stack Frames and RBP
// Reserve 24 bytes of locals, store 1/2/3 at offsets 0/8/16, then load them
// back and sum them into RBX.
        sub rsp, 24
        mov qword ptr [rsp], 1
        mov qword ptr [rsp+8], 2
        mov qword ptr [rsp+16], 3
        mov rcx, [rsp]
        mov rdx, [rsp+8]
        mov rsi, [rsp+16]
        add rcx, rdx
        add rcx, rsi
        mov rbx, rcx
        add rsp, 24

        mov rax, 60
        mov rdi, 0
        syscall
