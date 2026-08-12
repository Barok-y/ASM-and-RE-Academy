// Lesson: SIMD Overview
// Element-wise add of [1,2,3,4] and [4,3,2,1] gives [5,5,5,5]// leave the sum
// (20) in RBX.
        mov rdi, 0x600000
        mov byte ptr [rdi], 1
        mov byte ptr [rdi+1], 2
        mov byte ptr [rdi+2], 3
        mov byte ptr [rdi+3], 4
        mov rsi, 0x610000
        mov byte ptr [rsi], 4
        mov byte ptr [rsi+1], 3
        mov byte ptr [rsi+2], 2
        mov byte ptr [rsi+3], 1
        mov rbx, 0
        mov rcx, 0
loop_start:
        movzx r8, byte ptr [rdi+rcx]
        movzx r9, byte ptr [rsi+rcx]
        add r8, r9
        add rbx, r8
        inc rcx
        cmp rcx, 4
        jne loop_start

        mov rax, 60
        mov rdi, 0
        syscall
