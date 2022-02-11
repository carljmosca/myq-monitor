"""

device info

"""

import os
import json

from logutil import _LOGGER

MYQ_DATADIR = os.environ['MYQ_DATADIR']

def get_lastknown_device_status(device):

    result = None
    try:
        with open(MYQ_DATADIR + '/' + device.device_id + '.json') as json_file:
            result = json.load(json_file)
    except FileNotFoundError as err:
        _LOGGER.error(err)
    return result


def set_lastknown_device_status(device):

    result = None
    data = {
        'name': device.name,
        'device_state': device.device_state,
        'device_id': device.device_id
    }

    json_string = json.dumps(data)
    with open(MYQ_DATADIR + '/' + device.device_id + '.json', 'w') as outfile:
        outfile.write(json_string)
    return result
