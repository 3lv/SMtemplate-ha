DEFAULT_ICONS = {
        "on": "mdi:numeric",
        "off": "mdi:numeric-0",
}

import logging
import time
import types
import inspect
from inspect import signature

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta

from . import (
        DOMAIN, CONF_STACK, CONF_TYPE, CONF_CHAN, CONF_NAME,
        CONF_UPDATE_INTERVAL,
        SM_MAP, SM_API
)
SM_MAP = SM_MAP["sensor"]

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, add_devices, discovery_info=None):
    # We want this platform to be setup via discovery
    if discovery_info == None:
        return
    add_devices([Sensor(
        hass=hass,
		name=discovery_info.get(CONF_NAME),
        stack=discovery_info.get(CONF_STACK),
        type=discovery_info.get(CONF_TYPE),
        chan=discovery_info.get(CONF_CHAN),
        update_interval=discovery_info.get(CONF_UPDATE_INTERVAL) or 30,
	)])

class Sensor(SensorEntity):
    def __init__(self, hass, name, stack, type, chan, update_interval):
        generated_name = DOMAIN + str(stack) + "_" + type + "_" + str(chan)
        self._unique_id = generate_entity_id("sensor.{}", generated_name, hass=hass)
        self._name = name or generated_name
        self._stack = int(stack)
        self._type = type
        self._chan = int(chan)
        self._update_interval = float(update_interval)
        self._short_timeout = .05
        self._icons = DEFAULT_ICONS | SM_MAP[self._type].get("icon", {})
        self._icon = self._icons["off"]
        self._uom = SM_MAP[self._type].get("uom", "")
        self._value = 0
        self._remove_hooks = []
        self.__SM__init()
        ### CUSTOM_SETUP START
        ### CUSTOM_SETUP END

    def __SM__init(self):
        com = SM_MAP[self._type]["com"]
        self._SM = SM_API
        if inspect.isclass(self._SM):
            self._SM = self._SM(self._stack)
            self._SM_get = getattr(self._SM, com["get"])
            ### Make API compatible if channel is not used (_)
            if len(signature(self._SM_get).parameters) == 0:
                def _aux2_SM_get(self, _):
                    return getattr(self, com["get"])()
                self._SM_get = types.MethodType(_aux2_SM_get, self._SM)
        else:
            _SM_get = getattr(self._SM, com["get"])
            if len(signature(_SM_get).parameters) == 1:
                def _aux3_SM_get(_, *args):
                    return _SM_get(self._stack, *args)
                self._SM_get = _aux3_SM_get
            else:
                def _aux_SM_get(*args):
                    return _SM_get(self._stack, *args)
                self._SM_get = _aux_SM_get

    async def async_added_to_hass(self):
        new_hook = async_track_time_interval(
            self.hass, self.async_update_ha_state, timedelta(seconds=self._update_interval)
        )
        self._remove_hooks.append(new_hook)

    async def async_will_remove_from_hass(self):
        for remove_hook in self._remove_hooks:
            remove_hook()

    @property
    def should_poll(self):
        return False

    def update(self):
        time.sleep(self._short_timeout)
        try:
            self._value = self._SM_get(self._chan)
        except Exception as ex:
            _LOGGER.error(DOMAIN + " %s update() failed, %e, %s, %s", self._type, ex, str(self._stack), str(self._chan))
            return
        if self._value != 0:
            self._icon = self._icons["on"]
        else:
            self._icon = self._icons["off"]

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def native_unit_of_measurement(self):
        return self._uom

    @property
    def native_value(self):
        return self._value
