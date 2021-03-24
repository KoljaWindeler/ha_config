import appdaemon.plugins.hass.hassapi as hass
import json
import datetime, time

class TestWorld2(hass.Hass):

	def initialize(self):
		self.log("Starting Test Service2")
#		for i in range(9,17):
#			self.run_daily(self.pump_on, datetime.time(int(i), 0, 0))
#			self.run_daily(self.pump_off, datetime.time(int(i), 10, 0))

    ######################################################

	def pump_on(self, entity="", attribute="", old="", new="", kwargs=""):
		self.log("Starting Pump")
		self.turn_on("switch.dev4_gpio_12")

	def pump_off(self, entity="", attribute="", old="", new="", kwargs=""):
		self.log("Stopping Pump")
		self.turn_off("switch.dev4_gpio_12")
