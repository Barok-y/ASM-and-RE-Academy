// Lesson: Byte Transform Loops (based on picoCTF 'rev')
// The 'rev' binary reads flag.txt and for chars at indexes 8..22 applies:
//   even index  -> byte + 5
//   odd index   -> byte - 2
// Here index 8 (even) transforms 'w' (0x77) into 0x7c ('|').
        mov rbx, 0x600000
        mov byte ptr [rbx], 'w'         // 0x77
        mov rcx, 8                      // even index
        mov al, byte ptr [rbx]
        test rcx, 1
        jnz odd
        add al, 5                       // even path: +5
        jmp store
odd:
        sub al, 2                       // odd path: -2
store:
        mov byte ptr [rbx], al
        movzx r8, byte ptr [rbx]        // 0x7c ('|')
        mov rax, 60
        mov rdi, 0
        syscall
