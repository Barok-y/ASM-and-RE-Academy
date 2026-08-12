// Lesson: Heap and Dynamic Memory
// Write a value into the heap segment and read it straight back.
        mov rax, 0x1111111122222222
        mov rbx, 0x700000
        mov qword ptr [rbx], rax
        mov rcx, [rbx]

        mov rax, 60
        mov rdi, 0
        syscall
