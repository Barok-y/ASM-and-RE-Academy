// Lesson: Switches and Jump Tables
// A three-way switch as a chain of CMP/JE. RAX = 2 selects case 2.
        mov rax, 2
        cmp rax, 1
        je case_one
        cmp rax, 2
        je case_two
        mov rbx, 0
        jmp done
case_one:
        mov rbx, 10
        jmp done
case_two:
        mov rbx, 20
done:
        mov r8, rbx

        mov rax, 60
        mov rdi, 0
        syscall
