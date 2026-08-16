// Lesson: Byte Transform Loops
// To recover the original flag from rev_this you invert the transform:
//   even index  -> byte - 5
//   odd index   -> byte + 2
// rev_this[8] = '|' (0x7c) at the even index 8, so subtract 5 to recover
// the original 'w' (0x77) and leave it in R8.
        mov rbx, 0x600000
        mov byte ptr [rbx], 0x7c        // rev_this[8] = '|'
        mov rcx, 8                      // even index
        mov al, byte ptr [rbx]
        test rcx, 1
        jnz odd
        sub al, 5                       // inverse even path: -5
        jmp store
odd:
        add al, 2                       // inverse odd path: +2
store:
        mov byte ptr [rbx], al
        movzx r8, byte ptr [rbx]        // 0x77 ('w')
        mov rax, 60
        mov rdi, 0
        syscall
