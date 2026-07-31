; file: asm/uno_blink/uno_blink.asm
; SPDX-License-Identifier: MIT
; Purpose: Bare metal AVR assembly blink for ATmega328P (Arduino Uno Pin 13 / PB5)
; Target Toolchain: avr-gcc / avr-as

#define __SFR_OFFSET 0
#include <avr/io.h>

.global main

main:
    ; Set PB5 (Pin 13) as output in DDRB register
    sbi     _SFR_IO_ADDR(DDRB), 5

loop:
    ; Toggle PB5 (Pin 13) set HIGH
    sbi     _SFR_IO_ADDR(PORTB), 5
    rcall   delay_long

    ; Toggle PB5 (Pin 13) set LOW
    cbi     _SFR_IO_ADDR(PORTB), 5
    rcall   delay_long

    rjmp    loop

; Delay subroutine using nested register countdowns (approx ~0.5s at 16MHz)
delay_long:
    ldi     r18, 40
delay_outer:
    ldi     r19, 255
delay_mid:
    ldi     r20, 255
delay_inner:
    dec     r20
    brne    delay_inner
    dec     r19
    brne    delay_mid
    dec     r18
    brne    delay_outer
    ret

; file asm/uno_blink/uno_blink.asm ends
