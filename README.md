# FiPy Dev-Kit UDP Example Code

Pycom FiPy UDP over LTE-M (Cat M1) or NB-IoT example. The example sends UDP data packets over LTE-M (Cat M1) or NB-IoT network to Telenor Start IoT Managed IoT Cloud (MIC).

## Prerequsites

Your Pycom FiPy dev-kit contains a Sequans modem. This modem needs to be flashed with firmware for the correct network protocol (LTE-M or NB-IoT). This must be done before you try to connect using the selected network protocol. The Sequans modem is by default flashed for LTE-M, so if you plan to use LTE-M you can skip this step.

Instructions on how to update or flash a different FiPy Sequans modem firmware can be found in the Pycom documentation here: https://docs.pycom.io/tutorials/lte/firmware/

## Network Related Code Changes

The code in this repository reflects settings for the NB-IoT network in Telenor Norway. If your device will connect to a different network you will have to make some changes in [lib/telenor.py](./lib/telenor.py) to reflect this:

  * Change band (from 20 to the band you are using)
  * Change earfcn (from 6352 to your networks earfcn)
  * Change APN name (from telenor.iotgw to your APN name)
  * Change network shortname (from 24201 to your network shortname)

Example:

```
TODO :)
```
