"""Modbus Mapping Data."""

# Registers are:
#    A_1 to A_500 - Analog Registers e.g. outside temperature
#    D_1 to D_496 - Digital Registers e.g. pump on/ off
#    I_1 to I_500 - Integer Registers e.g. pump runtime

# Mapping based on controller and possibly ext from info.
#   Also the value I_405 has Serial Port Used 0, 1, 2, 3, 4, not sure if useful.
CONROLLER_MAP = {
    "pco5_0": "mt_0",
    "uPC_0": "mt_1",
}

# Currently known mappings:
# default is standard firmware for the CAREL
# mt_1 looks like custom firmware for certain devices
MAPPING = {
    "mt_0": {
        "A": {"type": "hold", "start": 0},
        "D": {"type": "coil", "start": 0},
        "I": {"type": "hold", "start": 5001},
    },
    "mt_1": {
        "A": {"type": "hold", "start": 2},
        "D": {"type": "coil", "start": 2},
        "I": {"type": "hold", "start": 5003},
    },
}
