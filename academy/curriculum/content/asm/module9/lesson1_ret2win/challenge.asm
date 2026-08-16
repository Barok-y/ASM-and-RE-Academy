// Lesson: Return-to-Win (ret2win) - challenge
// Craft the exploit payload: 40 bytes of padding + the 8-byte little-endian
// address of win(). The reference payload is "A"*40 + pack("<Q", win_addr);
// run it with the emulator feeding that exact input and win() prints "WIN!".
vuln:
        push rbp
        mov rbp, rsp
        sub rsp, 32
        mov rax, 0
        mov rdi, 0
        mov rsi, rsp
        mov rdx, 128
        syscall
        test rax, rax
        jz done
        leave
        ret
win:
        mov rsi, 0x600000
        mov byte ptr [rsi], 'W'
        mov byte ptr [rsi+1], 'I'
        mov byte ptr [rsi+2], 'N'
        mov byte ptr [rsi+3], '!'
        mov rax, 1
        mov rdi, 1
        mov rdx, 4
        syscall
        mov rax, 60
        mov rdi, 0
        syscall
done:
        mov rax, 60
        mov rdi, 0
        syscall