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

The code in this repository reflects settings for the network in Telenor Norway. If your device will connect to a different network you will have to make some changes in [lib/telenor.py:10](./lib/telenor.py#L10) to reflect this:

``` python
# Network related configuration
BAND = 20                       # Telenor NB-IoT band frequency (use band 28 if you are in Finnmark close to the Russian border)
APN = 'telenor.iotgw'           # Telenor IoT Gateway APN
IOTGW_IP = '172.16.32.1'        # Telenor IoT Gateway IP address
IOTGW_PORT = 5683               # Telenor IoT Gateway CoAP port
IOTGW_ENDPOINT = '/'            # Telenor IoT Gateway CoAP endpoint
EARFCN = 6352                   # Telenor E-UTRA Absolute Radio Frequency Channel Number
COPS = 24201                    # Telenor Norway MNC-MCC
```

## Downlink Messages

When using CoAP there are two ways you can get messages downlink from Telenor Managed IoT Cloud to your FiPy device; CoAP pull and CoAP push. A starting point for each transport method is included but the functionality vary depending on your use-case and it most likely requires some modification to the code on your side.

### CoAP Pull

If messages are sent downlink from Telenor Managed IoT Cloud using the `coap-pull` transport they will end up in a queue. The device is then responsible for pulling messages from this queue. This can be done by invoking the `StartIoT.pull(path='/')` method, which in turn will make a CoAP GET request that will return any potentially queued massages.

### CoAP Push

If messages are sent downlink from Telenor Managed IoT Cloud using the `coap-push` transport they will be sent directly to the device. The device must then implement a CoAP server which can handle incoming CoAP requests from the IoT Gateway. By invoking the `StartIoT.setup_coap_server()` method a simple CoAP server will be setup.
