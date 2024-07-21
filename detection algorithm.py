#===========================================================================================================================================
##MIT License

#Copyright (c) 2024 NightBlobby

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


#============================================================================================================================================



import asyncio
from bleak import BleakScanner, BleakClient
from plyer import notification
import nfc
import logging

# Define Nothing device identifiers and tags
NOTHING_DEVICES = {
    'Nothing Phone 1': 'A14C1',
    'Nothing Phone 2': 'A14C2',
    'Nothing Phone 2A': 'A14C3'
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10  # Notification duration in seconds
    )

async def bluetooth_scan():
    try:
        logger.info("Starting Bluetooth scan...")
        # Discover Bluetooth devices with a longer timeout
        devices = await BleakScanner.discover(timeout=20.0)
        if devices:
            detected_devices = set()
            for device in devices:
                device_name = device.name if device.name else "Unknown Device"
                logger.info(f"Bluetooth Device Found: {device.address} - {device_name}")

                # Check if the device is a Nothing device
                if any(nothing_name.lower() in device_name.lower() for nothing_name in NOTHING_DEVICES):
                    if device.address not in detected_devices:
                        show_notification("Bluetooth Device Detected", f"You passed by a {device_name} user!")
                        detected_devices.add(device.address)
                        logger.info(f"Detected Nothing Phone: {device_name}")
                else:
                    logger.info(f"Device is not a Nothing Phone: {device_name}")

                # Attempt to connect and retrieve services
                try:
                    async with BleakClient(device) as client:
                        if client.is_connected:
                            services = await client.get_services()
                            logger.info(f"Services for {device_name}: {services}")
                            for service in services:
                                logger.info(f"Service: {service}")
                        else:
                            logger.warning(f"Failed to connect to {device_name}")
                except Exception as e:
                    logger.error(f"Error accessing services for {device.address}: {e}")
        else:
            logger.warning("No Bluetooth devices found during the scan.")
    except Exception as e:
        logger.error(f"Error discovering Bluetooth devices: {e}")

def nfc_detect(tag):
    tag_id = tag.identifier.hex().upper()
    logger.info(f"NFC Tag Detected: {tag_id}")

    for nothing_name, tag_code in NOTHING_DEVICES.items():
        if tag_id == tag_code:
            show_notification("NFC Tag Detected", f"You passed by a {nothing_name} user!")
            logger.info(f"Detected Nothing Phone with NFC tag: {nothing_name}")

async def run_nfc_scan():
    try:
        clf = None
        possible_paths = ['usb', 'tty:S0', 'spi:']
        for path in possible_paths:
            try:
                clf = nfc.ContactlessFrontend(path)
                if clf:
                    break
            except IOError:
                logger.warning(f"Failed to find NFC reader on path {path}")

        if clf:
            logger.info("NFC scan started...")
            clf.connect(rdwr={'on-connect': nfc_detect})
            await asyncio.sleep(10)  # Keep the scan running for a while
            clf.close()
        else:
            logger.error("No NFC device found. Ensure your NFC reader is properly connected and recognized by your system.")
    except Exception as e:
        logger.error(f"Error during NFC scan: {e}")

async def main():
    # Run NFC scan in the background
    nfc_task = asyncio.create_task(run_nfc_scan())

    # Run Bluetooth scan concurrently
    await bluetooth_scan()

    # Wait for NFC scan to complete
    await nfc_task

# Run the main asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
