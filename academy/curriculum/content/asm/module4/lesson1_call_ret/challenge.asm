// Lesson: CALL and RET
// Call two functions in sequence: first adds 10, second doubles.
        mov rax, 5
        call addten
        call double_it
        mov r8, rax

        mov rax, 60
        mov rdi, 0
        syscall

addten:
        add rax, 10
        ret

double_it:
        shl rax, 1
        ret
