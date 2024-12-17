DEFAULT_ICONS = {
        "on": "mdi:format-list-buletted",
        "off": "mdi:format-list-buletted",
}

import logging
import time
import types
import inspect
from inspect import signature
_LOGGER = logging.getLogger(__name__)

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity import generate_entity_id

from . import (
        DOMAIN, CONF_STACK, CONF_TYPE, CONF_CHAN, CONF_NAME,
        CONF_UPDATE_INTERVAL,
        COM_NOGET,
        SM_MAP, SM_API
)
SM_MAP = SM_MAP["select"]

async def async_setup_platform(hass, config, add_devices, discovery_info=None):
    # We want this platform to be setup via discovery
    if discovery_info == None:
        return
    type=discovery_info.get(CONF_TYPE)
    add_devices([Select(
        hass=hass,
        name=discovery_info.get(CONF_NAME),
        stack=discovery_info.get(CONF_STACK, 0),
        type=discovery_info.get(CONF_TYPE),
        chan=discovery_info.get(CONF_CHAN),
    )])

class Select(SelectEntity):
    def __init__(self, hass, name, stack, type, chan):
        generated_name = DOMAIN + str(stack) + "_" + type + "_" + str(chan)
        self._unique_id = generate_entity_id("select.{}", generated_name, hass=hass)
        self._name = name or generated_name
        self._stack = int(stack)
        self._type = type
        self._chan = int(chan)
        self._short_timeout = .05
        self._icons = DEFAULT_ICONS | SM_MAP[self._type].get("icon", {})
        self._icon = self._icons["off"]
        self._uom = SM_MAP[self._type].get("uom", "")
        self._option_map = SM_MAP[self._type]["option_map"]
        self._r_option_map = {value: key for key, value in self._option_map.items()}
        self._options = list(self._option_map.keys())
        self._current_option = next(iter(self._options))
        self.__SM__init()
        ### __CUSTOM_SETUP__ START
        ### __CUSTOM_SETUP__ END

    def __SM__init(self):
        com = SM_MAP[self._type]["com"]
        self._SM = SM_API
        if inspect.isclass(self._SM):
            self._SM = self._SM(self._stack)
            self._SM_get = getattr(self._SM, com["get"])
            self._SM_set = getattr(self._SM, com["set"])
            if len(signature(self._SM_get).parameters) == 0:
                def _aux2_SM_get(self, _):
                    return getattr(self, com["get"])()
                self._SM_get = types.MethodType(_aux2_SM_get, self._SM)
            if len(signature(self._SM_set).parameters) == 1:
                def _aux2_SM_set(self, _, value):
                    getattr(self, com["set"])(value)
                self._SM_set = types.MethodType(_aux2_SM_set, self._SM)
        else:
            _SM_get = getattr(self._SM, com["get"])
            if len(signature(_SM_get).parameters) == 1:
                def _aux3_SM_get(_):
                    return _SM_get(self._stack)
                self._SM_get = _aux3_SM_get
            else:
                def _aux_SM_get(chan):
                    return _SM_get(self._stack, chan)
                self._SM_get = _aux_SM_get
            _SM_set = getattr(self._SM, com["set"])
            if len(signature(_SM_set).parameters) == 2:
                def _aux3_SM_set(_, value):
                    return _SM_set(self._stack, value)
                self._SM_set = _aux3_SM_set
            else:
                def _aux_SM_set(chan, value):
                    return _SM_set(self._stack, chan, value)
                self._SM_set = _aux_SM_set

    def update(self):
        time.sleep(self._short_timeout)
        try:
            value = self._SM_get(self._chan)
            self._current_option = self._r_option_map[value]
        except Exception as ex:
            _LOGGER.error(DOMAIN + " %s update() failed, %e, %s, %s", self._type, ex, str(self._stack), str(self._chan))
            return

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
    def options(self):
        return self._options

    @property
    def current_option(self):
        return self._current_option

    def select_option(self, option):
        try:
            value = self._option_map[option]
            self._SM_set(self._chan, value)
        except Exception as ex:
            _LOGGER.error(DOMAIN + " %s setting value failed, %e", self._type, ex)
