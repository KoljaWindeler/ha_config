import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, time

class cubeWorld(hass.Hass):

	def initialize(self):
		self.log("Starting cube Service")
		self.action = False
		self.listen_state(self.cube, "sensor.0x00158d0002a7051f_action", attribute = "action")
		self.listen_state(self.no_cube, "sensor.0x00158d0002a7051f_action", attribute = "action", new="", duration=30)

    ######################################################

	def no_cube(self, entity="", attribute="", old="", new="", kwargs=""):
		self.log("no cube movement for 90sec")
		if(self.action):
			self.turn_on("light.dev56",brightness=8)
			self.turn_off("light.dev19")


	def cube(self, entity="", attribute="", old="", new="", kwargs=""):
		c = self.get_state(entity,attribute="all")['attributes']
		self.log(c)
		self.log("new cuve state")
		self.log(new)
		if(new=="wakeup"):
			return
		elif(new=="None"):
			return
		elif(new==None):
			return
		elif(not(new=="")):
			self.action = True
			self.turn_on("light.dev56",brightness=120)
			self.turn_on("light.dev57",brightness=180)
			self.turn_on("light.dev19")
		return
#			l = "light.joiner_livingroom"
#			k = "light.joiner_kitchen"
#			if(self.get_state(l)=="on" and self.get_state(k)=="on"):
#				self.turn_off(l)
#				self.turn_off(k)
#			else:
#				self.turn_on(l)
#				self.turn_on(k)
#		elif(new=="flip90"):
#			self.toggle("light.dev44")
#		elif(new.startswith("rotate")):
#			if(new=="rotate_right"):
#				self.log("rotate right")
#			if(new=="rotate_left"):
#				self.log("rotate left")
#			angle = min(c['angle'],300)
#			add = 0.08/100*angle
#			vol = self.get_state("media_player.yamaha_receiver",attribute="all")['attributes']['volume_level']
#			self.log("vol level "+str(vol))
#			vol = str(vol+add)
#			self.call_service("media_player/volume_set", entity_id="media_player.yamaha_receiver", volume_level=vol)

