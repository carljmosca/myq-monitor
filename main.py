import asyncio
import os

from aiohttp import ClientSession

from pymyq import login
from pymyq.account import MyQAccount
from pymyq.errors import MyQError, RequestError
from pymyq.garagedoor import STATE_CLOSED
from notification import send
from device_info import get_lastknown_device_status, set_lastknown_device_status
from logutil import _LOGGER

MYQ_EMAIL = os.environ['MYQ_EMAIL']
MYQ_PASSWORD = os.environ['MYQ_PASSWORD']

MYQ_SEND_ANY_STATUS = os.getenv("MYQ_SEND_ANY_STATUS", 'False').lower() in ('true', '1', 't')

async def process_garagedoors(account: MyQAccount):
    """Process garage doors

    Args:
        account (MyQAccount): Account for which to retrieve garage doors
    """
    _LOGGER.info('GarageDoors: %d', len(account.covers))
    if len(account.covers) != 0:
        for idx, device in enumerate(account.covers.values()):
            _LOGGER.info('processing device %d', idx)
            send_notification = MYQ_SEND_ANY_STATUS
            try:
                lastknown_device_status = get_lastknown_device_status(
                    device)
                if device.state == STATE_CLOSED:
                    _LOGGER.info('%s %s is closed', account.name, device.name)
                    if (lastknown_device_status == None or device.device_state != lastknown_device_status['device_state']):
                        set_lastknown_device_status(device)
                else:
                    _LOGGER.info(
                        '%s %s is %s', account.name, device.name, device.device_state)
                    if (device.device_state != lastknown_device_status['device_state']):
                        set_lastknown_device_status(device)
                    send_notification = True
                if send_notification:
                    send(account.name, device)
            except RequestError as err:
                _LOGGER.error(err)


async def main() -> None:

    async with ClientSession() as websession:
        try:
            # Create an API object:
            api = await login(MYQ_EMAIL, MYQ_PASSWORD, websession)

            for account in api.accounts.values():
                _LOGGER.info('Account ID: %s', account.id)
                _LOGGER.info('Account Name: %s', account.name)

                # Get all devices listed with this account – note that you can use
                # api.covers to only examine covers or api.lamps for only lamps.
                await process_garagedoors(account=account)

        except MyQError as err:
            _LOGGER.error("There was an error: %s", err)

asyncio.get_event_loop().run_until_complete(main())
