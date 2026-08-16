// Lesson: TCache Freelist Poisoning
// A freed heap chunk at 0x700000 holds the freelist's "next" pointer in its
// first qword (here the current head, 0x701000). The attacker overwrites
// that qword - poisoning the list - so the next malloc returns an arbitrary
// target address, 0x700080. The vuln "allocates" by reading the poisoned
// next pointer into R8.
        mov rbx, 0x700000
        mov qword ptr [rbx], 0x701000        // freed chunk's next = freelist head
        mov qword ptr [rbx], 0x700080        // attacker poisons the next pointer
        mov r8, qword ptr [rbx]              // malloc returns the poisoned next
        mov rax, 60
        mov rdi, 0
        syscall