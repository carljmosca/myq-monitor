"""

notifcation

"""

import os
import vonage

from logutil import _LOGGER

MYQ_SMS_RECIPIENTS = os.environ['MYQ_SMS_RECIPIENTS']
VONAGE_CLIENT_KEY = os.environ['VONAGE_CLIENT_KEY']
VONAGE_CLIENT_SECRET = os.environ['VONAGE_CLIENT_SECRET']
VONAGE_CLIENT_SMS_NUMBER = os.environ['VONAGE_CLIENT_SMS_NUMBER']

vonageClient = vonage.Client(
    key=VONAGE_CLIENT_KEY, secret=VONAGE_CLIENT_SECRET)
vonageSms = vonage.Sms(vonageClient)

def send(account_name, device):

    recipients = MYQ_SMS_RECIPIENTS.split(",")
    for x in range(len(recipients)):

        _LOGGER.info('Sending message to %s', recipients[x])
        responseData = vonageSms.send_message(
            {
                "from": VONAGE_CLIENT_SMS_NUMBER,
                "to": recipients[x],
                "text": account_name + " " + device.name + " is " + device.device_state,
            }
        )

        if responseData["messages"][0]["status"] == "0":
            _LOGGER.info('Message sent successfully.')
        else:
            _LOGGER.error(
                'Message failed with error: %s', responseData['messages'][0]['error-text'])

