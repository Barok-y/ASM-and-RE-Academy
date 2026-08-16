// Lesson: XOR Obfuscation
// Decode the crackme's 7-byte XOR password. The ciphertext is
//   0x28 0x3f 0x2c 0x6b 0x68 0x69 0x7b
// and the key is the single byte 0x5a. The decoded plaintext spells
// 'rev123!'. Leave the FIRST decoded byte ('r' = 0x72) in R8.
        mov rbx, 0x600000
        mov byte ptr [rbx], 0x28
        mov byte ptr [rbx+1], 0x3f
        mov byte ptr [rbx+2], 0x2c
        mov byte ptr [rbx+3], 0x6b
        mov byte ptr [rbx+4], 0x68
        mov byte ptr [rbx+5], 0x69
        mov byte ptr [rbx+6], 0x7b
        mov rcx, 0
loop:
        mov al, byte ptr [rbx+rcx]
        xor al, 0x5a
        mov byte ptr [rbx+rcx], al
        inc rcx
        cmp rcx, 7
        jne loop
        movzx r8, byte ptr [rbx]        // 'r' = 0x72
        mov rax, 60
        mov rdi, 0
        syscall
