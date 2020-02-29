# FiPy Dev-Kit CoAP Example Code

The example sends CoAP data packets over LTE-M (Cat M1) or NB-IoT network to Telenor Managed IoT Cloud (MIC).

## Prerequisites

Your Pycom FiPy dev-kit contains a Sequans modem. This modem needs to be flashed with firmware for the correct network protocol (LTE-M or NB-IoT). This must be done before you try to connect using the selected network protocol. The Sequans modem is by default flashed for LTE-M, so if you plan to use LTE-M you can skip this step.

Instructions on how to update or flash a different FiPy Sequans modem firmware can be found in the Pycom documentation here: https://docs.pycom.io/tutorials/lte/firmware/

## Change Network Protocol

The code will by default use the LTE-M network:

``` python
iot = StartIoT(network='lte-m')
```

To use the NB-IoT network (assuming you have flashed the modem as described in the prerequisites):

``` python
iot = StartIoT(network='nb-iot')
```

## Network Related Code Changes

The code in this repository reflects settings for the network in Telenor Norway. If your device will connect to a different network you will have to make some changes in [lib/telenor.py:11](./lib/telenor.py#L11) to reflect this:

``` python
# Network related configuration
BAND = 20                       # Telenor NB-IoT band frequency (use band 28 if you are in Finnmark)
APN = 'telenor.iotgw'           # Telenor IoT Gateway APN
IOTGW_IP = '172.16.32.1'        # Telenor IoT Gateway IP address
IOTGW_PORT = 5683               # Telenor IoT Gateway CoAP port
IOTGW_ENDPOINT = '/request/uri' # Telenor IoT Gateway CoAP endpoint
EARFCN = 6352                   # Telenor E-UTRA Absolute Radio Frequency Channel Number
COPS = 24201                    # Telenor network shortname
```
