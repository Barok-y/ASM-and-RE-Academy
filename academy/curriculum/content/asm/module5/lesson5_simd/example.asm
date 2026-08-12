// Lesson: SIMD Overview
// Simulate an element-wise vector add of [2,4,6,8] and [1,1,1,1] with a
// scalar loop (real SIMD would do this in one instruction) and sum the
// results.
        mov rdi, 0x600000
        mov byte ptr [rdi], 2
        mov byte ptr [rdi+1], 4
        mov byte ptr [rdi+2], 6
        mov byte ptr [rdi+3], 8
        mov rsi, 0x610000
        mov byte ptr [rsi], 1
        mov byte ptr [rsi+1], 1
        mov byte ptr [rsi+2], 1
        mov byte ptr [rsi+3], 1
        mov rax, 0
        mov rcx, 0
loop_start:
        movzx r8, byte ptr [rdi+rcx]
        movzx r9, byte ptr [rsi+rcx]
        add r8, r9
        add rax, r8
        inc rcx
        cmp rcx, 4
        jne loop_start

        mov rax, 60
        mov rdi, 0
        syscall
