import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, time
import os
import wait

class EntranceWorld2(hass.Hass):

    def initialize(self):
        self.log("Starting Entrance Service 2")
        wait.wait_available(self,["binary_sensor.dev54_button","binary_sensor.dev17_motion","person.kolja_2","person.caro_2","proximity.caro_home","proximity.kolja_home"],False)

        try:
          os.makedirs('/tmp/cams')
        except:
          pass

        self.ring_cnt = [0,0,0]
        self.listen_state(self.ring, "binary_sensor.dev54_button", new = "on") #klingel
        self.listen_state(self.backdoor, "binary_sensor.dev17_motion", new = "on") #klingel

        self.run_daily(self.six, time(6, 0, 0))
        self.run_daily(self.twentytwo, time(22, 0, 0))
        self.run_daily(self.twentythree, time(23, 0, 0))
        try:
           self.run_at_sunrise(self.sunrise, offset = 30 * 60)
           self.run_at_sunset(self.sunset, offset = 15 * 60)
        except:
           pass
        self.listen_state(self.caro_home, "person.caro_2", new = "home", duration = 10*60, arg1="Caro home")  # everyone is home for 10 min
        self.listen_state(self.kolja_home, "person.kolja_2", new = "home", duration = 10*60, arg1="Kolja home")  # everyone is home for 10 min
        self.listen_state(self.approaching, "proximity.caro_home")
        self.listen_state(self.approaching, "proximity.kolja_home")

        now = datetime.now()
        self.recording_start=[now,now]
        self.listen_state(self.rec_front_door, "binary_sensor.mymotiondetectorrule_cell_motion_detection")
        self.listen_state(self.rec_garden, "binary_sensor.mymotiondetectorrule_cell_motion_detection_2")

    ######################################################

    def six(self, entity="", attribute="", old="", new="", kwargs=""):
        self.outside_on("6am")
    def twentytwo(self, entity="", attribute="", old="", new="", kwargs=""):
        self.outside("22pm")
    def twentythree(self, entity="", attribute="", old="", new="", kwargs=""):
        self.outside("23pm")
    def sunrise(self, entity="", attribute="", old="", new="", kwargs=""):
        self.outside("Sunrise")
    def sunset(self, entity="", attribute="", old="", new="", kwargs=""):
        self.outside("Senset")
    def kolja_home(self, entity="", attribute="", old="", new="", kwargs=""):
        self.outside("Kolja home")
    def caro_home(self, entity="", attribute="", old="", new="", kwargs=""):
        self.outside("Caro home")

    ######################################################

    def rec_front_door(self, entity="", attribute="", old="", new="",kwargs=""):
        if(new == "on"):
           now = datetime.now()
           if((now-self.recording_start[0]).total_seconds()>30):
              fn = "/tmp/cams/front_door_"+str(self.ring_cnt[0]).zfill(2) # save filename without filetype ending 
              self.log("========= front door motion -> recording 20 sec to "+fn+" ========================") # log output
              self.ring_cnt[0] = (self.ring_cnt[0] + 1) % 40 # inc
              self.call_service("camera/record",   entity_id="camera.cam_dome1_profile_000", filename=fn+".mp4", duration="25", lookback="5") # save video
              self.recording_start[0] = now
    def rec_garden(self, entity="", attribute="", old="", new="",kwargs=""):
        if(new == "on"):
           now = datetime.now()
           if((now-self.recording_start[1]).total_seconds()>30):
              fn = "/tmp/cams/garden_"+str(self.ring_cnt[2]).zfill(2) # save filename without filetype ending 
              self.log("========= garden motion -> recording 20 sec to "+fn+" ========================") # log output
              self.ring_cnt[2] = (self.ring_cnt[2] + 1) % 40 # inc
              self.call_service("camera/record",   entity_id="camera.cam_dome3_profile_000", filename=fn+".mp4", duration="25", lookback="5") # save video
              self.recording_start[1] = now

    ######################################################

    def ring(self, entity, attribute, old, new,kwargs):
        self.log("========= ring ========================") # log output
        self.outside_wish("on!",kwargs) # turn light on

        # generate filename, even if we won't record 
        fn = "/tmp/cams/ring_"+str(self.ring_cnt[0]).zfill(2) # save filename without filetype ending
        self.ring_cnt[0] = (self.ring_cnt[0] + 1) % 40 # inc

        # grab screenshot and send that via MSG
        self.call_service("camera/snapshot", entity_id="camera.cam_dome1_profile_000", filename=fn+".jpg") # save snapshot
        self.notify_vid(arg={"arg":{"t":"Frontdoor","m":"Ding Dong","d":{"file":""}}}) # send info
        self.run_in(self.notify_vid,1, arg={"t":"Frontdoor image","m":"Sensor triggered","d":{"file": fn+".jpg"}}) # send image

        # check we we should start our own recording of it that already exists driven by motion
        now = datetime.now()
        if((now-self.recording_start[0]).total_seconds()>30):
           # camera is NOT recording, driven by motion
           self.call_service("camera/record", entity_id="camera.cam_dome1_profile_000", filename=fn+".mp4", duration="25", lookback="5") # save video
        else:
           # camera IS recording
           #self.log("last motion triggered recording started less then 30 sec ago, so I'll take that video. ring_cnt[0]="+str(self.ring_cnt[0])) # log output
           fn = "/tmp/cams/front_door_"+str((self.ring_cnt[0]-2+40)%40).zfill(2) # save filename without filetype ending 
           #self.log("so our filename will be: "+fn)

        # send link to video
        self.run_in(self.notify_vid,20,arg={"t":"Frontdoor video","m":"http://192.168.2.84:8081/"+fn.replace("/tmp/","")+".mp4","d":{"file":""}}) # send link to video
        self.run_in(self.outside,5*60) # turn off after 5 min

        # open stream on screen
        self.set_state("binary_sensor.dev16_motion", state = "on")
        self.call_service("browser_mod/more_info", entity_id="camera.cam_dome1_profile_000",deviceID="33f1c020-593396b4", large=True)
        self.run_in(self.close_info,20)

    def close_info(self,arg):
        self.set_state("binary_sensor.dev16_motion", state = "off")
        self.call_service("browser_mod/close_popup",deviceID="33f1c020-593396b4")

    def backdoor(self, entity="", attribute="", old="", new="",kwargs=""):
        self.log("========= backdoor ========================") # log output
        fn = "/tmp/cams/backdoor_"+str(self.ring_cnt[1]).zfill(2) # save filename without firetype ending
        self.ring_cnt[1] = (self.ring_cnt[1] + 1) % 40 # inc
        self.call_service("camera/record",   entity_id="camera.cam_dome2_profile_000", filename=fn+".mp4", duration="20", lookback="5") # save video
        self.call_service("camera/snapshot", entity_id="camera.cam_dome2_profile_000", filename=fn+".jpg") # save snapshot
        if(self.get_state("input_boolean.alarm_system") == "on" and self.get_state("binary_sensor.someone_is_home") == "off"):
           self.notify_vid(arg={"arg":{"t":"Backdoor","m":"Triggered","d":{"file":""}}}) # send info
           self.run_in(self.notify_vid,1, arg={"t":"Backdoor image","m":"Sensor triggered","d":{"file": fn+".jpg"}}) # send image
           self.run_in(self.notify_vid,20,arg={"t":"Backdoor video","m":"http://192.168.2.84:8081/"+fn.replace("/tmp/","")+".mp4","d":{"file":""}}) # send link to video

    def notify_vid(self, arg):
        #self.log(arg)
        t=arg["arg"]["t"]
        m=arg["arg"]["m"]
        d=arg["arg"]["d"]
        self.log("sending notification: "+t)
        if(d["file"]!=""):
           self.call_service("notify/pb",   title=t, message=m, data=d)
           self.call_service("notify/pb_c", title=t, message=m, data=d)
        else:
           self.call_service("notify/pb",   title=t, message=m)
           self.call_service("notify/pb_c", title=t, message=m)

    def approaching(self, entity, attribute, old, new,kwargs):
        #self.log("proxy")
        #self.log(dir)
        #self.log(dist)
        if(self.get_state("person.caro_2") == "home" and self.get_state("person.kolja_2") == "home"):
            self.log("ignoring approach, both home")
            return 0
        if(attribute == "state"):
            dir = self.get_state(entity, attribute="dir_of_travel")
            dist = self.get_state(entity)
            if(dir == "towards" and attribute == "state"):
                if(int(dist) < 3):
                    self.log("========= approach ========================")
                    #self.log(repr(kwargs["arg1"])
                    self.log(entity+" is approaching home")
                    self.outside_wish("on",kwargs)

    def outside_on(self, title):
        self.log("============= outside on ====================")
        self.log(repr(title))
        self.outside_wish("on")

    def outside(self, title):
        self.log("============== outside ===================")
        self.log(repr(title))
        self.outside_wish("auto")

    def outside_wish(self,w,kwargs=""):
        #self.log(repr(kwargs))

        now = datetime.now().time()
        ele = float(self.get_state("sun.sun", attribute="elevation"))
        rising = self.get_state("sun.sun", attribute="rising")
        self.log("current elevation "+str(ele))

        if(w=="on!"):
            self.log("COMMAND! to turn on lights")
            self.turn_on("light.joiner_outdoor")
            self.log("=================================")
        elif(w=="on"):
            self.log("request to turn on lights")
            if(ele < 2):
                self.log("request granted, sun is low, turning on")
                self.turn_on("light.joiner_outdoor")
                self.log("=================================")
            else:
                self.log("request rejected, sun is up, turning off")
                self.turn_off("light.joiner_outdoor")
                self.log("=================================")
        else: #if(w=="auto"):
            self.log("request in auto mode")
            if(now >= time(23,00,00)):
                self.log("after 11 turn off")
                self.turn_off("light.joiner_outdoor")
            elif(now >= time(22,00,00) and self.get_state("binary_sensor.everyone_is_home") == "on"):
                self.log("after 10 and everyone is home, turn off")
                self.turn_off("light.joiner_outdoor")
            elif(ele < 2 and now >= time(13,0,0)):
                self.log("sun low and falling, must be evening, turn on")
                self.turn_on("light.joiner_outdoor")
            elif(ele >= 2):
                self.log("sun is up, turn off")
                self.turn_off("light.joiner_outdoor")
            elif(now >= time(6,0,0)):
                self.log(">= six AM but still dark, turn on")
                self.turn_on("light.joiner_outdoor")
            else:
                self.log("before six in the nigth, turn off")
                self.turn_off("light.joiner_outdoor")
            self.log("=================================")



