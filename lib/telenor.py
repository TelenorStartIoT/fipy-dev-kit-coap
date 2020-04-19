from network import LTE
from time import sleep
from network import Coap
from machine import reset
import uselect
import _thread


# Network types chosen by user
LTE_M = 'lte-m'
NB_IOT = 'nb-iot'

# Network related configuration
BAND = 20                       # Telenor NB-IoT band frequency (use band 28 if you are in Finnmark close to the Russian border)
APN = 'telenor.iotgw'           # Telenor IoT Gateway APN
IOTGW_IP = '172.16.32.1'        # Telenor IoT Gateway IP address
IOTGW_PORT = 5683               # Telenor IoT Gateway CoAP port
IOTGW_ENDPOINT = '/'            # Telenor IoT Gateway CoAP endpoint
EARFCN = 6352                   # Telenor E-UTRA Absolute Radio Frequency Channel Number
COPS = 24201                    # Telenor Norway MNC-MCC

attach_timeout = 60  # Attach timeout in seconds. If this is exceeded, the exception AttachTimeout will be raised.
connect_timeout = 60 # Connect timeout in seconds. If this is exceeded, the exception ConnectTimeout will be raised.

class WrongNetwork(Exception): # Exception for when the network is configured wrong.
  pass
class AttachTimeout(Exception): # Exception for when the attach process reaches a timeout (configured above)
  pass
class ConnectTimeout(Exception): # Exception for when the connection process reaches a timeout (configured above)
  pass

# Thread handling the sockets
def socket_thread(p, coap_socket):
  while True:
    # Wait for any socket to become available
    sockets = p.poll()
    for s in sockets:
      sock = s[0]
      event = s[1]
      if (event & uselect.POLLIN):
        # Check if the socket belongs to the CoAP module
        if (sock == coap_socket):
          # Call Coap.read() which parses the incoming CoAP message
          Coap.read()

class StartIoT:
  def __init__(self, network=LTE_M):
    self._network = network
    self.lte = LTE()
    try:
      self.lte.deinit()
      self.lte.reset()
    except:
      pass
    sleep(5)

    self.lte.init()
    sleep(5)

    self._assure_modem_fw()

  def _assure_modem_fw(self):
    response = self.lte.send_at_cmd('ATI1')
    if response != None:
      lines = response.split('\r\n')
      fw_id = lines[1][0:3]
      is_nb = fw_id == 'UE6'
      if is_nb:
        print('Modem is using NB-IoT firmware (%s/%s).' % (lines[1], lines[2]))
      else:
        print('Modem in using LTE-M firmware (%s/%s).' % (lines[1], lines[2]))
      if not is_nb and self._network == NB_IOT:
        print('You cannot connect using NB-IoT with wrong modem firmware! Please re-flash the modem with the correct firmware.')
        raise WrongNetwork
      if is_nb and self._network == LTE_M:
        print('You cannot connect using LTE-M with wrong modem firmware! Please re-flash the modem with the correct firmware.')
        raise WrongNetwork
    else:
      print('Failed to determine modem firmware. Rebooting device...')
      reset() # Reboot the device

  def _get_assigned_ip(self):
    ip_address = None
    try:
      self.lte.pppsuspend()
      response = self.send_at_cmd_pretty('AT+CGPADDR=1')
      self.lte.pppresume()
      lines = response.split('\r\n')
      sections = lines[1].split('"')
      ip_address = sections[1]
    except:
      print('Failed to retrieve assigned IP from LTE network.')

    return ip_address

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
      self.send_at_cmd_pretty('AT+CFUN=0')
      self.send_at_cmd_pretty('AT+CEMODE=0')
      self.send_at_cmd_pretty('AT+CEMODE?')
      self.send_at_cmd_pretty('AT!="clearscanconfig"')
      self.send_at_cmd_pretty('AT!="addscanfreq band=%s dl-earfcn=%s"' % (BAND, EARFCN))
      self.send_at_cmd_pretty('AT+CGDCONT=1,"IP","%s"' % APN)
      self.send_at_cmd_pretty('AT+COPS=1,2,"%s"' % COPS)
      self.send_at_cmd_pretty('AT+CFUN=1')

    # LTE-M (Cat M1)
    else:
      self.send_at_cmd_pretty('AT+CFUN=0')
      self.send_at_cmd_pretty('AT!="clearscanconfig"')
      self.send_at_cmd_pretty('AT!="addscanfreq band=%s dl-earfcn=%s"' % (BAND, EARFCN))
      self.send_at_cmd_pretty('AT+CGDCONT=1,"IP","%s"' % APN)
      self.send_at_cmd_pretty('AT+CFUN=1')
      self.send_at_cmd_pretty('AT+CSQ')

    # For a range scan:
    # AT!="addscanfreqrange band=20 dl-earfcn-min=3450 dl-earfcn-max=6352"

    print('Attaching...')
    seconds = 0
    while not self.lte.isattached() and seconds < attach_timeout:
      sleep(0.25)
      seconds += 0.25
    if self.lte.isattached():
      print('Attached!')
    else:
      print('Failed to attach to LTE (timeout)!')
      raise AttachTimeout
    self.lte.connect()

    print('Connecting...')
    seconds = 0
    while not self.lte.isconnected() and seconds < connect_timeout:
      sleep(0.25)
      seconds += 0.25
    if self.lte.isconnected():
      print('Connected!')
    else:
      print('Failed to connect to LTE (timeout)!')
      raise ConnectTimeout

    print('Retrieving assigned IP...')
    ip_address = self._get_assigned_ip()

    print("Device IP: {}".format(ip_address))
    print(ip_address)

    # Initialise the CoAP module
    Coap.init(ip_address)

    # Register the response handler for the requests that the module initiates as a CoAP Client
    Coap.register_response_handler(self.response_callback)

    # A CoAP server is needed if CoAP push is used (messages are pushed down from Managed IoT Cloud)
    # self.setup_coap_server()

  def setup_coap_server(self):
    # Add a resource with a default value and a plain text content format
    r = Coap.add_resource('', media_type=Coap.MEDIATYPE_APP_JSON, value='default_value')
    # Configure the possible operations on the resource
    r.callback(Coap.REQUEST_GET | Coap.REQUEST_POST | Coap.REQUEST_PUT | Coap.REQUEST_DELETE, True)

    # Get the UDP socket created for the CoAP module
    coap_server_socket = Coap.socket()
    # Create a new poll object
    p = uselect.poll()
    # Register the CoAP module's socket to the poll
    p.register(coap_server_socket, uselect.POLLIN | uselect.POLLHUP | uselect.POLLERR)
    # Start a new thread which will handle the sockets of "p" poll
    _thread.start_new_thread(socket_thread, (p, coap_server_socket))

    print('CoAP server running!')

  # The callback that handles the responses generated from the requests sent to a CoAP Server
  def response_callback(self, code, id_param, type_param, token, payload):
    # The ID can be used to pair the requests with the responses
    print('ID: {}'.format(id_param))
    print('Code: {}'.format(code))
    print('Type: {}'.format(type_param))
    print('Token: {}'.format(token))
    print('Payload: {}'.format(payload))

  def disconnect(self):
    if self.lte.isconnected():
      self.lte.disconnect()

  def dettach(self):
    if self.lte.isattached():
      self.lte.dettach()

  def send(self, data):
    if not self.lte.isconnected():
      raise Exception('Not connected! Unable to send.')

    id = Coap.send_request(IOTGW_IP, Coap.REQUEST_POST, uri_port=IOTGW_PORT, uri_path=IOTGW_ENDPOINT, payload=data, include_options=True)
    print('CoAP POST message ID: {}'.format(id))

  def pull(self, uri_path='/'):
    if not self.lte.isconnected():
      raise Exception('Not connected! Unable to pull.')

    id = Coap.send_request(IOTGW_IP, Coap.REQUEST_GET, uri_port=IOTGW_PORT, uri_path=uri_path, include_options=True)
    Coap.read()
    print('CoAP GET message ID: {}'.format(id))
