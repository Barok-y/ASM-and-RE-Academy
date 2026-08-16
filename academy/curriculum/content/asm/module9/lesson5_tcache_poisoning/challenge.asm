// Lesson: TCache Freelist Poisoning - challenge
// Poison the freed chunk's next pointer (first qword at 0x700000) so the
// next malloc returns 0x700080 instead of the real freelist head. The
// reference writes 0x700080 into the chunk and R8 ends up holding it.
        mov rbx, 0x700000
        mov qword ptr [rbx], 0x701000        // freed chunk's next = freelist head
        mov qword ptr [rbx], 0x700080        // attacker poisons the next pointer
        mov r8, qword ptr [rbx]              // malloc returns the poisoned next
        mov rax, 60
        mov rdi, 0
        syscall