// Lesson: Crackmes and Patching
// A password check: compare the candidate to 42. If equal, grant access.
        mov rax, 42        // candidate password
        cmp rax, 42        // expected password
        je grant
        mov rbx, 0
        jmp done
grant:
        mov rbx, 1
done:
        mov r8, rbx

        mov rax, 60
        mov rdi, 0
        syscall
