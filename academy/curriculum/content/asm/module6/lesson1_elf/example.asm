// Lesson: ELF Structure
// A leaf 'function' fragment that takes RDI and returns RDI + 1 in RAX
// (this is the kind of code an ELF .text section contains).
        mov rax, rdi
        add rax, 1

        mov rdi, 0
        mov rax, 60
        syscall
