// Lesson: Switches and Jump Tables
// Switch on RAX = 3: case 1 -> RBX=100, case 2 -> RBX=200, case 3 -> RBX=300,
// default -> RBX=0.
        mov rax, 3
        cmp rax, 1
        je c1
        cmp rax, 2
        je c2
        cmp rax, 3
        je c3
        mov rbx, 0
        jmp done
c1:
        mov rbx, 100
        jmp done
c2:
        mov rbx, 200
        jmp done
c3:
        mov rbx, 300
done:

        mov rax, 60
        mov rdi, 0
        syscall
