import appdaemon.plugins.hass.hassapi as hass
import json
import datetime, time

class StuffWorld(hass.Hass):

	def initialize(self):
		self.log("Starting Stuff")
		## virtual buttons for all on / off / music
		self.listen_state(self.sleep,"input_boolean.sleep")
		self.listen_state(self.on_music,"input_boolean.on_with_music")

		## forward switch to lamp on terrace
		self.f = [] # input (binary) , output (switch)
		self.f.append(["binary_sensor.dev46_gpio_13","switch.dev47_gpio_15"])
		self.f.append(["binary_sensor.dev46_gpio_5","switch.dev47_gpio_4"])
		for i in self.f:
			self.listen_state(self.forward,i[0])


	def forward(self, entity="", attribute="", old="", new="", kwargs=""):
		s = ["on","off"]
		if(new in s and old in s):
			self.log("forwarding state "+new+" from entity "+entity)
			for i in self.f:
				if(i[0] == entity):
					self.toggle(i[1])
					break
		else:
			self.log(new+"/"+old)


	def sleep(self, entity="", attribute="", old="", new="", kwargs=""):
		self.log("Sleep")
		if(new=="on"):
			self.set_state("sensor.adafruit",state="wir_gehen_schlafen")
			self.set_state(entity,state="Off")

	def on_music(self, entity="", attribute="", old="", new="", kwargs=""):
		self.log("on music")
		if(new=="on"):
			self.set_state("binary_sensor.dev3_button1s",state="on")
			time.sleep(1)
			self.set_state("binary_sensor.dev3_button1s",state="off")
			self.set_state(entity,state="Off")

