import logging
import re
import time

import serial
import serial.tools.list_ports

import numpy as np

logger = logging.getLogger('AE')
logger.setLevel(logging.DEBUG)
handler_debug = logging.StreamHandler()
formatterDetail = logging.Formatter("%(asctime)s %(levelname)s %(filename)s %(funcName)s line %(lineno)d %(module)s %(message)s")
formatterCompact = logging.Formatter("%(asctime)s %(levelname)s %(module)s %(funcName)s line %(lineno)d %(message)s")
handler_debug.setFormatter(formatterDetail)
handler_debug.setLevel(logging.DEBUG)
logger.addHandler(handler_debug)


# def scan_serial_ports():
# 		"""scan for available ports. return a list of tuples (num, name)"""
# 		available 
# 		for i in range(256):
# 			try:
# 				s = serial.Serial(i, timeout=3)
# 				available.append((i, s.portstr))
# 				s.close()  # explicit close 'cause of delayed GC in java
# 			except serial.SerialException:
# 				pass
# 		return available

class MotorsXYZ:
	"""
	class to communicate with the MotorsXYZ at baudrate speed
	"""

	def __init__(self, all_msgs, com_port=None, baudrate=115200, timeout=10):
		self.all_msgs = all_msgs

		self.com_port = com_port
		self.timeout = timeout
		self.baudrate = baudrate
		self.currentPos = [-1.0,-1.0,-1.0]

		#0 pattern: "X:([-+]?[0-9]*\.[0-9]*),Y:([-+]?[0-9]*\.[0-9]*),Z:([-+]?[0-9]*\.[0-9]*)"
		# https://regex101.com/#python
		self.pattern = "X:([-+]?[0-9]*\.[0-9]*),Y:([-+]?[0-9]*\.[0-9]*),Z:([-+]?[0-9]*\.[0-9]*)"
		self.M114_re = re.compile(self.pattern)

		self.connected = False

	def find_motor_port(self):
		motor_port_number = -1
		for port in serial.tools.list_ports.comports():
			com = serial.Serial(port.device, 115200, timeout=5)
			line = str(com.readline().rstrip(),'ascii')

			if(line != ''):
				self.all_msgs.appendMsg(line)
				if line == 'start':
					motor_port_number = port.device
			com.close()
		return motor_port_number

	def connect(self):
		if self.connected:
			self.all_msgs.appendMsg('Already connected to motor system!')
			return

		if self.com_port is None:
			self.com_port = self.find_motor_port()

		if self.com_port == -1:
			self.all_msgs.appendMsg(
							'Could not find Motor System. Check if plugged in and turned on?')
			return False
		

		self.open_com()
		self.connected = True
		
		self.all_msgs.appendMsg('Connected to motor system successfully!')
		self.currentPos = [-1,-1,-1]
		return [-1,-1,-1]

	def set_zero(self):
		ok = self.send_wait("G28 X Y Z\r\n")
		if ok != 'ok':
			self.all_msgs.appendMsg('Error in Zeroing. Will close connection')
			self.close_com()
			return False
		return True

	def open_com(self):
		self.com=serial.Serial(self.com_port,self.baudrate,timeout=self.timeout)

	def send_cmd(self,cmd):
		self.nb=self.com.write(cmd.encode())

	def wait_for_ok(self,timeout=5):
		start_time=time.time()
		finished=False
		while ( not finished ):
			line=str(self.com.readline().rstrip(),'ascii')
			if(line!=''):
				line=line[:2]
			finished = (line == 'ok') or (line == '!!') or ((time.time()-start_time)>timeout)
		return line

	def print_ans(self):
		for line in self.ans:
			self.all_msgs.appendMsg(line)

	def send_wait(self,cmd):
		self.nb=self.com.write(cmd.encode())
		ans=self.wait_for_ok()
		return ans

	def close_com(self):
		if not self.connected:
			self.all_msgs.appendMsg('Not connected to motor system!')
			return
		self.com.close()
		self.connected = False

	def getPos(self):
		ok=self.send_cmd("M114\r\n")
		finished = False
		tries = 5
		while not finished and tries > 0:
			line = str(self.com.readline(), 'ascii')
			split_str=line.split()
			if len(split_str) < 1:
				tries -= 1
				continue
			if split_str[0] == 'ok':
				if len(split_str) > 1:
					match_M114=self.M114_re.match(split_str[1])
					self.currentPos = [float(x) for x in match_M114.groups()]
				else:
					self.currentPos = [-1.0,-1.0,-1.0]
				finished = True
			else:
				if split_str[0]=='!!':
					self.all_msgs.appendMsg("error: " + str(split_str[1]))
					self.currentPos = [-1.0,-1.0,-1.0]
					return None
					finished = True
			tries -= 1
		return self.currentPos

	def moveRel(self,coords):
		#Construct move command from the motor system
		cmd = "G1 X{:.2f} Y{:.2f} Z{:.2f}\r\n".format(coords[0],coords[1],coords[2])
		ok = self.send_wait(cmd)
		if ok != 'ok':
			self.all_msgs.appendMsg('Hit motor edge!')

		self.currentPos = self.getPos()
		
		return self.currentPos

	def moveAbs(self,coords):
		if any(np.array(self.currentPos) < 0):
			self.all_msgs.appendMsg('Cannot move without initializing zero')
			return
		move_coords = np.array(coords) - np.array(self.currentPos)
		return self.moveRel(move_coords)

	def test_move(self,dist):
		tot_times = np.zeros(3)
		for axis in range(3):
			move_one = np.zeros(3)
			move_two = np.zeros(3)
			move_one[axis] = dist
			move_two[axis] = -dist

			start = time.time()
			for i in range(25):
				self.moveRel(move_one)
				self.moveRel(move_two)

			tot_times[axis] = (time.time() - start)/50

		print('Times: ' + str(tot_times))
				
