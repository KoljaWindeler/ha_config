import appdaemon.plugins.hass.hassapi as hass
import datetime, time
import wait
#
# Hellow World App
#
# Args:
#

class workshopWorld(hass.Hass):

    def initialize(self):
        self.log("Starting Workshop Service")
        wait.wait_available(self,["light.dev20","light.dev28","binary_sensor.dev20_button1s"],False)
        self.listen_state(self.group_toggle,"binary_sensor.dev20_button", new="on", old="off")
        self.listen_state(self.vent_toggle,"binary_sensor.dev20_button1s", new="on", old="off")

    def group_toggle(self, entity, attribute, old, new,kwargs):
        self.log("Toggle group lights")
        self.toggle("light.dev20")
        self.toggle("light.dev28")
        self.set_state("binary_sensor.dev59_motion_13",state="on")
        time.sleep(1)
        self.set_state("binary_sensor.dev59_motion_13",state="off")


    def vent_toggle(self, entity, attribute, old, new,kwargs):
        self.log("Toggle ventilation")
        self.toggle("switch.dev28_gpio_4") # bench only
