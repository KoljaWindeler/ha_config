from homeassistant.components.sensor import PLATFORM_SCHEMA, ENTITY_ID_FORMAT
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
import logging
import datetime
import traceback
from collections import OrderedDict
from ytmusicapi import YTMusic


from homeassistant.const import (
	EVENT_HOMEASSISTANT_START,
	ATTR_ENTITY_ID,
	CONF_DEVICE_ID,
	CONF_USERNAME,
	CONF_PASSWORD,
	STATE_PLAYING,
	STATE_PAUSED,
	STATE_OFF,
	STATE_IDLE,
)

from homeassistant.components.media_player import (
	MediaPlayerEntity,
	PLATFORM_SCHEMA,
	SERVICE_TURN_ON,
	SERVICE_TURN_OFF,
	SERVICE_PLAY_MEDIA,
	SERVICE_MEDIA_PAUSE,
	SERVICE_VOLUME_UP,
	SERVICE_VOLUME_DOWN,
	SERVICE_VOLUME_SET,
	ATTR_MEDIA_VOLUME_LEVEL,
	ATTR_MEDIA_CONTENT_ID,
	ATTR_MEDIA_CONTENT_TYPE,
	DOMAIN as DOMAIN_MP,
)

from homeassistant.components.media_player.const import (
	MEDIA_TYPE_MUSIC,
	SUPPORT_STOP,
	SUPPORT_PLAY,
	SUPPORT_PAUSE,
	SUPPORT_PLAY_MEDIA,
	SUPPORT_PREVIOUS_TRACK,
	SUPPORT_NEXT_TRACK,
	SUPPORT_VOLUME_MUTE,
 	SUPPORT_VOLUME_SET,
	SUPPORT_VOLUME_STEP,
	SUPPORT_TURN_ON,
	SUPPORT_TURN_OFF,
	SUPPORT_SHUFFLE_SET,
)

# Should be equal to the name of your component.
PLATFORM = "media_player"
DOMAIN = "ytube_music_player"
VERSION = "0.1.5"
ISSUE_URL = "https://github.com/koljawindeler/ytube_music_player/issues"

SUPPORT_YTUBEMUSIC_PLAYER = (
	SUPPORT_TURN_ON
	| SUPPORT_TURN_OFF
	| SUPPORT_PLAY
	| SUPPORT_PAUSE
	| SUPPORT_STOP
	| SUPPORT_VOLUME_SET
	| SUPPORT_VOLUME_STEP
	| SUPPORT_VOLUME_MUTE
	| SUPPORT_PREVIOUS_TRACK
	| SUPPORT_NEXT_TRACK
	| SUPPORT_SHUFFLE_SET
)

CONF_RECEIVERS = 'speakers'	 # list of speakers (media_players)
CONF_HEADER_PATH = 'header_path'
CONF_SHUFFLE = 'shuffle'
CONF_SHUFFLE_MODE = 'shuffle_mode'
CONF_COOKIE = 'cookie'
CONF_BRAND_ID = 'brand_id'

CONF_SELECT_SOURCE = 'select_source'
CONF_SELECT_PLAYLIST = 'select_playlist'
CONF_SELECT_SPEAKERS = 'select_speakers'
CONF_SELECT_PLAYMODE = 'select_playmode'
CONF_SELECT_PLAYCONTINUOUS = 'select_playcontinuous'

DEFAULT_SELECT_PLAYCONTINUOUS = DOMAIN + '_playcontinuous'
DEFAULT_SELECT_SOURCE = DOMAIN + '_source'
DEFAULT_SELECT_PLAYLIST = DOMAIN + '_playlist'
DEFAULT_SELECT_PLAYMODE = DOMAIN + '_playmode'
DEFAULT_SELECT_SPEAKERS = DOMAIN + '_speakers'
DEFAULT_HEADER_FILENAME = 'ytube_header.json'

DEFAULT_SHUFFLE_MODE = 1
DEFAULT_SHUFFLE = True

ERROR_COOKIE = 'error_cookie'
ERROR_AUTH_USER = 'error_auth_user'
ERROR_GENERIC = 'error_generic'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend = vol.Schema({
	DOMAIN: vol.Schema({
		vol.Optional(CONF_RECEIVERS): cv.string,
		vol.Optional(CONF_HEADER_PATH, default=DEFAULT_HEADER_FILENAME): cv.string,
		vol.Optional(CONF_SELECT_SOURCE, default=DEFAULT_SELECT_SOURCE): cv.string,
		vol.Optional(CONF_SELECT_PLAYLIST, default=DEFAULT_SELECT_PLAYLIST): cv.string,
		vol.Optional(CONF_SELECT_PLAYMODE, default=DEFAULT_SELECT_PLAYMODE): cv.string,
		vol.Optional(CONF_SELECT_SPEAKERS, default=DEFAULT_SELECT_SPEAKERS): cv.string,
	})
}, extra=vol.ALLOW_EXTRA)

# Shortcut for the logger
_LOGGER = logging.getLogger(__name__)


def check_data(user_input,path):
	"""Check validity of the provided date."""
	ret = {}
	if(CONF_COOKIE in user_input):
		try:
			# sadly config flow will not allow to have a multiline text field
			# we get a looong string that we've to rearrange into multiline for ytmusic

			# the only thing we need is cookie + x-goog-authuser, lets try to cut this out
			# so the fields are written like 'identifier':'value', but some values actually have ':' inside, bummer.
			c = user_input[CONF_COOKIE]
			clean_cookie = ""
			clean_x_goog_authuser = ""
			## lets try to find the cookie part
			cookie_pos = c.lower().find('cookie')
			if(cookie_pos>=0):
				#_LOGGER.debug("found cookie in text")
				cookie_end = c[cookie_pos:]
				cookie_end_split = cookie_end.split(':')
				if(len(cookie_end_split)>=3):
					#_LOGGER.debug("found three or more sections")
					cookie_length_last_field = cookie_end_split[2].rfind(' ')
					if(cookie_length_last_field>=0):
						#_LOGGER.debug("found a space")
						cookie_length = len(cookie_end_split[0])+1+len(cookie_end_split[1])+1+cookie_length_last_field
						clean_cookie = c[cookie_pos:cookie_pos+cookie_length]
						#_LOGGER.debug(clean_cookie)
			## lets try to find x-auth-part
			xauth_pos = c.lower().find('x-goog-authuser: ')
			if(xauth_pos>=0):
				#_LOGGER.debug("found x-goog-authuser in text")
				#_LOGGER.debug(c[xauth_pos+len('x-goog-authuser: '):])
				xauth_len = c[xauth_pos+len('x-goog-authuser: '):].find(' ')
				#_LOGGER.debug(xauth_len)
				if(xauth_len>=0):
					#_LOGGER.debug("found space in text")
					clean_x_goog_authuser = c[xauth_pos:(xauth_pos+len('x-goog-authuser: ')+xauth_len)]
					#_LOGGER.debug(clean_x_goog_authuser)
			## lets see what we got
			if(clean_cookie!="" and clean_x_goog_authuser!=""):
				# woop woop, this COULD be it
				c = clean_cookie+"\n"+clean_x_goog_authuser+"\n"
			else:
				# well we've failed to find the cookie, the only thing we can do is at least to help with some breaks
				c = c.replace('cookie','\ncookie')
				c = c.replace('Cookie','\nCookie')
				c = c.replace('x-goog-authuser','\nx-goog-authuser')
				c = c.replace('X-Goog-AuthUser','\nX-Goog-AuthUser')
			#_LOGGER.debug("feeding with: ")
			#_LOGGER.debug(c)
			YTMusic.setup(filepath = path, headers_raw = c)
			return {}
		except Exception:
			c = user_input[CONF_COOKIE].lower()
			if(c.find('cookie') == -1 ):
				_LOGGER.error("Field 'Cookie' not found!")
				ret["base"] = ERROR_COOKIE
			elif(c.find('X-Goog-AuthUser') == -1 ):
				_LOGGER.error("Field 'X-Goog-AuthUser' not found!")
				ret["base"] = ERROR_AUTH_USER
			else:
				_LOGGER.error("Generic setup error, please see below")
				_LOGGER.error(traceback.format_exc())
				ret["base"] = ERROR_GENERIC
			return ret

def ensure_config(user_input,path):
	"""Make sure that needed Parameter exist and are filled with default if not."""
	out = {}
	out[CONF_HEADER_PATH] = path
#	out[CONF_ICON] = DEFAULT_ICON
	out[CONF_RECEIVERS] = ''
	out[CONF_SHUFFLE] = DEFAULT_SHUFFLE
	out[CONF_SHUFFLE_MODE] = DEFAULT_SHUFFLE_MODE
	out[CONF_SELECT_SOURCE] = DEFAULT_SELECT_SOURCE
	out[CONF_SELECT_PLAYLIST] = DEFAULT_SELECT_PLAYLIST
	out[CONF_SELECT_PLAYMODE] = DEFAULT_SELECT_PLAYMODE
	out[CONF_SELECT_SPEAKERS] = DEFAULT_SELECT_SPEAKERS

	if user_input is not None:
		if CONF_HEADER_PATH in user_input:
			out[CONF_HEADER_PATH] = user_input[CONF_HEADER_PATH]
		if CONF_RECEIVERS in user_input:
			out[CONF_RECEIVERS] = user_input[CONF_RECEIVERS]
		if CONF_SHUFFLE in user_input:
			out[CONF_SHUFFLE] = user_input[CONF_SHUFFLE]
		if CONF_SHUFFLE_MODE in user_input:
			out[CONF_SHUFFLE_MODE] = user_input[CONF_SHUFFLE_MODE]
		if CONF_SELECT_SOURCE in user_input:
			out[CONF_SELECT_SOURCE] = user_input[CONF_SELECT_SOURCE]
		if CONF_SELECT_PLAYLIST in user_input:
			out[CONF_SELECT_PLAYLIST] = user_input[CONF_SELECT_PLAYLIST]
		if CONF_SELECT_PLAYMODE in user_input:
			out[CONF_SELECT_PLAYMODE] = user_input[CONF_SELECT_PLAYMODE]
		if CONF_SELECT_SPEAKERS in user_input:
			out[CONF_SELECT_SPEAKERS] = user_input[CONF_SELECT_SPEAKERS]
	return out


def create_form(user_input, path):
	"""Create form for UI setup."""
	user_input = ensure_config(user_input,path)

	data_schema = OrderedDict()
	data_schema[vol.Required(CONF_COOKIE, default="")] = str
#	data_schema[vol.Required(CONF_HEADER_PATH, default=user_input[CONF_HEADER_PATH])] = str
#	data_schema[vol.Required(CONF_RECEIVERS, default=user_input[CONF_RECEIVERS])] = str
#	data_schema[vol.Optional(CONF_SHUFFLE, default=user_input[CONF_SHUFFLE])] = vol.Coerce(bool)
#	data_schema[vol.Optional(CONF_SHUFFLE_MODE, default=user_input[CONF_SHUFFLE_MODE])] = vol.Coerce(int)
#	data_schema[vol.Optional(CONF_SELECT_SOURCE, default=user_input[CONF_SELECT_SOURCE])] = str
#	data_schema[vol.Optional(CONF_SELECT_PLAYLIST, default=user_input[CONF_SELECT_PLAYLIST])] = str
#	data_schema[vol.Optional(CONF_SELECT_SPEAKERS, default=user_input[CONF_SELECT_SPEAKERS])] = str

	return data_schema
