import asyncio
import logging
import os
import json
import vonage

from aiohttp import ClientSession

from pymyq import login
from pymyq.account import MyQAccount
from pymyq.errors import MyQError, RequestError
from pymyq.garagedoor import STATE_CLOSED

_LOGGER = logging.getLogger()
MYQ_EMAIL = os.environ['MYQ_EMAIL']
MYQ_PASSWORD = os.environ['MYQ_PASSWORD']
MYQ_DATADIR = os.environ['MYQ_DATADIR']
MYQ_SMS_RECIPIENTS = os.environ['MYQ_SMS_RECIPIENTS']
MYQ_SEND_ANY_STATUS = os.getenv("MYQ_SEND_ANY_STATUS", 'False').lower() in ('true', '1', 't')
VONAGE_CLIENT_KEY = os.environ['VONAGE_CLIENT_KEY']
VONAGE_CLIENT_SECRET = os.environ['VONAGE_CLIENT_SECRET']
VONAGE_CLIENT_SMS_NUMBER = os.environ['VONAGE_CLIENT_SMS_NUMBER']

vonageClient = vonage.Client(
    key=VONAGE_CLIENT_KEY, secret=VONAGE_CLIENT_SECRET)
vonageSms = vonage.Sms(vonageClient)

LOGLEVEL = logging.INFO


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


def send_notification(device):

    recipients = MYQ_SMS_RECIPIENTS.split(",")
    for x in range(len(recipients)):

        print(f"Sending message to {recipients[x]}")
        responseData = vonageSms.send_message(
            {
                "from": VONAGE_CLIENT_SMS_NUMBER,
                "to": recipients[x],
                "text": device.name + " is " + device.device_state,
            }
        )

        if responseData["messages"][0]["status"] == "0":
            print("Message sent successfully.")
        else:
            print(
                f"Message failed with error: {responseData['messages'][0]['error-text']}")


async def process_garagedoors(account: MyQAccount):
    """Process garage doors

    Args:
        account (MyQAccount): Account for which to retrieve garage doors
    """
    print(f"  GarageDoors: {len(account.covers)}")
    print("  ---------------")
    if len(account.covers) != 0:
        for idx, device in enumerate(account.covers.values()):
            print(f" processing device {idx}")
            sendNotification = MYQ_SEND_ANY_STATUS
            try:
                lastknown_device_status = get_lastknown_device_status(
                    device)
                if device.state == STATE_CLOSED:
                    print(f"Garage door {device.name} is closed")
                    if (lastknown_device_status == None or device.state != lastknown_device_status['device_state']):
                        set_lastknown_device_status(device)
                else:
                    print(
                        f"Garage door {device.name} is {device.device_state}")
                    if (not hasattr(lastknown_device_status, "state") or device.state != lastknown_device_status.state):
                        set_lastknown_device_status(device)
                    else:
                        print(f"report status {device.device_state}")
                        sendNotification = True
                if sendNotification:
                    send_notification(device)
            except RequestError as err:
                _LOGGER.error(err)
        print("  ------------------------------")


async def main() -> None:
    logging.basicConfig(level=LOGLEVEL)
    async with ClientSession() as websession:
        try:
            # Create an API object:
            api = await login(MYQ_EMAIL, MYQ_PASSWORD, websession)

            for account in api.accounts.values():
                print(f"Account ID: {account.id}")
                print(f"Account Name: {account.name}")

                # Get all devices listed with this account – note that you can use
                # api.covers to only examine covers or api.lamps for only lamps.
                await process_garagedoors(account=account)

        except MyQError as err:
            _LOGGER.error("There was an error: %s", err)

asyncio.get_event_loop().run_until_complete(main())
