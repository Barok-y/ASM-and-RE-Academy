// Lesson: Strings and Arrays
// Build a null-terminated string "ABC" in memory and count its length.
        mov rbx, 0x600000
        mov byte ptr [rbx], 65
        mov byte ptr [rbx+1], 66
        mov byte ptr [rbx+2], 67
        mov byte ptr [rbx+3], 0
        mov rcx, 0
        mov rdx, 0x600000
loop_start:
        movzx rax, byte ptr [rdx]
        test rax, rax
        je done
        inc rcx
        inc rdx
        jmp loop_start
done:
        mov r8, rcx

        mov rax, 60
        mov rdi, 0
        syscall
