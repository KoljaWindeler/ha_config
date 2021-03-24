import appdaemon.plugins.hass.hassapi as hass 
import datetime, time
import wait 
from random import *
#
# Hellow World App
#
# Args:
#

class NfcWorld(hass.Hass):

	def initialize(self):
		self.log("Starting nfc Service")
		self.listen_event(self.tag,"tag_scanned")
		self.listen_state(self.pp,"binary_sensor.dev23_button2s", new = "on", old="off")
		self.listen_state(self.pp_unten,"binary_sensor.dev34_button2s", new = "on", old="off")

	def pp(self, entity, attribute, old, new,kwargs):
		self.log("carlo 2s")
		if(self.get_state("input_boolean.carlo_switch_lock")=="off"):
			self.tag(' ',{'tag_id':'e2976d7b-d508-4a31-b308-20d6ea4432ca'})
		else:
			self.log("lock")

	def pp_unten(self, entity, attribute, old, new,kwargs):
		self.log("carlo unten 2s")
		self.tag(' ',{'tag_id':'3ffe57f5-0dcd-45ad-a6b6-3cdaa170cfe0'})


	def tag(self, event, data, kwargs=None):
		self.log("Tag")
		self.log(data)
		_id = False
		_type = False
		_vol=0.3
		_e = "media_player.ytube_music_player_carlo"
		_shuffle=True
		_repeat = 'all'
		_source = 'carlo'
		if(data['tag_id'] == '13541d80-11ed-48f6-94ae-9237029dce7b'
		    or data['tag_id'] == 'BB-97-A5-00'): # Karte: Leo Lausemaus
			_id = "PLZvjm51R8SGs1bY2L--3KbwZqWWU6ZKYp"
			_type = "playlist"
		elif(data['tag_id'] == 'ea1e868f-867a-412c-a638-9dfa1de642cd'): # schneeballschlacht
			_id = "lT9zR0eFWYM"
			_type = "track"
		elif(data['tag_id'] == 'cfb587ae-895e-4ff8-a77c-54f9cf961819'): # licht aus sticker
			self.turn_off("light.dev23")
			self.turn_off("light.dev33")
		elif(data['tag_id'] == '748e245f-7a20-4326-b746-07bb31df9c68'
		     or data['tag_id'] == 'DF-7B-8A-3D'): # geburtstag
			_id = 'MPREb_o9nL4EQho3G'
			_type = "album"
			_vol=0.32
			_shuffle=False
			_repeat='off'
		elif(data['tag_id'] == 'bf3af0d4-0818-4927-94a8-b2d4c7f19d68'
		      or data['tag_id'] == '89-D1-8A-3D'): # wettlauf gegen die zeit
			_id = 'MPREb_hu5FRQNIOav'
			_type = "album"
			_vol=0.32
			_shuffle=False
			_repeat='off'
		elif(data['tag_id'] == 'ec63e494-c269-4a6e-b4c1-e87351204780'
		      or data['tag_id'] == 'C0-C1-E5-02'): # ploetzlich filmheld
			_id = 'MPREb_oYAOqxEFEvc'
			_type = "album"
			_vol=0.32
			_shuffle=False
			_repeat='off'
		elif(data['tag_id'] == '1a06a12c-4e8b-4bee-9b99-475c0a2ab2c3'): # ausserirdische
			_id = 'MPREb_V9RBwfsOz3e'
			_type = "album"
			_vol=0.32
			_shuffle=False
			_repeat='off'
		elif(data['tag_id'] == '630033b9-ce01-4d97-87d1-f2c725697758'
		     or data['tag_id'] == '1D-78-8A-3D'): # pinguine
			_id = 'MPREb_OKClsYnH8Fq'
			_type = "album"
			_vol=0.32
			_shuffle=False
			_repeat='off'
		elif(data['tag_id'] == '5aa6ffdf-857b-4a06-b96a-d23638d2f658'
		      or data['tag_id'] == '04-07-EE-DA-5E-5C-81'): # schatz
			_id = 'MPREb_BfmgAjML3Zw'
			_type = "album"
			_vol=0.32
			_shuffle=False
			_repeat='off'
		elif(data['tag_id'] == '67ae6715-9e67-427e-b893-e1cd26fedb54'): # garage
			self.turn_on("switch.dev8")
		elif(data['tag_id'] == 'e2976d7b-d508-4a31-b308-20d6ea4432c1'): # random im keller
			_e = "media_player.ytube_music_player_keller"
			if(self.get_state(_e)=='playing'):
				self.turn_off(_e)
			else:
				_id = 'RDTMAK5uy_kset8DisdE7LSD4TNjEVvrKRTmG7a56sY'
				_source = 'keller_2'
				_type = "channel"
				_vol=1
		elif(data['tag_id'] == 'de37d2f3-cf0d-476c-af63-7ab951693347'): #holz tag feuermann sam
			_ids = []
			_ids.append('MPREb_o9nL4EQho3G')
			_ids.append('MPREb_hu5FRQNIOav')
			_ids.append('MPREb_BfmgAjML3Zw')
			_ids.append('MPREb_OKClsYnH8Fq')
			_ids.append('MPREb_oYAOqxEFEvc')
			_type = "album"
			_vol=0.32
			_shuffle=False
			_repeat='off'
			_id = _ids[randint(0,len(_ids))]
		elif(data['tag_id'] == '872d21c7-5f80-4632-8965-8e9aa0f3ab8a'): #holz tag rabe socke
			_ids = []
			_ids.append('MPREb_BelcOuwzEaS')
			_ids.append('MPREb_g5nRHob42pW')
			_ids.append('MPREb_AOOtClRKUZR')
			_ids.append('MPREb_Jf7dNA0ddoZ')
			_ids.append('MPREb_m9nj52x8IYl')
			_ids.append('MPREb_dM8DvZMFcUQ')
			_ids.append('MPREb_AOOtClRKUZR')
			_ids.append('MPREb_koF1MsWFxjb')
			_type = "album"
			_vol=0.32
			_shuffle=False
			_repeat='off'
			_id = _ids[randint(0,len(_ids))]
		elif(data['tag_id'] == 'e2976d7b-d508-4a31-b308-20d6ea4432ca'
		   or data['tag_id'] == '3ffe57f5-0dcd-45ad-a6b6-3cdaa170cfe0'
		   or data['tag_id'] == '41e029b0-3b24-4397-9d09-ebb811c01ee1'): # random Pawpatrol
			_ids = []
			_ids.append('MPREb_B4B3YfQfOLG') # Folge 120: Die Überschwemmung
			_ids.append('MPREb_2BwoDLCJFTf') # Folge 117: Das versunkene Piratenschiff
			_ids.append('MPREb_I93hLz1mWDR') # Folge 123: Tiere im Schloss
			_ids.append('MPREb_CxBREHcOAvV') # Folge 118: Ein Wal braucht Hilfe
			_ids.append('MPREb_qUZFOtp5Fji') # Folge 119: Der Unterwasser-Vulkan
			_ids.append('MPREb_TEWBxwfV8f1') # Folge 122: Ein königliches Konzert
			_ids.append('MPREb_AliGeA4dNYR') # Folge 121: Der Filmdreh
			_ids.append('MPREb_KON9SF0QSeT') # Folge 116: Die Super-Zwillinge
			_ids.append('MPREb_0bPy3w1blMd') # Folge 115: Berthold und die Superkätzchen
			_ids.append('MPREb_ENa8TCrYFbH') # Folge 108: Die Schaf-Schermaschine
			_ids.append('MPREb_2RzzvIla4Tf') # Folge 110: Danny X und sein Flusspferd
			_ids.append('MPREb_prc0nqVHZtj') # Folge 107: Die Schildkröten-Eie
			_ids.append('MPREb_1Qm2AViTiIq') # Folge 109: Francois, der Pinguin
			_ids.append('MPREb_ByD9husVZOL') # Folge 112: Die Katzenshow
			_ids.append('MPREb_WuV9AGdH5Ex') # Folge 113: Jake hat Geburtstag
			_ids.append('MPREb_K2fmueNPLTY') # Folge 111: Eine eisige Rettung
			_ids.append('MPREb_oUu5qOYnmql') # Folge 114: Die wilde Abfahrt
			_ids.append('MPREb_z23mfdMzkgn') # Folge 102: Auf Safari
			_ids.append('MPREb_Klxbd7oE09j') # Folge 100: Die traurige Prinzessin
			_ids.append('MPREb_o3VAvLD7sTj') # Folge 101: Das Schlossgespenst
			_ids.append('MPREb_0cR5FDmP86k') # Folge 105: Paket in Gefahr
			_ids.append('MPREb_T1GITWEsMhI') # Folge 106: Frau Frosch-Bürgermeisterin
			_ids.append('MPREb_2A5ldvvEWvY') # Folge 104: Flugkatze in Not
			_ids.append('MPREb_bodO7r2GV3R') # Folge 103: Affen-Alarm
			_ids.append('MPREb_d6Oq4u6NI4a') # Folge 95: Der Piratenzauber
			_ids.append('MPREb_PNLoDaeRXlc') # Folge 96: Die eingefrorene Flunder
			_ids.append('MPREb_VIqSZ2F9oVB') # Folge 99: Die Suche nach der Krone
			_ids.append('MPREb_vtKxtWIxB8l') # Folge 98: Die Fellfreunde retten Wufflantis
			_ids.append('MPREb_Qh7PjK8hJp5') # Folge 97: Das Ein-Leopard-Löwe-Horn
			_ids.append('MPREb_QBxXGoEBC1N') # Folge 94: Künstler in Not
			_ids.append('MPREb_jlGRW5KhyiX') # Folge 90: Die Riesenpflanze
			_ids.append('MPREb_fwYi1YQRX18') # Folge 92: Das Tintenfisch-Baby
			_ids.append('MPREb_j7a6EarEAMH') # Folge 93: Der seltsame Hai
			_ids.append('MPREb_Kz2uSvCh0Lk') # Folge 91: Der Magnet
			_ids.append('MPREb_A8KbY42cIqX') # Folge 89: Die Winterwunder-Show
			_ids.append('MPREb_1o0XLQazGHW') # Folge 13: Was für ein Zirkus
			_ids.append('MPREb_PVMmKQATGa3') # Folge 09: Die Gänse kommen
			_ids.append('MPREb_4sQFW5rvsS0') # Folge 18: Rettung aus höchster Not
			_ids.append('MPREb_d4HEgBrIdIL') # Folge 12: Das Schneemonster
			_ids.append('MPREb_S4u6Mx9XN55') # Folge 17: Leckerlis auf Eis
			_ids.append('MPREb_yMgHiDPVoxY') # Folge 10: Die Ballon-Wettfahrt
			_ids.append('MPREb_lELbL2mxIT2') # Folge 14: Hunde retten Huhn
			_ids.append('MPREb_CJDywzI1esO') # Folge 11: Hunde im Schnee
			_ids.append('MPREb_NLlYOMgUWD1') # Folge 15: Der Boxenstopp
			_ids.append('MPREb_OKYIb9q2cJt') # Folge 16: Schneller als die Feuerwehr
			_ids.append('MPREb_NwHAeuuBhyb') # Folge 19: Das Geisterschiff
			_ids.append('MPREb_gSl1VVQW0lk') # Folge 33: Die Ostereiersuche
			_ids.append('MPREb_4R414j4ecyK') # Folge 24: Die Hundeschau
			_ids.append('MPREb_YBD9RXu3iZb') # Folge 23: Das Kaninchen-Problem
			_ids.append('MPREb_cR9EGIvG37d') # Folge 26: Großvater über Bord
			_ids.append('MPREb_99TlZMkMd2g') # Folge 21: Rubble, der Fundhund
			_ids.append('MPREb_vHxCLVc06iL') # Folge 22: Die Walross-Rettung
			_ids.append('MPREb_My1GoTaANQ8') # Folge 85: Der Freundschaftstag
			_ids.append('MPREb_th1WexqOtfP') # Folge 84: Fliegende Fellfreunde
			_ids.append('MPREb_BofzBXZkRv4') # Folge 20: Die Paw Patrol rettet Weihnachten
			_ids.append('MPREb_BsNK1d4e4hd') # Folge 87: Der sprechende Papagei
			_ids.append('MPREb_qK3akifXHxi') # Folge 88: Die Nacht des magischen Meer-Mondes
			_ids.append('MPREb_3iVWCt3VEF9') # Folge 86: Hier kommt Tracker
			_ids.append('MPREb_7K2exyrVBHA') # Folge 31: Fellfreunde auf dem Trockenen
			_ids.append('MPREb_wMPCb9AOQGV') # Folge 37: Der kleine Tut
			_ids.append('MPREb_9e3yh2k2Zka') # Folge 36: Großes Affentheater
			_ids.append('MPREb_1tlWguKD34J') # Folge 32: Der Hundezirkus
			_ids.append('MPREb_s4Fr8Mo5eNo') # Folge 35: Ryders Roboterhund
			_ids.append('MPREb_cAKLUHCTozO') # Folge 27: Kühe tanzen aus der Reihe
			_ids.append('MPREb_9dfi9M4yYQn') # Folge 28: Alex auf Rettungsmission
			_ids.append('MPREb_irrjSnXQI0l') # Folge 34: Der Super-Fellfreund
			_ids.append('MPREb_PSNR9474uIL') # Folge 30: Der Stromausfall
			_ids.append('MPREb_NueyMb2uCQl') # Folge 29: Alex erster Schultag
			_ids.append('MPREb_68G9wlzEYMk') # Folge 73: Die Meerfellfreunde
			_ids.append('MPREb_O7LhEqwTzsd') # Folge 77: François, der Seiltänzer
			_ids.append('MPREb_YsOsnWnuxS5') # Folge 63: Die Kältewelle
			_ids.append('MPREb_tFG9HljxWLA') # Folge 81: Das Glückshalsband
			_ids.append('MPREb_WMg7qvLk22S') # Folge 75: Kätzchen-Chaos
			_ids.append('MPREb_yggjPppx61C') # Folge 44: Der Leuchtturm-Boogie
			_ids.append('MPREb_EDHkLrBIRV7') # Folge 47: Der Kuchenback-Wettbewerb
			_ids.append('MPREb_JJQlEzLkzMe') # Folge 40: Die Pfotenfinder
			_ids.append('MPREb_ulEVXWruLRZ') # Folge 54: Die Parade
			_ids.append('MPREb_bq75Y1fSpEC') # Folge 39: Der Wackelzahn
			_ids.append('MPREb_76DG15bRQam') # Folge 55: Auf Tauchstation
			_ids.append('MPREb_D6gnbyumjo4') # Folge 64: Das Basketballspiel
			_ids.append('MPREb_uy9VAuaIxd8') # Folge 78: Im Goldrausch
			_ids.append('MPREb_dzz3t4dhWFv') # Folge 62: Der Schafhüte-Wettbewerb
			_ids.append('MPREb_n2B58GhQ0ix') # Folge 52: Der fliegende Frosch
			_ids.append('MPREb_Vuhw876ADlW') # Folge 50: Der Delfin-Freund
			_ids.append('MPREb_OHzqkPDzHhF') # Folge 38: Der Flederfreund
			_ids.append('MPREb_2GjP7X8L38M') # Folge 58: Das Ritterspiel
			_ids.append('MPREb_wInzVmMicT8') # Folge 71: Der Papagei
			_ids.append('MPREb_vaNGs9bAg27') # Folge 48: Der Piratenschatz
			_ids.append('MPREb_ZCXLgBkomHQ') # Folge 61: Einsatz im Dschungel
			_ids.append('MPREb_eMf7S6VDlvw') # Folge 57: Geisterstunde
			_ids.append('MPREb_QzozGmbRc2j') # Folge 46: Das große Rennen
			_ids.append('MPREb_FjzpcIj7AKE') # Folge 82: Die Mini Patrol
			_ids.append('MPREb_Mf5JcvhOWMc') # Folge 45: Ryder in Not
			_ids.append('MPREb_3QqT4fNtOEL') # Folge 79: Der Paw Patroler ist weg
			_ids.append('MPREb_CpeuQQGn1Re') # Folge 68: Maiskolben vom Grill
			_ids.append('MPREb_I1goefVnd11') # Folge 67: Der Talentwettbewerb
			_ids.append('MPREb_Hr3ifqKNxz3') # Folge 65: Ein Ass in der Luft
			_ids.append('MPREb_sUIHIBHdYdR') # Folge 60: Ein neuer Fellfreund
			_ids.append('MPREb_mmHHczSj23x') # Folge 83: Der verlorene Zahn
			_ids.append('MPREb_eGrCUxYHZAC') # Folge 51: Der Besucher aus dem All
			_ids.append('MPREb_eAFPhe8uxjv') # Folge 49: Pinguine an Bord
			_ids.append('MPREb_0ZPNgqNswNb') # Folge 53: Jake in der Klemme
			_ids.append('MPREb_mOlvSg94cQS') # Folge 42: Die Riesenbohnen-Ranke
			_ids.append('MPREb_95Y4i9Tw6rS') # Folge 80: Das Fußballspiel
			_ids.append('MPREb_YwwmYaEhNj8') # Folge 41: Die Schildkröten-Krise
			_ids.append('MPREb_r9ZUNFEY9qf') # Folge 56: Biberprobleme
			_ids.append('MPREb_uU7wH094jlX') # Folge 43: Cousin Francois
			_ids.append('MPREb_Ehrw3NJFpt4') # Folge 66: Hochzeit in Gefahr
			_ids.append('MPREb_2WL6lPyhUHm') # Folge 74: Die Elefanten-Familie
			_ids.append('MPREb_AuwrCic3h1k') # Folge 76: Der Flaschengeist
			_ids.append('MPREb_4yUdafB4Rn3') # Folge 70: Rettet die Rehe
			_ids.append('MPREb_DqHarXpdE8i') # Folge 72: Der Bienenumzug
			_ids.append('MPREb_IOBAHO6BipW') # Folge 25: Der Ölteppich
			_ids.append('MPREb_4xIvm4HjXcO') # Folge 69: Marshall allein zu Haus
			_ids.append('MPREb_lgJy13Rp3TW') # Folge 04: Das Riesenbaby
			_ids.append('MPREb_UkX9Vxi3oxC') # Folge 01: Rocky will nicht baden
			_ids.append('MPREb_tPx9LR7Uwr2') # Folge 02: Das große Herbstfest
			_ids.append('MPREb_dXIessQGFia') # Folge 07: Der Fellfreunde Boogie
			_ids.append('MPREb_RZuh3jOP73s') # Folge 05: Die Katz-A-Strophe
			_ids.append('MPREb_QJDCEnbLC0l') # Folge 03: Die Rettung der Meeresschildkröten
			_ids.append('MPREb_o9y8shqP8S0') # Folge 06: Die Zugrettung
			_ids.append('MPREb_26OinQqVVdi') # Folge 08: Hunde im Nebel
			_id = _ids[randint(0,len(_ids))]
			_shuffle=False
			_repeat='off'
			_type = "album"
			if(data['tag_id'] == '3ffe57f5-0dcd-45ad-a6b6-3cdaa170cfe0'): # random Pawpatrol
				_vol=1
				_e="media_player.ytube_music_player"
				_source = 'jkw_cast2'
			else:
				_vol=0.32
		if(_id and _type):
			self.turn_off(_e)
			self.call_service("media_player/shuffle_set", entity_id=_e, shuffle=_shuffle)
			self.call_service("media_player/repeat_set", entity_id=_e, repeat=_repeat)
			self.call_service("media_player/select_source", entity_id=_e, source=_source)
			self.call_service("media_player/volume_set", entity_id=_e, volume_level=_vol)
			self.call_service("media_player/play_media", entity_id=_e, media_content_id=_id, media_content_type=_type)
