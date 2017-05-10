# -*- coding: utf-8 -*-
# Clase para control de LEDs del proyecto de Radio con Raspberry

import RPi.GPIO as GPIO
import time

class led_out:
	name = ""
    	channel = 0

    	def __init__(self, nombre, canal):
        	self.name = nombre
        	self.channel = canal
        	GPIO.setmode(GPIO.BOARD)
    		GPIO.setwarnings(False)
		GPIO.setup(canal, GPIO.OUT)
       
	def on(self):
        	GPIO.output(self.channel, 1)
        	return self.channel

    	def off(self):
            	GPIO.output(self.channel, 0)
        	return self.channel

    	def blink(self):
            	GPIO.output(self.channel, 1)
            	time.sleep(0.04)
            	GPIO.output(self.channel, 0)
            	time.sleep(0.04)
		return self.channel
	
	def sit_led(self, valor):
                valor = int(valor)
		if valor == 0:
                        self.off()
                elif valor == 1:
                        self.on()
                else:
                        self.blink()
                return self.name

