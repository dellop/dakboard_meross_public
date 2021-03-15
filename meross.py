#FILL IN <email>,<password>,thingspeak<api_key>


import asyncio
import os
import urllib

from meross_iot.controller.mixins.garage import GarageOpenerMixin
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager

EMAIL = os.environ.get('MEROSS_EMAIL') or "<email>"
PASSWORD = os.environ.get('MEROSS_PASSWORD') or "<password>"
door_status=0

async def main():
    # Setup the HTTP client API from user-password
    http_api_client = await MerossHttpClient.async_from_user_password(email=EMAIL, password=PASSWORD)

    # Setup and start the device manager
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()

    # Retrieve all the devices that implement the garage-door opening mixin
    await manager.async_device_discovery()
    openers = manager.find_devices(device_class=GarageOpenerMixin)

    if len(openers) < 1:
        sys.exit(1)
    else:
        dev = openers[0]

        # Update device status: this is needed only the very first time we play with this device (or if the
        #  connection goes down)
        await dev.async_update()

        # Check current door status
        open_status = dev.get_is_open()
        if open_status:
            door_status=1
        else:
            door_status=2


	#SEND TO THINGSPEAK
        thingSpeakURL = 'https://api.thingspeak.com/update?api_key=<API_KEY>&field1='
        f = urllib.request.urlopen(thingSpeakURL+str(door_status))
        f.read()
        f.close()

        # To open the door, uncomment the following:
        #print(f"Opening door {dev.name}...")
        #await dev.open(channel=0)
        #print("Door opened!")
        #
        # Wait a bit before closing it again
        #await asyncio.sleep(5)
        #
        #print(f"Closing door {dev.name}...")
        #await dev.close()
        # print(f"Door closed!")

    # Close the manager and logout from http_api
    manager.close()
    await http_api_client.async_logout()

if __name__ == '__main__':
    # On Windows + Python 3.8, you should uncomment the following
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
