// Lesson: Recovering Strings from Immediates (based on picoCTF)
// A compiler stored 'ASM{3lf_' as a single 64-bit immediate:
//   movabs rax, 0x5f666c337b4d5341
// Stored little-endian, the bytes in memory read 41 53 4d 7b 33 6c 66 5f,
// which is exactly the ASCII string 'ASM{3lf_'.
        mov rbx, 0x600000
        mov rax, 0x5f666c337b4d5341
        mov qword ptr [rbx], rax
        movzx r8, byte ptr [rbx]        // byte index 0 -> 'A' (0x41)
        mov rax, 60
        mov rdi, 0
        syscall
