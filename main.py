from telenor import StartIoT
from uos import urandom
from ujson import dumps
from time import sleep


def run():
  
  # Create a new Telenor Start IoT object using the LTE-M network.
  # Change the `network` parameter if you want to use the NB-IoT network
  # like this: iot = StartIoT(network='nb-iot')
  # You must flash the correct Sequans modem firmware before changing
  # network protocol!
  iot = StartIoT(network='lte-m')

  # Connect to the network
  print("Started connecting to the network...")
  iot.connect()

  # We should now be connected.
  # Start an endless loop and send some dummy data.
  while True:

    try:
      # Generate random data
      temperature = ((urandom(1)[0] / 256) * 10) + 20
      humidity = ((urandom(1)[0] / 256) * 10) + 60

      # Create the data payload
      payload = {
        "temperature": temperature,
        "humidity": humidity
      }

      # Format payload as a JSON string
      json = dumps(payload)

      print('Sending data:', json)

      # Send JSON string over the network
      iot.send(json)

    # Handle exception (if an error occured)
    except Exception as e:
      print('Caugh exception:', e)

    # Wait 10 seconds before running loop again
    sleep(10)

# The example code will start here
print('Running example code...')
run()
