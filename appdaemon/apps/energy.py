import math
import appdaemon.plugins.hass.hassapi as hass
import wait
import datetime

class EnergyWorld(hass.Hass):

	def initialize(self):
		self.log("Starting Energy Service")
		wait.wait_available(self,["sensor.dev37_em_tot_grid","sensor.pv_power_int"],False)
		#self.listen_state(self.update, "input_boolean.clear_Energy")
		self.cost_kwh = 0.247 #0.2231 # 25.35
		self.cost_fix_month = 17.31 # 17.85 # 196.46 = 16.37
		self.payment_month = 115
		self.dbg = True
		self.update()
		runtime = datetime.time(23, 50, 0)
		self.run_daily(self.update, runtime)

		############ smart power ###############
		self.dbg_sp = 0

		self.sp_net_lp = 0
		self.sp_on_delay_on_until = datetime.datetime.now()
		self.sp_on_delay_off_until = datetime.datetime.now()
		self.sp_safe_budget = 100
		self.sp_est_pwr = [] # estimated power
		self.sp_remaining = [] # min thst the device shall run
		self.sp_dev = []
		self.sp_timesensor = []
		self.sp_constrain = []
		self.sp_constrain_l = []
		self.sp_constrain_u = []
		self.sp_on_delay = []
		self.sp_off_delay = []

		self.sp_add(dev="switch.dev40_gpio_12", pwr=240) # dehumidifier has a build in safety feature to way 3 min before start, removed, power impact small
#sommer		self.sp_add(dev="switch.dev30_gpio_0",  pwr=600, time=180,timesensor="sensor.pump_time") # pool pump
		self.sp_add(dev="switch.dev41_gpio_4",  pwr=1000, constrain="sensor.dev29_temperature", lower=0, upper=55) # WW Heater 1
		self.sp_add(dev="switch.dev41_gpio_5",  pwr=500, constrain="sensor.dev29_temperature", lower=0, upper=55) # WW Heater 2
		self.sp_add(dev="switch.dev41_gpio_12", pwr=500, constrain="sensor.dev29_temperature", lower=0, upper=55) # WW Heater 3
#sommer extreme		self.sp_add(dev="switch.dev38_gpio_5",  pwr=2200, on_delay=90, off_delay=10) # pool heat will start approximatly 80 sec after flow

		self.run_daily(self.sp_reset, runtime)
		self.sp_time = datetime.datetime.now()
		self.listen_state(self.sp, "sensor.dev37_em_cur_fast")
		############ smart power ###############
		#self.listen_state(self.pv_watch, "sensor.kaco_194", attribute = "status_code")

	def pv_watch(self, entity="", attribute="", old="", new="", kwargs=""):
		try:
			state = self.get_state(entity_id="sensor.kaco_194", attribute="status")
			msg = "PV state change to "+str(new)+" = "+state
			self.log(msg)
			if(int(new)==47):
				self.call_service("notify/pb", title = "Solar", message = msg)
		except:
			pass


	def sp_add(self,dev,pwr,time=0,timesensor=None,constrain="",lower=0,upper=0,on_delay=10, off_delay=5):
		self.sp_est_pwr.append(pwr) # estimated power
		self.sp_remaining.append(time) # min thst the device shall run
		self.sp_dev.append(dev)
		self.sp_timesensor.append(timesensor)
		self.sp_constrain.append(constrain)
		self.sp_constrain_l.append(lower)
		self.sp_constrain_u.append(upper)
		self.sp_on_delay.append(on_delay)
		self.sp_off_delay.append(off_delay)

	def sp_reset(self, kwargs=""):
		self.log("resetting smart power runtime")

	def sp(self, entity="", attribute="", old="", new="", kwargs=""):
		try:
			net_d = float(self.get_state("sensor.dev37_em_cur_fast"))
			if(self.sp_net_lp == 0):
				net = round(net_d)
			else:
				net = round((2*self.sp_net_lp+net_d)/3)
			self.sp_net_lp = net
			solar = float(self.get_state("sensor.pv_power_int"))
		except:
			self.log("smart power exception")
			return

		######## debug	#####
		ontime = int(max(0,(self.sp_on_delay_on_until-datetime.datetime.now()).total_seconds()))
		offtime = int(max(0,(self.sp_on_delay_off_until-datetime.datetime.now()).total_seconds()))

		msg = "["+str(ontime)+"/"+str(offtime)+"] Solar "+str(int(solar))+", LP: "+str(net).zfill(5)+"W ("+str(net_d).zfill(7)+"W)"
		for d in range(0,len(self.sp_dev)):
			msg+=" "+self.friendly_name(self.sp_dev[d])+" ["+self.get_state(self.sp_dev[d])+"]"
#		self.log(msg)
		######## debug	#####


		elapsedTime = (datetime.datetime.now() - self.sp_time).total_seconds()
		self.sp_time = datetime.datetime.now()


		### log
		msg = "Smart power, solar: "+str(solar)+", net: "+str(net)
		if(net>0):
			msg += " so we're drawing power from the net"
		elif(net<2*(-self.sp_safe_budget)):
			msg += " so we're feeding the net above safety margin"
		else:
			msg += " so we're feeding the net but haven't even reached safety margin"
		if(self.dbg_sp):
			self.log(msg)

		### switch on in order ###
		if(self.sp_on_delay_on_until < datetime.datetime.now()):
			if(self.dbg_sp):
				self.log("no switch on delay")
			for d in range(0,len(self.sp_dev)):
				# check if the device is online at all
				try:
					if(self.get_state("sensor."+self.sp_dev[d].split(".")[1].split("_")[0]+"_update")!="0"):
						if(self.dbg_sp):
							self.log(self.sp_dev[d]+" offline")
						continue
				except:
					self.log("getting _update failed for "+self.sp_dev[d])
					pass

				# if the device is OFF we consider to turn it on
				if(self.get_state(self.sp_dev[d]) == "off"):

					# get time constrain if there is one
					if(self.sp_timesensor[d]!=None):
						rem = float(self.get_state(self.sp_timesensor[d]))*60 #convert h to min
					else:
						rem = None

					#self.log("Device "+self.sp_dev[d]+" is off, ran "+str(rem)+" / "+str(self.sp_remaining[d]))
					if(rem==None or rem < self.sp_remaining[d]):
						# only switch on if we would have still extra
						if(net*-1 > self.sp_est_pwr[d]+self.sp_safe_budget*2): 
							# check the constrain
							if(self.sp_constrain[d]!=""):
								v = float(self.get_state(self.sp_constrain[d]))
								if(self.dbg_sp):
									self.log("there is a contrain on "+str(self.sp_dev[d])+" current value: "+str(v)+" and limits["+str(self.sp_constrain_l[d])+","+str(self.sp_constrain_u[d])+"]")
								# only turn in on if the constrain value is within range
								if(v>=self.sp_constrain_l[d] and v<=self.sp_constrain_u[d]):
									self.log("[TURN ON ("+str(new)+"W)] "+self.friendly_name(self.sp_dev[d]))
									self.turn_on(self.sp_dev[d])
									self.sp_on_delay_on_until = datetime.datetime.now()+datetime.timedelta(seconds=self.sp_on_delay[d])
									return # only switch on one at the time
							# no constrain, turn it on directly
							else:
								self.log("[TURN ON ("+str(new)+"W)] "+self.friendly_name(self.sp_dev[d]))
								self.turn_on(self.sp_dev[d])
								self.sp_on_delay_on_until = datetime.datetime.now()+datetime.timedelta(seconds=self.sp_on_delay[d])
								return # only switch on one at the time
		### switch on in order ###
		
		### switch off in invert order ###
		if(self.sp_on_delay_off_until < datetime.datetime.now()):
			for i in range(0,len(self.sp_dev)):
				# revers order
				d = len(self.sp_dev) - i - 1

				# check if the device is online at all
				try:
					if(self.get_state("sensor."+self.sp_dev[d].split(".")[1].split("_")[0]+"_update")!="0"):
						continue
				except:
					self.log("getting _update failed for "+self.sp_dev[d])
					pass

				# we consider to switch if off, but only if it is on
				if(self.get_state(self.sp_dev[d]) == "on"):
					if(self.sp_timesensor[d]!=None):
						rem = float(self.get_state(self.sp_timesensor[d]))*60
#						rem = round(rem+elapsedTime/60,3) # runs every 15 sec, so add a quarter sec
#						self.call_service("mqtt/publish",topic=self.sp_timesensor[d], payload = str(rem), qos = "2", retain="true")
					else:
						rem = None

					#self.log("Device "+self.sp_dev[d]+" is on, ran "+str(rem)+" / "+str(self.sp_remaining[d]))
					if(rem!=None and rem >= self.sp_remaining[d]):
						self.turn_off(self.sp_dev[d])
						self.log("[time out, turn off] "+self.friendly_name(self.sp_dev[d]))
						return
					elif(net > -self.sp_safe_budget): # switch off if we have less then 250W budget, but delay further switching for a couple seconds to see the effect
						self.turn_off(self.sp_dev[d])
						self.log("[power out ("+str(net)+"W), turn off] "+self.friendly_name(self.sp_dev[d]))
						self.sp_on_delay_off_until = datetime.datetime.now()+datetime.timedelta(seconds=self.sp_off_delay[d])
						return
					else:
						if(self.sp_constrain[d]!=""):
							v = float(self.get_state(self.sp_constrain[d]))
							if(v<self.sp_constrain_l[d] or v>self.sp_constrain_u[d]):
								self.turn_off(self.sp_dev[d])
								self.log("[constrain, turn off] "+self.friendly_name(self.sp_dev[d]))
								return

		### switch off in invert order ###


	def update(self, entity="", attribute="", old="", new="", kwargs=""):
		try:
			if(not(isinstance(new,str)) or not(isinstance(old,str))):
				self.log("not a string")
				return

			now = datetime.date.today()
			e_now = float(self.get_state("sensor.dev37_em_tot_grid"))
			e_old = 0
			c = self.get_state("sensor.long_term_power",attribute="all")['attributes']['entries']
			for i in c:
				p = datetime.datetime.strptime(i.split(',')[0], "%Y-%M-%d")
				if(p.year == now.year):
					e_old = float(i.split(',')[1])
					break
			if(e_old):
				days = (now-p.date()).days + 1
				e_con = e_now - e_old
				fix = self.cost_fix_month * 12 / 365 * days
				usage = self.cost_kwh * e_con
				cost = fix + usage
				payment = self.payment_month * 12 / 365 * days
				total = payment - cost

				try:
					self.set_state("sensor.energy_cost",state=str(total))
				except:
					self.log("could not set cost")

				if(self.dbg):
					self.log("using startdate: "+str(p)+" that is "+str(days)+" days ago")
					self.log("Used energy "+str(int(e_con))+" kWh = "+str(int(e_now))+" - "+str(int(e_old)))
					self.log("total: "+str(int(total*100)/100)+" eur = "+str(int(payment*100)/100)+" - "+str(int(cost*100)/100)+" (fix:"+str(int(fix*100)/100)+", usage:"+str(int(usage*100)/100)+")")

			net = float(self.get_state("sensor.dev37_em_stst",attribute="total"))
			net = net/(60*24*1000)
			kaco = float(self.get_state("sensor.pv_daily_int"))
			selfconsume = kaco+net
			self.log("generiert: "+str(kaco)+", verbraucht: "+str(selfconsume)+", eingespeist: "+str(-net))
		except:
			pass

