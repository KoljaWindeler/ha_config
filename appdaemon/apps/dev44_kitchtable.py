import appdaemon.plugins.hass.hassapi as hass 
import datetime, time
import wait
#
# Hellow World App
#
# Args:
#

class kitchenTableWorld(hass.Hass):

    def initialize(self):
        self.log("Starting kitchenTable Service")
        wait.wait_available(self,["binary_sensor.dev44_gpio_13","light.dev44_2"],False)
        self.listen_state(self.couch_toggle,"binary_sensor.dev44_gpio_13")
        self.listen_state(self.tower_toggle,"light.dev44")

    def couch_toggle(self, entity, attribute, old, new,kwargs):
        if(old=="unknown"):
           return
        self.log("Toggle couch")
        self.toggle("light.dev44_2")

    def tower_toggle(self, entity, attribute, old, new,kwargs):
        if(new=="on"):
           self.turn_on("light.dev7")
        elif(new=="off"):
           self.turn_off("light.dev7")
