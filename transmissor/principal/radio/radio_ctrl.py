# -*- coding: utf-8 -*-
# Clase para control de acciones de Radio con Raspberry

import os
import sys
import subprocess as sub
import xml.etree.ElementTree as ET
import time
import urllib2
import ConfigParser
import leds.leds_ctrl as led

class radio_class:

	act_ices = False
    	audio = False
    	server = False
	t_led = ''
	a_led = ''
	p_led = ''
	a0 = ''
	b0 = ''
	c0 = ''
	d0 = ''
	an0 = ''
	an1 = ''
	user_name = ''
	listeners = 0
    
    	def __init__(self):
		# Declaración de objetos de los leds
		self.p_led = led.led_out("broadcast", 11)
		self.a_led = led.led_out("audio", 12)
		self.t_led = led.led_out("ping", 13)	
        	# Declaracion de objetos del display
		self.a0 = led.led_out("A0", 8)
                self.b0 = led.led_out("B0", 7)
                self.c0 = led.led_out("C0", 5)
                self.d0 = led.led_out("D0", 10)

                self.an0 = led.led_out("AN0", 16)
                self.an1 = led.led_out("AN1", 15)

		self.print_delay('Verificando Funcionamiento de LEDS')
		self.toggle_leds()
    		print '\n'
		self.print_delay('Verificando Funcionamiento de Display')
		self.check_display()
		print '\n'
		self.print_delay('Generando Nombre de Usuario')
		self.gen_usuario()
		self.print_delay('Verificando conexión al Servidor de Radio')
		self.server_connect()
		self.print_delay('Verificando dispositivo de Entrada de Audio')
		self.audio_device()
	
	def server_connect(self):
		ping = os.system('sudo timeout 0.2 ping -c1 120.120.6.32 > /dev/null')
		nb_ping = not(bool(ping))
                if nb_ping != self.server:
                        if ping == 0:
                                print '\nHay conexión con el servidor de radio'
                                self.server_up()
                        else:
                                print '\nNo hay conexión con el servidor de radio'
                                self.server_down()
		return ping

	def server_up(self):
		self.server = True
		self.p_led.on()
		return self.server
	
	def server_down(self):
		self.server = False
		self.p_led.off()
		# Método que termina transmisión
		return self.server
		
	def audio_device(self):
		a_dev = os.popen('arecord -l')
		line_t = a_dev.read()
		line = line_t.split('\n')
		n_lines = len(line)
		if bool(n_lines - 2) != self.audio:
			if n_lines == 2:
				print '\nNo se encuentra dispositivo de audio'
				self.audio_down()
			elif n_lines == 5:
				print '\nSe encuentra dispositivo de audio'
				self.audio_up()
		return n_lines 

	def audio_up(self):
		self.audio = True
		self.a_led.on()
		return self.audio

	def audio_down(self):
                self.audio = False
                self.a_led.off() 
                return self.audio

	def gen_usuario(self):		                
		proc = sub.Popen('cat /sys/class/net/eth0/address', shell=True, stdout=sub.PIPE, )
                phy_add=proc.communicate()[0]
                add_phy = phy_add[::-1]
                add_phy = add_phy.split('\n')
                self.user_name = add_phy[1].replace(':','')
		print '\nEl usuario generado es %s' %self.user_name
		return self.user_name
	
	def cfg_darkice(self):
		os.system('sudo rm /etc/darkice.cfg')
		Config = ConfigParser.ConfigParser()
                Config.optionxform = str
		cfgfile = open("/home/pi/RadioRaspi/aux_cfg",'w')
                Config.add_section('general')
                Config.add_section('input')
                Config.add_section('icecast2-0')
                #datos de la sección "general"
                Config.set('general', 'duration', 0)
                Config.set('general', 'bufferSecs', 2)
                Config.set('general', 'reconnect', 'yes')
                #Datos de la sección input      
                Config.set('input', 'device', 'hw:1,0')
                Config.set('input', 'sampleRate', 44100)
                Config.set('input', 'bitsPerSample', 16)
                Config.set('input', 'channel', 1)
                #Datos de la sección icecast2-0
                Config.set('icecast2-0', 'bitrateMode', 'vbr')
                Config.set('icecast2-0', 'bitrate', 320)
                Config.set('icecast2-0', 'format', 'mp3')
                Config.set('icecast2-0', 'quality', 0.6)
                Config.set('icecast2-0', 'server', '120.120.6.32')
                Config.set('icecast2-0', 'port', 8000)
                Config.set('icecast2-0', 'password', 'raDioCCD07')
                Config.set('icecast2-0', 'mountPoint', self.user_name)
		Config.set('icecast2-0', 'sampleRate', 44100)
                Config.set('icecast2-0', 'name', self.user_name)
                Config.set('icecast2-0', 'description', self.user_name)
                Config.set('icecast2-0', 'public', 'yes')
		#Escritura de cambios
                Config.write(cfgfile)
                cfgfile.close()
                os.system("sudo cp /home/pi/RadioRaspi/aux_cfg /etc/darkice.cfg")
                os.system("sudo rm /home/pi/RadioRaspi/aux_cfg")
	
	def n_listeners(self):
		try:
			str_listen = ''
			url = 'http://120.120.6.32:8000/' + self.user_name + '.xspf'
			f = urllib2.urlopen(url)
			data = f.read()
			data_split = data.split('\n')
			aux_listen = data_split[12].split(':')
			self.listeners = int(aux_listen[1])
		except:
			self.listeners = 0
		return self.listeners
		
	def transm(self):
		if self.server == True and self.audio == True:
			if self.act_ices == False:
				self.start_transm()
			else:
				self.stop_transm()
	
	def start_transm(self):
		print 'Inicio Transmisión'
                self.cfg_darkice()
		os.system('sudo darkice &')
                self.t_led.on()
		self.act_ices = True

	def stop_transm(self):
		print 'Fin Transmisión'
		self.t_led.off()
		os.system('sudo killall darkice')
		self.act_ices = False

	def val_display(self):
		if self.act_ices == True:
			self.n_listeners()
			e_nu = '{0:04b}'.format(int(self.listeners) % 10)
			d_nu = '{0:04b}'.format(int(self.listeners) / 10)
			print 'e_nu: %s' %e_nu
			print 'd_nu: %s' %d_nu
			for n_rep in range(500):
				print n_rep
				for digit in range(2):
					if digit == 0:
						self.a0.sit_led(e_nu[0])
						self.b0.sit_led(e_nu[1])
						self.c0.sit_led(e_nu[2])
						self.d0.sit_led(e_nu[3])
						self.an0.off()
						self.an1.on()
						time.sleep(0.008)
					else:
						self.a0.sit_led(d_nu[0])
						self.b0.sit_led(d_nu[1])
						self.c0.sit_led(d_nu[2])
						self.d0.sit_led(d_nu[3])
						self.an1.off()
						self.an0.on()
						time.sleep(0.008)
		else:
			print 'No hay emisión de radio'
			self.an0.on()
			self.an1.on()					
	
	def toggle_leds(self):
		for i in range(0, 15):
			self.p_led.on()
			self.a_led.on()
			self.t_led.on()
			time.sleep(0.075)
			self.p_led.off()
                        self.a_led.off()
                        self.t_led.off()
                        time.sleep(0.075)

	def check_display(self):
		self.an0.off()
		self.an1.off()
		for i in range(0,10):
			nu = '{0:04b}'.format(i)
			print nu
			self.a0.sit_led(nu[0])
			self.b0.sit_led(nu[1])
			self.c0.sit_led(nu[2])
			self.d0.sit_led(nu[3])
			time.sleep(0.25)
		self.an0.on()
		self.an1.on()

	def print_delay(self, blah):
		for l in blah:
			sys.stdout.write(l)
			sys.stdout.flush()
			time.sleep(0.025)

