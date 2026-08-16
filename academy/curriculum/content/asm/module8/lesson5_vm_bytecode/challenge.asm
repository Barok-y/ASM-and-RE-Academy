// Lesson: VM Bytecode Obfuscation
// Extend the toy VM with the oracle's remaining ops:
//   '2' -> acc += 0x41424344      'U' -> acc *= 7     'D' -> rol 3
// Bytecode '2','D','U',0 runs against acc = 0x1337 and leaves the final
// accumulator value in R8.
        mov rbx, 0x600000
        mov byte ptr [rbx], '2'
        mov byte ptr [rbx+1], 'D'
        mov byte ptr [rbx+2], 'U'
        mov byte ptr [rbx+3], 0
        mov rax, 0x1337                 // accumulator
        mov rcx, 0                      // program counter
loop:
        mov sil, byte ptr [rbx+rcx]
        cmp sil, 0
        je done
        cmp sil, 'U'
        je op_u
        cmp sil, 'D'
        je op_d
        cmp sil, '2'
        je op_two
        jmp loop
op_u:
        imul rax, 7
        inc rcx
        jmp loop
op_d:
        rol rax, 3
        inc rcx
        jmp loop
op_two:
        add rax, 0x41424344
        inc rcx
        jmp loop
done:
        mov r8, rax
        mov rax, 60
        mov rdi, 0
        syscall