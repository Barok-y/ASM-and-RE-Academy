// Lesson: VM Bytecode Obfuscation (based on the ADWA 'oracle' challenge)
// A tiny interpreter walks bytecode bytes stored in memory and updates a
// 64-bit accumulator (initially 0x1337, like the real oracle):
//   'U' -> acc *= 7        'D' -> acc = rotate-left 3      0 -> halt
// Bytecode 'U','D',0 leaves acc = 0x43408.
        mov rbx, 0x600000
        mov byte ptr [rbx], 'U'
        mov byte ptr [rbx+1], 'D'
        mov byte ptr [rbx+2], 0
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
        jmp loop
op_u:
        imul rax, 7
        inc rcx
        jmp loop
op_d:
        rol rax, 3
        inc rcx
        jmp loop
done:
        mov r8, rax                     // 0x43408
        mov rax, 60
        mov rdi, 0
        syscall