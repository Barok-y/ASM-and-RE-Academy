// Lesson: Heap and Dynamic Memory
// Treat 0x700000 as a 16-byte heap block: write 0xABCD into the first slot
// and 0x1234 into the second, then leave the second slot's value in RBX.
        mov rbx, 0x700000
        mov qword ptr [rbx], 0xABCD
        mov qword ptr [rbx+8], 0x1234
        mov rbx, [rbx+8]

        mov rax, 60
        mov rdi, 0
        syscall
