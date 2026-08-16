// Lesson: Patching a Check with NOPs (based on a real crackme)
// The crackme compared the typed password to 'hidden123'. A patcher
// overwrote the 2-byte conditional jump with two NOPs, so the check always
// falls through to the grant block - even for the WRONG password RAX = 0.
        mov rax, 0              // attacker-supplied wrong password
        cmp rax, 1337
        nop                     // was: je grant (patched out)
        nop
        mov r8, 1               // grant block: access granted
done:
        mov rax, 60
        mov rdi, 0
        syscall
