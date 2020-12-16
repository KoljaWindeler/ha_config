import appdaemon.plugins.hass.hassapi as hass
import datetime, time


#
# Hellow World App
#
# Args:
#

class harmonyWorld(hass.Hass):

    def initialize(self):
        self.log("Starting harmony Service")
        self.remote=["remote.tvhub","remote.beamer_harmony" ]
        self.binary=["harmony","harmony_beamer"]
        self.mp=["media_player.jkw_cast2","media_player.keller"]

        for i in range(0,len(self.remote)):
           self.listen_state(self.state,self.remote[i])
           self.listen_state(self.activity, self.remote[i], attribute = "current_activity", duration=10)

    def activity(self, entity="", attribute="", old="", new="",kwargs=""):
        i=self.remote.index(entity)
        if(i==0):
            att = self.get_state(entity,attribute="current_activity")
            if(not(att.startswith("Music") or att.startswith("Chrom"))): # can be "Chromecast" / "Musik hoeren" / "Chrom TV"
                if(not(self.get_state(self.mp[i])=="off")):
                    self.log("turining mediaplayer "+self.mp[i]+" off")
                    self.turn_off(self.mp[i])

    def state(self, entity="", attribute="", old="", new="",kwargs=""):
        if(not(isinstance(new,str)) or not(isinstance(old,str))):
           self.log("not a string")
           return
        i=self.remote.index(entity)
        if(new=="on"):
            self.set_state("binary_sensor."+self.binary[i],state="on")
            self.log("new "+self.binary[i]+" state "+new+" -> on")
        elif(new=="off"):
            self.set_state("binary_sensor."+self.binary[i],state="off")
            self.log("new "+self.binary[i]+" state "+new+" -> off")



