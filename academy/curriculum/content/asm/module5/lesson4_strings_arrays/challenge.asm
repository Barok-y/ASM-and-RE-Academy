// Lesson: Strings and Arrays
// Write the null-terminated string "GO" to memory and count its length into
// RBX (length must be 2, not counting the terminator).
        mov rbx, 0x600000
        mov byte ptr [rbx], 71
        mov byte ptr [rbx+1], 79
        mov byte ptr [rbx+2], 0
        mov rbx, 0
        mov rcx, 0x600000
loop_start:
        movzx rax, byte ptr [rcx]
        test rax, rax
        je done
        inc rbx
        inc rcx
        jmp loop_start
done:

        mov rax, 60
        mov rdi, 0
        syscall
