from network import LTE
from time import sleep
import usocket as socket


class StartIoT:

  # Network types chosen by user
  LTE_M = 'lte-m'
  NB_IOT = 'nb-iot'

  # Telenor NB-IoT band frequency
  BAND = 20

  # Telenor IoT Gateway APN
  APN = 'telenor.iotgw'

  # Telenor IoT Gateway IP address
  IOTGW_IP = '172.16.15.14'

  def __init__(self, network=StartIoT.LTE_M):
    self._network = network
    self.lte = LTE()

  def connect(self):
    # NB-IoT
    if (self._network == StartIoT.NB_IOT):
      self.lte.attach(band=StartIoT.BAND, apn=StartIoT.APN)
    # LTE-M (Cat M1)
    else:
      self.lte.attach()

    print('Attaching...')
    while not lte.isattached():
      sleep(0.25)
    print('Attached!')

    lte.connect()

    print('Connecting...')
    while not lte.isconnected():
      sleep(0.25)
    print('Connected!')

  def disconnect(self):
    if self.lte.isconnected():
      self.lte.disconnect()

  def dettach(self):
    if self.lte.isattached():
      self.lte.dettach()

  def send(self, data):
    if not self.lte.isconnected():
      raise Exception('Not connected! Unable to send.')

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    IP_ADDR = socket.getaddrinfo(StartIoT.IOTGW_IP, 1234)[0][-1]
    s.connect(IP_ADDR)
    s.send(data)
    s.close()
