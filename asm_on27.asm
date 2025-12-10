section .data
filename db "/home/abi/Proyecto_GPIO/gpio27.txt",0
one db "1",0

section .text
global _start

_start:
    mov rax, 2
    mov rdi, filename
    mov rsi, 1
    mov rdx, 0644o
    syscall

    mov rbx, rax

    mov rax, 1
    mov rdi, rbx
    mov rsi, one
    mov rdx, 1
    syscall

    mov rax, 3
    mov rdi, rbx
    syscall

    mov rax, 60
    mov rdi, 0
    syscall
