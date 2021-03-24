import appdaemon.plugins.hass.hassapi as hass
import datetime, time
import wait 
#
# Hellow World App
#
# Args:
#

class bedroomWorld(hass.Hass):

    def initialize(self):
        self.log("Starting bedroom Service")
        wait.wait_available(self,["binary_sensor.dev31_button","binary_sensor.dev31_button1s","binary_sensor.dev32_button1s","binary_sensor.dev31_button3s","binary_sensor.dev32_button3s","sensor.dev26_5_hold","sensor.dev26_5_hold","binary_sensor.dev26_gpio_5","light.dev32"],False)
        self.listen_state(self.crip_toggle,"binary_sensor.dev31_button", new = "on", old="off")
        self.listen_state(self.bedlight_off,"binary_sensor.dev31_button1s", new = "on", old="off")
        self.listen_state(self.bedlight_off,"binary_sensor.dev32_button1s", new = "on", old="off")
        self.listen_state(self.bedlight_c_on,"binary_sensor.dev31_button3s", new = "on", old="off")
        self.listen_state(self.bedlight_k_toggle,"binary_sensor.dev32_button", new = "on", old="off")
        self.listen_state(self.bedlight_on,"binary_sensor.dev32_button3s", new = "on", old="off")
        self.listen_state(self.ventilation_toggle,"sensor.dev26_5_hold")
        self.listen_state(self.bedlight_toggle,"binary_sensor.dev26_gpio_5", new = "on", old="off")
        self.listen_state(self.main_toggle,"binary_sensor.dev26_button", new = "on", old="off")
        self.listen_state(self.mpc,"light.dev32", new="on")
        self.listen_state(self.mpc,"sensor.bed_occupancy", old="1", new="2")


    def bedlight_off(self, entity, attribute, old, new,kwargs):
        self.log("Switch bedlight lights off")
        self.turn_off("light.joiner_bedroom")

    def bedlight_on(self, entity, attribute, old, new,kwargs):
        self.log("Switch bedlight lights on")
        self.turn_on("light.joiner_bedroom")

    def bedlight_c_on(self, entity, attribute, old, new,kwargs):
        self.log("Switch csro lights on")
        self.turn_on("light.dev31")

    def bedlight_k_toggle(self, entity, attribute, old, new,kwargs):
        self.log("toggle kolja light")
        self.toggle("light.dev32")

    def bedlight_toggle(self, entity, attribute, old, new,kwargs):
        self.log("Toggle bed lights")
        now = datetime.datetime.now().time()
#        if(now >= datetime.time(20,00,00) or now <= datetime.time(5,00,00)):
#           self.toggle("light.dev19") # crip
#        else:
        self.toggle("light.joiner_bedroom")

    def main_toggle(self, entity, attribute, old, new,kwargs):
        self.log("Toggle main lights")
        self.toggle("light.dev26")

    def ventilation_toggle(self, entity, attribute, old, new,kwargs):
        if(old=="unknown"):
           return
        self.log("Toggle bed vent")
        now = datetime.datetime.now().time()
        if(now >= datetime.time(21,00,00) or now <= datetime.time(5,00,00)):
           if(new =="1"):
              self.toggle("light.joiner_bedroom")
           elif(new =="2"):
              self.toggle("switch.dev26_gpio_15") # ventilator
        elif(new == "1"):
           self.toggle("switch.dev26_gpio_15") # ventilator

    def crip_toggle(self, entity, attribute, old, new,kwargs):
        self.toggle("light.dev19") # crip

    def mpc(self, entity="", attribute="", old="", new="",kwargs=""):
        now = datetime.datetime.now().time()
        if(now >= datetime.time(22,00,00)):
            m="You just went to bed after 10 "
            if(self.get_state("switch.dev58_gpio_12")=="on"):
               t="media pc on"
               m+="and the media pc is still running"
               self.call_service("notify/pb", title=t, message=m)
            if(self.get_state("binary_sensor.dev17_motion")=="on"):
               t="Cellar door open"
               m+="the cellar door is still open!"
               self.call_service("notify/pb", title=t, message=m)
               self.call_service("notify/pb_c", title=t, message=m)
            if(float(self.get_state("sensor.dev37_ads_ch8_kw"))>30):
               t="Garage light"
               m+="the garage light is still on!"
               self.call_service("notify/pb", title=t, message=m)
               self.call_service("notify/pb_c", title=t, message=m)

