import math
import appdaemon.plugins.hass.hassapi as hass
import datetime, time
from threading import Timer


class GmotionWorld(hass.Hass):

	def initialize(self):
		self.log("Starting gmotion Service")
		self.set_state("sensor.error",state=" ")

		self.listen_state(self.home, "person.caro_2", new = "home", duration = 10*60, arg1="Caro home")  # everyone is home for 10 min
		self.listen_state(self.home, "person.kolja_2", new = "home", duration = 10*60, arg1="Kolja home")  # everyone is home for 10 min

		self.listen_state(self.system_state, "binary_sensor.someone_is_home")
		self.listen_state(self.system_state, "input_boolean.alarm_system")
		self.listen_state(self.system_state, "vacuum.xiaomi_vacuum_cleaner")
		self.listen_state(self.system_state, "vacuum.xiaomi_vacuum_cleaner_2")

		self.sensor = []
		self.sensor.append(["Floor upstairs","dev57_motion",1]) # lichterkette
		self.sensor.append(["Floor upstairs Zigbee","0x00158d0002f0bc08_occupancy",1]) # zigbee an der badezimmer wand
		self.sensor.append(["Stairs upstairs Zigbee","0x00158d00045d7a47_occupancy",1]) # zigbee an der treppe oben

		self.sensor.append(["World map","dev15_motion",0]) # weltkarte
		self.sensor.append(["Kitchen island","dev16_motion",0]) # kuechen tresen
		self.sensor.append(["Entrance","dev54_motion_1",0]) # foyer decke
#		self.sensor.append(["Entrance","dev9_gpio_4",0]) # schiebeschrank richtung foyer ...NICHT ZUVERLAESSIG
#		self.sensor.append(["Entrance","dev9_gpio_5",0]) # schiebeschrank innen
		self.sensor.append(["Entrance","0x00158d00056d51ca_occupancy",0]) # schiebeschrank innen
		self.sensor.append(["Entrance","dev54_motion_1",0]) # foyer decke

		self.sensor.append(["Cellar 1","dev59_motion_13",255]) # kellerdurchgang 1
		self.sensor.append(["Cellar 2","dev59_motion_16",255]) # kellerdurchgang 2
		self.sensor.append(["Cellar Zigbee","0x00158d0005a9e90e_occupancy",255]) # zigbee in der mitte
		self.sensor.append(["Entrance_cellar","dev54_motion_2",255]) # oben am treppenabgang
		self.sensor.append(["Cellar door","dev17_motion",255]) # 2. kelleraussen tuer
		self.sensor.append(["Cellar heater","0x00158d0003f85cf0_occupancy",255]) # zigbee im heizungskeller

		self.sensor.append(["Garage","dev8_motion",254])

		self.sensor_trigger_count = []
		self.sensor_trigger_count_reported = []
		for i in range(0,len(self.sensor)):
			self.listen_state(self.motion, "binary_sensor."+self.sensor[i][1])
			self.sensor_trigger_count_reported.append(0)
			self.sensor_trigger_count.append(0)
		self.msg_delay = [0,3*60,8*60,15*60]
		self.msg_ts = 0
		self.msg_nr = 0

		self.g_motion = 0
		self.g_motion_upstairs = 0
		self.g_motion_basement = 0
		self.g_motion_cellar = 0

 
		self.motion("","","","","")
		self.home("","","","","")
		self.system_state()


	def system_state(self, entity="", attribute="", old="", new="", kwargs=""):
		# assumption: system is off
		sec_short = "off"
		sec_long = "disabled"
		# system is on
		if(self.get_state("input_boolean.alarm_system") == "on"):
			vac = self.get_state("vacuum.xiaomi_vacuum_cleaner")
			vac2 = self.get_state("vacuum.xiaomi_vacuum_cleaner_2")
			if(self.get_state("binary_sensor.someone_is_home") == "on"):
				sec_short = "off" #unlocked
				sec_long = "enabled, but someone is home"
			elif((vac in ["cleaning", "returning"]) or (vac2 in ["cleaning", "returning"])):
				sec_short = "off" #unlocked
				sec_long = "enabeld, but vacuuming"
			else:
				sec_short = "on" #locked
				sec_long = "enabled"
		self.set_state("binary_sensor.sec_short",state=sec_short)
		self.set_state("sensor.sec_long",state=sec_long)


	def home(self, entity, attribute, old, new, kwargs):
		if(self.get_state("person.caro_2") != "home" and self.get_state("person.kolja_2") != "home"):
			self.sensor_trigger_count = []
			self.sensor_trigger_count_reported = []
			for i in range(0,len(self.sensor)):
				self.sensor_trigger_count.append(0)
				self.sensor_trigger_count_reported.append(0)


	def motion(self, entity, attribute, old, new, kwargs):
		#self.log("check motion")
		#start = time.time()
		cellar_m = "off"
		basement_m = "off"
		upstairs_m = "off"
		m = "off"
		for i in range(0,len(self.sensor)):
			#self.log("binary_sensor."+self.sensor[i]+": "+self.get_state("binary_sensor."+self.sensor[i]))
			if(self.get_state("binary_sensor."+self.sensor[i][1]) == "on"):
#				self.log(self.sensor[i])
				m = "on"
				self.sensor_trigger_count[i] = self.sensor_trigger_count[i]+1
				if(self.sensor[i][2]==255):
					cellar_m = "on"
				elif(self.sensor[i][2]==0):
					basement_m = "on"
				elif(self.sensor[i][2]==1):
					upstairs_m = "on"
		# per storry motion
		if(self.g_motion_cellar != cellar_m):
			self.set_state("binary_sensor.g_motion_cellar",state=cellar_m)
			self.g_motion_cellar = cellar_m
		if(self.g_motion_basement != basement_m):
			self.set_state("binary_sensor.g_motion_basement",state=basement_m)
			self.g_motion_basement = basement_m
		if(self.g_motion_upstairs != upstairs_m):
			self.set_state("binary_sensor.g_motion_upstairs",state=upstairs_m)
			self.g_motion_upstairs = upstairs_m
		# gloabal motion
		if(self.g_motion != m):
			self.set_state("binary_sensor.g_motion",state=m)
			if(m=="on"):
				self.safety()
		#end = time.time()
		#self.log(end-start)


	def safety(self, kwargs=""):
		#self.log("check safety")
		if(not(self.get_state("input_boolean.alarm_system") == "on")):
			#self.log("Safety disabled, quitting")
			return 0

		################# nicht alarm handling ########################
		try:
			if(int(self.get_state("sensor.bed_occupancy"))==2):
				if(self.get_state("binary_sensor.g_motion_cellar")=="on"  or self.get_state("binary_sensor.g_motion_basement")=="on"):
					m="Well there is motion at night in the cellar or the basement .. you might want to have a look, "
					m+=str(self.get_state('sensor.dev45_hx711'))
					self.log(m)
					self.call_service("notify/pb", title="Nightly motion alert", message=m)
					for i in range(0,6):
						if(i%2==0):
							self.turn_on("light.dev32")
						else:
							self.turn_off("light.dev32")
						time.sleep(1)
		except:
			pass


		################# global alarm handling ########################
		changes = False
		for i in range(0,len(self.sensor)):
			if(not(self.sensor_trigger_count_reported[i]==self.sensor_trigger_count[i])):
				changes = True

		if(not(changes)):
			#self.log("no new alarm counts, exiting")
			return 0

		#self.log("call safety")
		## ok, we have some motion, what to do?
		## 1. check if someone is home, if so, ignore it for the safety function
		##    if not, check if the vacuum is cleaning (more states needed?)
		## 2. if the vac is not cleaning and no one is home, send a message that includes:
		## 2.1. The sensor that triggered and their trigger count
		## 2.2. the vacuum status
		## 2.3. the distance of us towards home
		# 1.
		if(self.get_state("person.caro_2") != "home" and self.get_state("person.kolja_2") != "home"):
			# 2.
			vac = self.get_state("vacuum.xiaomi_vacuum_cleaner")
			vac2 = self.get_state("vacuum.xiaomi_vacuum_cleaner_2")
			if(not(vac in ["cleaning", "returning"]) and not(vac2 in ["cleaning", "returning"])):
				# 2.1.
				#self.log("motion and no-one home and vacuum not cleaning")
				if(time.time() - self.msg_ts >= self.msg_delay[self.msg_nr]):
					self.msg_ts = time.time()
					if(self.msg_nr == 0):
						msg = "Hi, there is some motion at home, "
					elif(self.msg_nr < 4):
						msg = "Hi, there is still something going on, "

					msg += "Sensors: " 
					for i in range(0,len(self.sensor)):
						if(self.sensor_trigger_count[i] - self.sensor_trigger_count_reported[i]>0):
							msg +=self.sensor[i][0]+" ("+str(self.sensor_trigger_count[i] - self.sensor_trigger_count_reported[i])+"x) "
					msg += ". Distances: "
					msg +="Kolja ("+str(self.distance("device_tracker.google_maps_110518043042355478237"))+") "
					msg +="Caro ("+str(self.distance("device_tracker.google_maps_114864588644392991844"))+") "
					msg +="Vacuum status: "+self.get_state("vacuum.xiaomi_vacuum_cleaner")
					msg +=" / Vacuum 2 status: "+self.get_state("vacuum.xiaomi_vacuum_cleaner_2")


					self.log(msg)
					self.call_service("notify/pb", title="Motion alert", message=msg)
					self.call_service("notify/pb_c", title="Motion alert", message=msg)

					if(self.msg_nr +1 < len(self.msg_delay)):
						self.msg_nr = self.msg_nr +1


				#else:
				#	self.log("have to wait further "+str(self.msg_delay[self.msg_nr]-(time.time()-self.msg_ts))+" sec")
				# call me again in 30 sec
			#else:
			#	self.log("vacuum running")
			self.handle = self.run_in(self.safety,delay=10)
		else:
			#self.log("someone is home, resetting counters")
			if(self.msg_nr>0):
				self.msg_nr = 0

				msg = "Issue solved, "
				if(self.get_state("person.caro_2") == "home"):
					msg = "Caro "
				elif(self.get_state("person.kolja_2") == "home"):
					msg = "Kolja "
				msg += "is home now"
				self.log(msg)
				self.call_service("notify/pb", title="Motion alert", message=msg)

				self.sensor_trigger_count = []
				self.sensor_trigger_count_reported = []
				for i in range(0,len(self.sensor)):
					self.sensor_trigger_count.append(0)
					self.sensor_trigger_count_reported.append(0)

		for i in range(0,len(self.sensor)):
			self.sensor_trigger_count_reported[i]=self.sensor_trigger_count[i]



	def distance(self,d):
		try:
			d = self.get_state(d,attribute="all")["attributes"]
			lat1 = d["latitude"]
			lon1 = d["longitude"]

			h = self.get_state("zone.home",attribute="all")["attributes"]
			lat2 = h["latitude"]
			lon2 = h["longitude"]

			radius = 6371  # km
			dlat = math.radians(lat2 - lat1)
			dlon = math.radians(lon2 - lon1)
			a = (math.sin(dlat / 2) * math.sin(dlat / 2) +  math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2))
			c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
			d = radius * c
			d = round(d,2)
		except:
			d = "-1"
		return d
