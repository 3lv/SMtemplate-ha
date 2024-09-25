"""Sequent Microsystems Home Automation Integration"""

import logging
import voluptuous as vol

from homeassistant.helpers import config_validation as cv
from homeassistant.const import (
	CONF_NAME
)
from homeassistant.helpers.discovery import load_platform

from . import data
DOMAIN = data.DOMAIN
NAME_PREFIX = data.NAME_PREFIX
SM_MAP = data.SM_MAP
SM_API = data.API

CONF_NAME = CONF_NAME
CONF_STACK = "stack"
CONF_TYPE = "type"
CONF_CHAN = "chan"
CONF_CHAN_RANGE = "chan_range"
CONF_UPDATE_INTERVAL = "update_interval" # In seconds
COM_NOGET = "__NOGET__"



CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema(vol.Any([vol.Schema({
        vol.Optional(CONF_STACK, default="0"): cv.string,
    }, extra=vol.ALLOW_EXTRA)], {}))
}, extra=vol.ALLOW_EXTRA)

_LOGGER = logging.getLogger(__name__)

async def SM_load_platform(hass, entity_config):
        for platform_type, attr in SM_MAP.items():
            if entity_config[CONF_TYPE] in attr:
                load_platform(
                        hass, platform_type, DOMAIN, entity_config, {}
                )

async def SM_load_all_platforms(hass, stack=0):
    for platform_type, platform in SM_MAP.items():
        for type, attr in platform.items():
            if attr.get("optional", False):
                continue
            for chan in range(int(attr["chan_no"])):
                entity_config = {
                        CONF_NAME: NAME_PREFIX+str(stack)+"_"+type+"_"+str(chan+1),
                        CONF_STACK: stack,
                        CONF_TYPE: type,
                        CONF_CHAN: chan+1
                }
                load_platform(
                        hass, platform_type, DOMAIN, entity_config, {}
                )


async def async_setup(hass, config):
    hass.data[DOMAIN] = []
    card_configs = config.get(DOMAIN)
    if not card_configs:
        await SM_load_all_platforms(hass, stack=0)
        return True
    for card_config in card_configs:
        stack = int(card_config.pop(CONF_STACK, 0))
        if not card_config:
            await SM_load_all_platforms(hass, stack=stack)
            continue
        for entity in card_config:
            card_config[entity] = card_config[entity] or {}
            chan_range = card_config[entity].get(CONF_CHAN_RANGE)
            update_interval = card_config[entity].get(CONF_UPDATE_INTERVAL)
            try:
                [chan_start, chan_end] = chan_range.split("..", 1)
                chan_start = int(chan_start)
                chan_end = int(chan_end)
                type = entity
                for chan in range(chan_start, chan_end + 1, 1):
                    entity_config = card_config[entity].copy()
                    entity_config |= {
                        CONF_NAME: NAME_PREFIX + str(stack) + "_" + entity + "_" + str(chan),
                        CONF_STACK: stack,
                        CONF_TYPE: type,
                        CONF_CHAN: chan,
                        CONF_UPDATE_INTERVAL: update_interval,
                    }
                    await SM_load_platform(hass, entity_config)
            except:
                try:
                    [type, chan] = entity.rsplit("_", 1)
                    chan = int(chan)
                except:
                    _LOGGER.error("%s doesn't respect type_channel format", entity)
                    continue
                entity_config = card_config[entity].copy()
                entity_config |= {
                        CONF_NAME: NAME_PREFIX + str(stack) + "_" + entity,
                        CONF_STACK: stack,
                        CONF_TYPE: type,
                        CONF_CHAN: chan,
                        CONF_UPDATE_INTERVAL: update_interval,
                }
                await SM_load_platform(hass, entity_config)
    return True
