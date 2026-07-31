# file: asm/uno_blink/Makefile
# Purpose: Build & Flash AVR Assembly for Arduino Uno (ATmega328P)

MCU = atmega328p
F_CPU = 16000000UL
PORT ?= /dev/ttyUSB0
BAUD = 115200

CC = avr-gcc
OBJCOPY = avr-objcopy
AVRDUDE = avrdude

CFLAGS = -mmcu=$(MCU) -DF_CPU=$(F_CPU) -Os -Wall

all: uno_blink.hex

uno_blink.elf: uno_blink.asm
	$(CC) $(CFLAGS) -nostartfiles -o $@ $<

uno_blink.hex: uno_blink.elf
	$(OBJCOPY) -O ihex -R .eeprom $< $@

flash: uno_blink.hex
	$(AVRDUDE) -C /etc/avrdude.conf -v -p $(MCU) -c arduino -P $(PORT) -b $(BAUD) -D -U flash:w:$<:i

clean:
	rm -f *.elf *.hex *.o

.PHONY: all flash clean
# file asm/uno_blink/Makefile ends
