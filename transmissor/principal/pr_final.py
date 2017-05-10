# !/usr/bin/env python
#  -*- coding: utf-8 -*-
# Programa Principal de Control de Radio con Raspberry Pi

import leds.leds_ctrl as led
import radio.radio_ctrl as radio
import RPi.GPIO as GPIO 
import threading
import time
import os

def do_ping_audio(radio):
	global end
	while 1:
		try:
			radio.server_connect()
			radio.audio_device()
			time.sleep(1)
			if end == True: break
		except KeyboardInterrupt:
			end = True

def do_listeners(radio):
	global end
	while 1:
		try:
			radio.val_display()
			time.sleep(1)
			if end == True: break
		except KeyboardInterrupt:
			end = True			
	
def btn_trns(channel):
	r_ccd.transm()

if __name__ == '__main__':

	global end
	try:
		end = False
		
		r_ccd = radio.radio_class()
		
		d_p_a = threading.Thread(target = do_ping_audio, args = (r_ccd,))
		d_l = threading.Thread(target = do_listeners, args = (r_ccd,))

		d_p_a.start()
		d_l.start()

		GPIO.setup(3, GPIO.IN,pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(3, GPIO.FALLING,callback=btn_trns,bouncetime=800)

		while 1:
			pass

	except KeyboardInterrupt:
		GPIO.cleanup()
		end = True
		print 'Fin del Programa'
