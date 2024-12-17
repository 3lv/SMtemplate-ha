FULL_NAME = "Home Automation"
LINK = "https://sequentmicrosystems.com/products/raspberry-pi-home-automation-card"

import libioplus
API = libioplus
DOMAIN = "SMioplus"
NAME_PREFIX = "smio"
SM_MAP = {
    "button": {
        "opto_cnt_rst": {
            "chan_no": 8,
            "com": {
                "set": "rstOptoCount",
            },
        }
    },
    "binary_sensor": {
        "opto": {
                "chan_no": 8,
                "com": {
                    "get": "getOptoCh",
                },
        },
    },
    "select": {
        "type": {
            "chan_no": 8,
            "com": {
                "get": "get_sensor_type",
                "set": "set_sensor_type",
            },
            "option_map": {
                "B": 0,
                "E": 1,
                "J": 2,
                "K": 3,
                "N": 4,
                "R": 5,
                "S": 6,
                "T": 7,
            }
        },
    },
    "sensor": {
        "opto_cnt": {
                "chan_no": 8,
                "com": {
                    "get": "getOptoCount",
                },
        },
        "adc": {
                "chan_no": 8,
                "uom": "V",
                "com": {
                    "get": "getAdcV",
                },
                "icon": {
                    "on": "mdi:flash-triangle",
                    "off": "mdi:flash-triangle"
                }
        },
    },
    "switch": {
        "relay": {
                "chan_no": 8,
                "com": {
                    "get": "getRelayCh",
                    "set": "setRelayCh"
                },
        }
    },
    "number": {
        "dac": {
                "chan_no": 4,
                "uom": "V",
                "min_value": 0.0,
                "max_value": 10.0,
                "step": 0.01,
                "com": {
                    #"get": "__NOGET__",
                    "get": "getDacV",
                    "set": "setDacV"
                },
                "icon": {
                    "on": "mdi:flash-triangle",
                    "off": "mdi:flash-triangle"
                }
        },
        "od": {
                "chan_no": 4,
                "uom": "%",
                "min_value": 0.0,
                "max_value": 100.0,
                "step": 0.01,
                "com": {
                    "get": "_fixed_getOdPwm",
                    "set": "_fixed_setOdPwm"
                },
                "icon": {
                    "on": "mdi:percent",
                    "off": "mdi:percent"
                }
        },
    },
}
