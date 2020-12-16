
import appdaemon.plugins.hass.hassapi as hass
import datetime, time
import wait
#
# Hellow World App
#
# Args:
#

class louisaWorld(hass.Hass):

    def initialize(self):
        self.log("Starting louisa Service")
        wait.wait_available(self,["binary_sensor.dev24_button1s","binary_sensor.dev24_button","light.dev55"],False)
        self.listen_state(self.main_toggle,"binary_sensor.dev24_button1s", new = "on", old="off")
        self.listen_state(self.tower_toggle,"binary_sensor.dev24_button", new = "on", old="off")

    def lampinions_toggle(self, entity, attribute, old, new,kwargs):
        self.log("Toggle lampinion")
        self.toggle("light.dev55")

    def tower_toggle(self, entity, attribute, old, new,kwargs):
        self.log("Toggle tower")
        self.toggle("light.dev5")

    def main_toggle(self, entity, attribute, old, new,kwargs):
        self.log("Toggle main")
        self.toggle("light.dev24") # main
