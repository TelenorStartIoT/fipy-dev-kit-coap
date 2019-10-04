from network import LTE
from time import sleep
import usocket as socket


# Network types chosen by user
LTE_M = 'lte-m'
NB_IOT = 'nb-iot'

# Network related configuration
BAND = 20                 # Telenor NB-IoT band frequency
APN = 'mda.ee'            # Telenor IoT Gateway APN (telenor.iotgw)
IOTGW_IP = '172.16.15.14' # Telenor IoT Gateway IP address
EARFCN = 6352             # Telenor E-UTRA Absolute Radio Frequency Channel Number
COPS = 24201              # Telenor network shortname

class StartIoT:
  def __init__(self, network=LTE_M):
    self._network = network
    self.lte = LTE()

  def send_at_cmd_pretty(self, cmd):
    print('>', cmd)
    response = self.lte.send_at_cmd(cmd)
    if response != None:
      lines = response.split('\r\n')
      for line in lines:
        if len(line.strip()) != 0:
          print('>>', line)
    else:
      print('>> No response.')
    return response

  def connect(self):
    # NB-IoT
    if (self._network == NB_IOT):
      self.lte.send_at_cmd_pretty('AT+CFUN=0')
      self.lte.send_at_cmd_pretty('AT+CEMODE=0')
      self.lte.send_at_cmd_pretty('AT+CEMODE?')
      self.lte.send_at_cmd_pretty('AT!="clearscanconfig"')
      self.lte.send_at_cmd_pretty('AT!="addscanfreq band=%s dl-earfcn=%s"' % BAND, EARFCN)
      self.lte.send_at_cmd_pretty('AT+CGDCONT=1,"IP","%s"' % APN)
      self.lte.send_at_cmd_pretty('AT+COPS=1,2,"%s"' % COPS)
      self.lte.send_at_cmd_pretty('AT+CFUN=1')
      self.lte.attach()
    # LTE-M (Cat M1)
    else:
      self.send_at_cmd_pretty('AT+CFUN=0')
      self.send_at_cmd_pretty('AT+CGDCONT=1,"IP","%s"' % APN)
      self.send_at_cmd_pretty('AT+CFUN=1')
      self.send_at_cmd_pretty('AT+CSQ')

    print('Attaching...')
    while not self.lte.isattached():
      sleep(0.25)
    print('Attached!')

    self.lte.connect()

    print('Connecting...')
    while not self.lte.isconnected():
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
    IP_ADDR = socket.getaddrinfo(IOTGW_IP, 1234)[0][-1]
    s.connect(IP_ADDR)
    s.send(data)
    s.close()
