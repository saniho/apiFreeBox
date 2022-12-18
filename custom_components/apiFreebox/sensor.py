"""Sensor for my first"""
import logging
from collections import defaultdict
from datetime import timedelta
import datetime

import urllib.parse as urlparse
from urllib.parse import parse_qs

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    ATTR_ATTRIBUTION,
)

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.util import slugify
from homeassistant.util.dt import now, parse_date

_LOGGER = logging.getLogger(__name__)

DOMAIN = "saniho"

ICON = "mdi:package-variant-closed"

SCAN_INTERVAL = timedelta(seconds=1800)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT): cv.positive_int,
        vol.Optional(CONF_NAME): cv.string,
    }
)


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

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the platform."""
    name = config.get(CONF_NAME)
    update_interval = config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)

    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT, 80)

    try:
        session = []
    except :
        _LOGGER.exception("Could not run my First Extension")
        return False
    fbx = freepybox.freepybox( token_file = manageDirectory() )
    _LOGGER.info("host %s" %(host))
    fbx.open(host, port)
    fbxlstPlayer = fbx.freeplayer.get_freeplayer_list()
    fbx.close()
    add_entities([myFreeBox(session, name, update_interval, host, port)], True)
    for monPlayer in fbxlstPlayer or []:
        add_entities([myFreeBoxPlayer(session, name, update_interval, host, port, monPlayer["id"] )], True)
    # on va gerer  un element par heure ... maintenant

class myFreeBox(Entity):
    """."""

    def __init__(self, session, name, interval, host, port):
        """Initialize the sensor."""
        self._session = session
        self._name = name
        self._host = host
        self._port = port
        self._attributes = None
        self._state = None
        self.update = Throttle(interval)(self._update)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "myFreeBox"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return ""

    def _update(self):
        """Update device state."""
        status_counts = defaultdict(int)
        fbx = freepybox.freepybox( token_file = manageDirectory() )
        fbx.open(self._host, self._port)
        fbx_connection_status_details = fbx.connection.get_status_details()
        fbx_connection_xdsl_details = fbx.connection.get_xdsl_stats()
        fbx.close()
        status_counts["version"] = __VERSION__
        status_counts["lastSynchro"] = datetime.datetime.now()
        status_counts['ipv4'] = fbx_connection_status_details.get('ipv4',"")
        status_counts['ipv6'] = fbx_connection_status_details.get('ipv6',"")
        # unite : Mb
        status_counts['bandwidth_down'] = (fbx_connection_status_details.get('bandwidth_down',0)/1000000)
        # unite : Mb
        status_counts['bandwidth_up'] = (fbx_connection_status_details.get('bandwidth_up',0)/1000000)
        
        status_counts['down_attn'] = (fbx_connection_xdsl_details['down']['attn_10']/10)
        status_counts['up_attn'] = (fbx_connection_xdsl_details['up']['attn_10']/10)
        status_counts['modulation'] = fbx_connection_xdsl_details['status']['modulation']
        status_counts['protocol'] = fbx_connection_xdsl_details['status']['protocol']
        status_counts['uptime'] = fbx_connection_xdsl_details['status']['uptime']
        
        status_counts['state'] = fbx_connection_status_details.get('state',"")

        self._attributes = {ATTR_ATTRIBUTION: ""}
        self._attributes.update(status_counts)
        ## pour debloquer
        self._state = fbx_connection_status_details['state']

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Icon to use in the frontend."""

class myFreeBoxPlayer(Entity):
    """."""

    def __init__(self, session, name, interval, host, port, id):
        """Initialize the sensor."""
        self._session = session
        self._name = name
        self._host = host
        self._port = port
        self._id = id
        self._attributes = None
        self._state = None
        self.update = Throttle(interval)(self._update)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "myFreeBoxPlayer.%s" %(self._id )

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return ""

    def _update(self):
        """Update device state."""
        status_counts = defaultdict(int)

        fbx = freepybox.freepybox( token_file = manageDirectory() )
        #_LOGGER.exception("host  update %s" %(self._host))
        status_counts["version"] = __VERSION__
        status_counts["lastSynchro"] = datetime.datetime.now()
        try:
            fbx.open(self._host, self._port)
            myfbx_player_status_details = fbx.freeplayer.get_freeplayer(self._id)
            fbx.close()
            status_counts["power_stat"] = myfbx_player_status_details["power_state"]
            quelPackage = myfbx_player_status_details["foreground_app"]["package"]
            status_counts["package"] = quelPackage
            status_counts["package_id"] = myfbx_player_status_details["foreground_app"]["package_id"]
            status_counts["channel"] = ""
            if ( quelPackage == "fr.freebox.tv"):
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
                    status_counts["out"] = "tv" # on force
            elif (quelPackage == "fr.freebox.mediaplayer"):
                status_counts["out"] = "mediaplayer"
                status_counts["channel"] = "mediaplayer"
                status_counts["channelName"] = "mediaplayer"
            elif (quelPackage == "fr.freebox.vodlauncher"):
                status_counts["out"] = "vodlaucher"
                status_counts["channel"] = "vodlaucher"
                status_counts["channelName"] = "vodlaucher"
            elif (quelPackage == "com.disneyplus"):
                status_counts["out"] = "Disney +"
                status_counts["channel"] = "Disney +"
                status_counts["channelName"] = "Disney +"
            elif (quelPackage == "com.netflix"):
                status_counts["out"] = "Netflix"
                status_counts["channel"] = "Netflix"
                status_counts["channelName"] = "Netflix"
            elif (quelPackage == "com.youtube.tv"):
                status_counts["out"] = "youtube"
                status_counts["channel"] = "youtube"
                status_counts["channelName"] = "youtube"
            elif (quelPackage == "com.primevideo"):
                status_counts["out"] = "Prime"
                status_counts["channel"] = "Prime"
                status_counts["channelName"] = "Prime"
            elif (quelPackage == "fr.freebox.home"):
                status_counts["out"] = "home"
                status_counts["channel"] = "home"
                status_counts["channelName"] = "home"
            else:
                status_counts["out"] = "%s ???"%(quelPackage)
        except:
            myfbx_player_status_details = {"power_state": "eteinte"}
            pass

        status_counts["info"] = "%s"%(myfbx_player_status_details)

        self._attributes = {ATTR_ATTRIBUTION: ""}
        self._attributes.update(status_counts)
        ## pour debloquer
        self._state = myfbx_player_status_details["power_state"]

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Icon to use in the frontend."""



