// Lesson: Crackmes and Patching
// The original check was 'jne deny' (wrong password -> denied). A patcher
// flipped the jump to 'je deny', so a WRONG password is now granted. With
// RAX = 0 the check grants access (RBX = 1).
        mov rax, 0
        cmp rax, 1337
        je deny            // patched: was 'jne deny'
        mov rbx, 1
        jmp done
deny:
        mov rbx, 0
done:

        mov rax, 60
        mov rdi, 0
        syscall
