// Lesson: XOR Obfuscation (based on a real crackme)
// The crackme's decode() XORs ciphertext bytes with a single key byte to
// restore the plaintext in memory before strcmp. Here we XOR three bytes
// (0x2c 0x6b 0x68) with the key 0x5a: they become 'v' '1' '2'.
        mov rbx, 0x600000
        mov byte ptr [rbx], 0x2c
        mov byte ptr [rbx+1], 0x6b
        mov byte ptr [rbx+2], 0x68
        mov rcx, 0
loop:
        mov al, byte ptr [rbx+rcx]
        xor al, 0x5a
        mov byte ptr [rbx+rcx], al
        inc rcx
        cmp rcx, 3
        jne loop
        movzx r8, byte ptr [rbx]        // first decoded byte -> 'v' (0x76)
        mov rax, 60
        mov rdi, 0
        syscall
