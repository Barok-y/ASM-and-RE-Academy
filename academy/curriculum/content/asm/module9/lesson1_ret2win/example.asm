// Lesson: Return-to-Win (ret2win)
// vuln() reads 128 bytes into a 32-byte stack buffer, then returns.
// An attacker payload of 40 bytes (32 buffer + 8 saved rbp) followed by
// the little-endian address of win() redirects control into win(), which
// prints "WIN!". With no input the read returns 0 and the function exits
// cleanly instead of overflowing.
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