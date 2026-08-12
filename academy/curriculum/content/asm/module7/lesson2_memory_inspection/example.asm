// Lesson: Memory Inspection
// Write a three-byte structure to memory for inspection.
        mov rbx, 0x600000
        mov byte ptr [rbx], 0xAA
        mov byte ptr [rbx+1], 0xBB
        mov byte ptr [rbx+2], 0xCC

        mov rax, 60
        mov rdi, 0
        syscall
