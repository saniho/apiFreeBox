import logging
from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_UNAVAILABLE

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)

import urllib.parse as urlparse
from urllib.parse import parse_qs
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util.enum import try_parse_enum
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.util import slugify
from homeassistant.util.dt import now, parse_date
from datetime import timedelta
import datetime
from collections import defaultdict


from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    ATTR_ATTRIBUTION,
)

_LOGGER = logging.getLogger(__name__)

DOMAIN = "saniho"

ICON = "mdi:eye"
SCAN_INTERVAL = timedelta(seconds=1800)

try:
    from .const import (
        __VERSION__
    )
    from . import freepybox

except ImportError:
    from const import (
        __VERSION__
    )
    import freepybox

def manageDirectory():
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = dir_path.replace("apiFreebox", "archive")
    try:
        path = "%s" % (dir_path)
        if not os.path.isdir(path):
            os.mkdir(path)
    except:
        pass
    try:
        path = "%s/apiFreebox" % (dir_path)
        if not os.path.isdir(path):
            os.mkdir(path)
    except:
        pass
    token_file = f"{path}/app_auth"
    return token_file

def setup_platform(hass, config, add_entities, discovery_info=None) -> None:
    """Set up the platform."""
    name = config.get(CONF_NAME)
    update_interval = config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)

    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT, 80)

    try:
        session = []
    except :
        -_LOGGER.exception("Could not run my First Extension")
        return False
    fbx = freepybox.freepybox(token_file = manageDirectory())
    _LOGGER.info("host %s" %(host))
    fbx.open(host, port)
    fbxlstPlayer = fbx.freeplayer.get_freeplayer_list()
    fbx.close()
    for monPlayer in fbxlstPlayer or []:
        add_entities([myFreeBoxPlayerState(session, name, update_interval, host, port, monPlayer)], True)

class myFreeBoxPlayerState(Entity):
    """."""

    def __init__(self, session, name, interval, host, port, monPlayer):
        """Initialize the sensor."""
        self._session = session
        self._attr_name = name
        self._host = host
        self._port = port
        self._id = monPlayer["id"]
        self._attributes = None
        self._attr_state = STATE_UNAVAILABLE
        self._monPlayer = monPlayer
        self.update = Throttle(interval)(self._update)

    @property
    def unique_id(self):
        "Return a unique_id for this entity."
        return "myFreeBoxPlayer.%s" %(self._id )

    @property
    def name(self):
        """Return the name of the sensor."""
        return "myFreeBoxPlayer.%s" %(self._id )

    def is_on(self): 
        return self._attr_state

    def _update(self):
        """Update device state."""
        status_counts = defaultdict(int)

        fbx = freepybox.freepybox(token_file = manageDirectory())
        #_LOGGER.exception("host  update %s" %(self._host))
        status_counts["version"] = __VERSION__
        status_counts["lastSynchro"] = datetime.datetime.now()

        try:
            fbx.open(self._host, self._port)
            myfbx_player_status_details = fbx.freeplayer.get_freeplayer(self._id)
            myfbx_player_control_volume = fbx.freeplayer.get_freeplayer_volume(self._id)
            myfbx_player_ip = fbx.freeplayer.get_freeplayer_ip(self._monPlayer)
            fbx.close()
            power = myfbx_player_status_details["power_state"]
            status_counts["ip"] = myfbx_player_ip
            if("running" == power):
                status_counts["power_stat"] = myfbx_player_status_details["power_state"]
                quelPackage = myfbx_player_status_details["foreground_app"]["package"]
                #status_counts["info"] = "%s"%(myfbx_player_status_details)
                status_counts["package"] = quelPackage
                if (quelPackage == "fr.freebox.tv"):
                    quoiRegarde = myfbx_player_status_details["foreground_app"]["cur_url"]
                    parsed = urlparse.urlparse(quoiRegarde)
                    status_counts["out"] = parsed.scheme
                    if ( status_counts["out"] == "tv" ):
                        status_counts["channel"] = parse_qs(parsed.query)['channel'][0]
                    if ( status_counts["out"] == "home" ):
                        status_counts["highlight"] = parse_qs(parsed.query)['highlight'][0]
                        newUrl = parse_qs(parsed.query)['highlight'][0]
                        parsed = urlparse.urlparse(newUrl)
                        try:
                            status_counts["bouquetName"] = parse_qs(parsed.query)["bouquetName"][0]
                        except:
                            pass
                    if ( status_counts["out"] == "" ):
                        channel = myfbx_player_status_details["foreground_app"]["context"]["channel"]
                        status_counts["channel"] = channel["channelNumber"]
                        status_counts["channelName"] = channel["channelName"]
                        status_counts["out"] = "tv"
                elif( quelPackage == "fr.freebox.radio"):
                    channel = myfbx_player_status_details["foreground_app"]["context"]["radio"]["currentRadio"]
                    status_counts["channel"] = channel["name"]
                    status_counts["channelName"] = channel["name"]
                    status_counts["out"] = "Radio"
                else: 
                    if (quelPackage == "fr.freebox.mediaplayer"):
                        chaine = "mediaplayer"
                    elif (quelPackage == "fr.freebox.vodlauncher"):
                        chaine = "vodlaucher"
                    elif (quelPackage == "com.disneyplus"):
                        chaine = "Disney +"
                    elif (quelPackage == "com.netflix"):
                        chaine = "Netflix"
                    elif (quelPackage == "com.youtube.tv"):
                        chaine = "Youtube"
                    elif (quelPackage == "com.primevideo"):
                        chaine = "Prime"
                    elif (quelPackage == "fr.freebox.home"):
                        chaine = "Home"
                    elif (quelPackage == "fr.freebox.overlayhome"):
                        chaine = "Home"
                    elif (quelPackage == "fr.freebox.replay"):
                        chaine = "Replay"
                    elif (quelPackage == "fr.freebox.filebrowser"):
                        chaine = "Mes Fichiers"
                    elif (quelPackage == "fr.freebox.ligue1"):
                        chaine = "Free Ligue 1"
                    elif (quelPackage == "fr.freebox.domotique"):
                        chaine = "Camera"
                    elif (quelPackage == "fr.freebox.downloader"):
                        chaine = "Téléchargements"
                    elif (quelPackage == "com.apple.tv"):
                        chaine = "Apple TV"
                    elif (quelPackage == "fr.freebox.nucleus"):
                        chaine = "Oqee Ciné"
                    elif (quelPackage == "fr.max.play"):
                        chaine = "Max"
                    else:
                        chaine = "%s ???"%(quelPackage)
                    status_counts["out"] = chaine
                    status_counts["channel"] = chaine
                    status_counts["channelName"] = chaine

                #Traitement du volume
                volume = 0
                mute = False
                mute = myfbx_player_control_volume['mute']
                if(False == mute):
                    volume = myfbx_player_control_volume['volume']
                status_counts["volume"] = volume
                status_counts["mute"] = mute
                self._attr_state = STATE_ON
                self._attributes = {ATTR_ATTRIBUTION: ""}
                self._attributes.update(status_counts)
                self._attr_available = True
            else:
                status_counts["out"] = ""
                status_counts["channel"] = ""
                status_counts["channelName"] = ""
                status_counts["volume"] = 0
                status_counts["mute"] = False
                self._attr_state = STATE_OFF
                self._attributes = {ATTR_ATTRIBUTION: ""}
                self._attributes.update(status_counts)
                self._attr_available = True
        except:
            status_counts["out"] = ""
            status_counts["channel"] = ""
            status_counts["channelName"] = ""
            status_counts["volume"] = 0
            status_counts["mute"] = False
            self._attributes = {ATTR_ATTRIBUTION: ""}
            self._attributes.update(status_counts)
            self._attr_state = STATE_UNAVAILABLE
            self._attr_available = False

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return ICON