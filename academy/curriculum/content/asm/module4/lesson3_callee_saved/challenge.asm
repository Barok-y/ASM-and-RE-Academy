// Lesson: Callee-Saved vs Caller-Saved
// The caller preserves RBX across a call that tramples it (caller-saved style).
        mov rbx, 77
        push rbx
        call trample
        pop rbx

        mov rax, 60
        mov rdi, 0
        syscall

trample:
        mov rbx, 999
        ret
