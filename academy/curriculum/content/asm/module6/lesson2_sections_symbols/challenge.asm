// Lesson: Sections and Symbols
// .bss starts zeroed. Write 3 into a bss slot, read the neighboring
// zero-initialized slot, add 5, and keep the sum in RBX (3 + 0 + 5 = 8).
        mov rbx, 0x610000
        mov qword ptr [rbx], 3
        mov rcx, [rbx]
        add rcx, 5
        mov rbx, rcx

        mov rax, 60
        mov rdi, 0
        syscall
