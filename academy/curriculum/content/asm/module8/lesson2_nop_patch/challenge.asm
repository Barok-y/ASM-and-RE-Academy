// Lesson: Patching a Check with NOPs
// The patched check mirrors the real crackme: a test on the password
// comparison result is followed by two NOPs (the conditional jump that used
// to skip the grant block). With a wrong password in RAX, control still
// falls straight into the grant block, leaving R8 = 1.
        mov rax, 0              // wrong password (RAX = 0 from strcmp != 0)
        test rax, rax
        nop                     // was: jne denied
        nop
        mov r8, 1               // "Access Granted!" always prints
done:
        mov rax, 60
        mov rdi, 0
        syscall
