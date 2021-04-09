import appdaemon.plugins.hass.hassapi as hass
import json
import datetime, time

class TestWorld2(hass.Hass):

	def initialize(self):
		self.log("Starting Test Service2")
#		self.call_service("browser_mod/toast", message= "al" )
#		self.call_service("browser_mod/navigate", navigation_path="testa",deviceID="1f8bb2c3-ef8bbfff")

#		self.call_service("browser_mod/more_info", entity_id="camera.cam_dome1_profile_000",deviceID="1f8bb2c3-ef8bbfff", large=True)
#		self.run_in(self.cl,10)

	def cl(self,arg):
		self.call_service("browser_mod/close_popup",deviceID="1f8bb2c3-ef8bbfff")


    ######################################################

	def pump_on(self, entity="", attribute="", old="", new="", kwargs=""):
		self.log("Starting Pump")
		self.turn_on("switch.dev4_gpio_12")

	def pump_off(self, entity="", attribute="", old="", new="", kwargs=""):
		self.log("Stopping Pump")
		self.turn_off("switch.dev4_gpio_12")
