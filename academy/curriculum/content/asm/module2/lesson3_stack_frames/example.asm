// Lesson: Stack Frames and RBP
// Reserve a 16-byte local area and use it to move values around.
        sub rsp, 16
        mov [rsp], rax
        mov [rsp+8], rbx
        mov rcx, [rsp]
        mov rdx, [rsp+8]
        add rsp, 16

        mov rax, 60
        mov rdi, 0
        syscall
