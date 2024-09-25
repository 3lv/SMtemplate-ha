DEFAULT_ICONS = {
        "off": "mdi:button-pointer",
}

import types
import inspect
from inspect import signature
import logging
import time

from homeassistant.const import (
	CONF_NAME
)

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import generate_entity_id

from . import (
        DOMAIN, CONF_STACK, CONF_TYPE, CONF_CHAN, CONF_NAME,
        SM_API, SM_MAP
)
SM_MAP = SM_MAP["button"]

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, add_devices, discovery_info=None):
    # We want this platform to be setup via discovery
    if discovery_info == None:
        return
    # TODO CHECK IF ALREADY CONFIGURED FOR WHATEVER REASON
    add_devices([Button(
		name=discovery_info.get(CONF_NAME, ""),
        stack=discovery_info.get(CONF_STACK, 0),
        type=discovery_info.get(CONF_TYPE),
        chan=discovery_info.get(CONF_CHAN),
        hass=hass,
	)])

class Button(ButtonEntity):
    def __init__(self, name, stack, type, chan, hass):
        generated_name = DOMAIN + str(stack) + "_" + type + "_" + str(chan)
        self._unique_id = generate_entity_id("button.{}", generated_name, hass=hass)
        self._name = name or generated_name
        self._stack = int(stack)
        self._type = type
        self._chan = int(chan)
        self._short_timeout = .05
        self._icons = DEFAULT_ICONS | SM_MAP[self._type].get("icon", {})
        self._icon = self._icons["off"]
        self.__SM__init()
        ### __CUSTOM_SETUP__ START
        ### __CUSTOM_SETUP__ END
    
    def __SM__init(self):
        com = SM_MAP[self._type]["com"]
        self._SM = SM_API
        if inspect.isclass(self._SM):
            self._SM = self._SM(self._stack)
            self._SM_set = getattr(self._SM, com["set"])
            ### Make API compatible if channel is not used (_)
            if len(signature(self._SM_set).parameters) == 1:
                def _aux2_SM_set(self, _, value):
                    getattr(self, com["set"])(value)
                self._SM_set = types.MethodType(_aux2_SM_set, self._SM)
        else:
            _SM_set = getattr(self._SM, com["set"])
            if len(signature(_SM_set).parameters) == 2:
                def _aux3_SM_set(_, *args):
                    return _SM_set(self._stack, *args)
                self._SM_set = _aux3_SM_set
            else:
                def _aux_SM_set(*args):
                    return _SM_set(self._stack, *args)
                self._SM_set = _aux_SM_set

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    def press(self, **kwargs):
        try:
            self._SM_set(self._chan)
        except Exception as ex:
            _LOGGER.error(DOMAIN + " %s turn ON failed, %e", self._type, ex)
