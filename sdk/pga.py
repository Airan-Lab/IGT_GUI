# -*- coding: utf-8 -*-

# This module is compatible with both Python 2.x and 3.x.

"""
.. xxx module:: pga
   :platform: Windows, Linux
   :synopsis: Python module to control the BBBOp/Cube Generator board (PGA)

.. moduleauthor:: IGT (Image Guided Therapy)
"""
import os
import time
import struct
import json
import serial
import serial.tools.list_ports
import serial.tools.list_ports
from serial.serialutil import SerialException


version = (1, 1, 0)
"""Module version as a tuple of integers (major, minor, bugfix)."""

versionstr = ".".join(map(str,version))
"""Module version as a string "major.minor.bugfix"."""


class Pulse(object):
	"""
	Definition of one pulse within a sequence. Its attributes are:

	- duration(int):  the pulse emission duration, in microseconds
	- delay(int):     the delay until the next pulse in the sequence, in microseconds
	- amplitude(int): the pulse amplitude, in [0,1023], 0=none, 1023=max power
	- frequency(int): the pulse frequency, in Hertz.
	"""

	def __init__ (self, dura, dela, ampl, freq):
		"""
		Creates a pulse with specified settings.

		:param int dura: the duration in microseconds.
		:param int dela: the delay in microseconds.
		:param int ampl: the amplitude, in [0, 1023].
		:param int freq: the frequency in Hertz.
		:return: a new Pulse object.
		"""
		self.duration  = dura
		self.delay     = dela
		self.amplitude = ampl
		self.frequency = freq


class PulseResult(object):
	"""
	A simple structure holding pulse measures. Its attributes are:

	- execIndex(int):   index of the execution (if repeated, from 0),
	- execID(int):      execution identifier as specified in executeSequence (0 if not supported),
	- pulseIndex(int):  index of this pulse within the sequence (from 0),
	- duration(int):    real duration of this pulse in microseconds,
	- fwdPowerADC(int): forward (emitted) power as raw ADC (16 bits),
	- revPowerADC(int): reverse (reflected) power as raw ADC (16 bits).
	"""

	def __init__ (self, protover, data):
		if protover < 2:
			d = struct.unpack ("<IIIHH", data)
			self.execIndex   = d[0]
			self.execID      = 0
			self.pulseIndex  = d[1]
			self.duration    = d[2]
			self.fwdPowerADC = d[3]
			self.revPowerADC = d[4]
		else:
			d = struct.unpack ("<IHHIHH", data)
			self.execIndex   = d[0]
			self.execID      = d[2]
			self.pulseIndex  = d[1]
			self.duration    = d[3]
			self.fwdPowerADC = d[4]
			self.revPowerADC = d[5]
		if self.execIndex == 0xFFFFFFFF:
			self.execIndex  = None
			self.execID     = None
			self.pulseIndex = None

	def __str__(self):
		if self.execIndex is None:
			msg = "Measure: no exec, "
		else:
			msg = "Measure: exec#: %d, execID: %d, pulse#: %d, " % (
				self.execIndex,
				self.execID,
				self.pulseIndex)
		msg += "dur: %d, fwd: %d, rev: %d" % (self.duration, self.fwdPowerADC, self.revPowerADC)
		return msg


class ExecutionStatus(object):
	"""
	A simple structure holding execution status information. Its attributes are:

	- execIndex(int):      index of the execution (if repeated, from 0), None if no execution
	- execID(int):         execution identifier as specified in :meth:`Generator.executeSequence`, None if no execution or not supported,
	- pulseIndex(int):     index of this pulse within the sequence (from 0), None if no execution
	- status(int):         status bit mask,
	- temperatureADC(int): temperature as raw ADC (16 bits),
	- currentADC(int):     current as raw ADC (16 bits).
	- voltageADC(int):     voltage as raw ADC (16 bits).
	"""

	def __init__ (self, protover, data):
		if protover < 2:
			d = struct.unpack ("<IIIIIII", data)
			self.execID     = None
			self.status     = d[3]
			self.temperatureADC = d[4]
			self.currentADC = d[5]
			self.voltageADC = d[6]
		else:
			d = struct.unpack ("<IIHHIIII", data)
			self.execID     = d[3]
			self.status     = d[4]
			self.temperatureADC = d[5]
			self.currentADC = d[6]
			self.voltageADC = d[7]
		self.execIndex  = d[1]
		self.pulseIndex = d[2]
		if self.execIndex == 0xFFFFFFFF:
			self.execIndex  = None
			self.execID     = None
			self.pulseIndex = None

	def __str__(self):
		if self.execIndex is None:
			msg = "Status: no exec, "
		else:
			msg = "Status: exec#: %d, execID: %d, pulse#: %d, " % (
				self.execIndex,
				self.execID,
				self.pulseIndex)
		msg += "status[{:08b}]: ".format(self.status)
		msg += self.statusMessage()
		msg += ", T: %d, I: %d, V: %d" % (self.temperatureADC, self.currentADC, self.voltageADC)
		return msg

	def statusMessage(self):
		"""Returns a human readable message corresponding to the current status."""
		if self.status == 0:
			return "Ok"

		ERRORS = {
			0: "RF channel disabled",
			1: "Amplifier power supply disabled",
			2: "Emergency stop active",
			3: "Watchdog error",
			4: "Timing error",
			5: "Unexpected trigger-in event during execution"
		}

		msg = ""
		for i in range(len(ERRORS)):
			bit = 1 << i
			if (self.status & bit) != 0:
				if len(msg) == 0:
					msg = ERRORS[i]
				else:
					msg += ", "+ERRORS[i]
		return msg


class Output(object):
	"""
	Possible parameters/returned value for :meth:`Generator.selectOutput()` and :meth:`Generator.output()`.

	- ``INTERNAL``: One of the possible targets for the main generator output. This one is an internal load of 50 ohms.
	- ``EXTERNAL``: One of the possible targets for the main generator output. This one leads to the external connector usually connected to a transducer.
	"""

	INTERNAL = 0
	"""
	One of the possible targets for the main generator output.
	This one is an internal load of 50 ohms.
	"""

	EXTERNAL = 1
	"""
	One of the possible targets for the main generator output.
	This one leads to the external connector usually connected to a transducer.
	"""


class _Parameter(object):
	def __init__(self, pid, editable, cacheable, init, optional, value):
		self.id = pid
		self.editable  = editable
		self.cacheable = cacheable
		self.reqOnInit = init
		self.optional  = optional
		self.defaultValue = value
#

class Param(object):
	"""
	Enumeration of all available parameters usable with :meth:`Generator.readParameter` and :meth:`Generator.writeParameter`.
	"""

	HARDWARE_VERSION = 0
	FIRMWARE_VERSION = 1
	BOARD_IDENTIFIER = 2
	FORWARD_POWER_MAX = 3
	REVERSE_POWER_MAX = 4
	POWER_RATIO_MAX = 5
	TRANSMITTED_POWER_MAX = 6
	AMPLIFIER_TEMPERATURE_MAX = 7
	AMPLIFIER_CURRENT_MAX = 8
	AMPLIFIER_VOLTAGE_MIN = 9
	AMPLIFIER_VOLTAGE_MAX = 10
	AMPLIFIER_INPUT_POWER_MAX = 11
	AMPLIFIER_FREQUENCY_MIN = 12
	AMPLIFIER_FREQUENCY_MAX = 13
	PULSE_COUNT_MAX = 14
	PULSE_DURATION_MIN = 15
	PULSE_DURATION_MAX = 16
	PULSE_DURATION_TOLERANCE = 17
	PULSE_LENGTH_MIN = 18
	PULSE_LENGTH_MAX = 19
	PULSE_LENGTH_TOLERANCE = 20
	EXECUTION_DELAY_MAX = 21
	WATCHDOG_TIME = 22
	SEQUENCE_DUTY_CYCLE_PERMIL = 23
	STATUS_FLAGS = 24
	SAFETY_FLAGS = 25
	DEBUG_FLAGS = 26
	FORWARD_POWER_ALARM = 27
	TRIGGER_IN_FLAGS = 28
	FEATURE_FLAGS = 29

	FIRST = 0 # first valid
	LAST = 29  # last valid


	DEFAULTS = {
		# local ID:                         proto ID, editable, cacheable, reqOnInit, optional, def value
		HARDWARE_VERSION:           _Parameter( 1000, False, True, False, False,       1234),
		FIRMWARE_VERSION:           _Parameter( 1001, False, True, False, False,       5678),
		BOARD_IDENTIFIER:           _Parameter( 1002, False, True, False, False,      55555),
		STATUS_FLAGS:               _Parameter( 2000, True,  False,False, False,          0),
		SAFETY_FLAGS:               _Parameter( 2001, True,  True, False, False,      0x3FB),
		FORWARD_POWER_MAX:          _Parameter( 3000, True,  True, True,  False,       3800), # 0xFFFFFFFF
		REVERSE_POWER_MAX:          _Parameter( 3001, True,  True, True,  False,        800), # 0xFFFFFFFF
		POWER_RATIO_MAX:            _Parameter( 3002, True,  True, True,  False,          1),
		TRANSMITTED_POWER_MAX:      _Parameter( 3003, True,  True, True,  False,   16000000), # 0xFFFFFFFF
		AMPLIFIER_TEMPERATURE_MAX:  _Parameter( 3004, True,  True, True,  False,       3522), # 0xFFFFFFFF
		AMPLIFIER_CURRENT_MAX:      _Parameter( 3005, True,  True, True,  False,       1551), # 0xFFFFFFFF
		AMPLIFIER_VOLTAGE_MIN:      _Parameter( 3006, True,  True, True,  False,       1427), # 0
		AMPLIFIER_VOLTAGE_MAX:      _Parameter( 3007, True,  True, True,  False,       3072), # 0xFFFFFFFF
		AMPLIFIER_INPUT_POWER_MAX:  _Parameter( 3008, True,  True, True,  False,    5197308), # 0xFFFFFFFF
		AMPLIFIER_FREQUENCY_MIN:    _Parameter( 3009, False, True, False, False,     600000),
		AMPLIFIER_FREQUENCY_MAX:    _Parameter( 3010, False, True, False, False,    7000000),
		FORWARD_POWER_ALARM:        _Parameter( 3011, True,  True, False, True,  0xFFFFFFFF),
		PULSE_COUNT_MAX:            _Parameter( 4000, False, True, False, False,         20),
		PULSE_DURATION_MIN:         _Parameter( 4001, False, True, False, False,          0),
		PULSE_DURATION_MAX:         _Parameter( 4002, False, True, False, False,  700000000),
		PULSE_DURATION_TOLERANCE:   _Parameter( 4003, True,  True, False, False,         50),
		PULSE_LENGTH_MIN:           _Parameter( 4004, False, True, False, False,       1000),
		PULSE_LENGTH_MAX:           _Parameter( 4005, False, True, False, False,  700000000),
		PULSE_LENGTH_TOLERANCE:     _Parameter( 4006, True,  True, False, False,        200),
		EXECUTION_DELAY_MAX:        _Parameter( 4007, False, True, False, False,   90000000),
		WATCHDOG_TIME:              _Parameter( 4008, False, True, False, False,      50000),
		SEQUENCE_DUTY_CYCLE_PERMIL: _Parameter( 4009, True,  True, False, False,       1000),
		TRIGGER_IN_FLAGS:           _Parameter( 4010, False, True, False, True,           0),
		FEATURE_FLAGS:              _Parameter( 5000, False, True, False, True,           0),
		DEBUG_FLAGS:                _Parameter(10000, True,  True, False, False,          0)
	}


#--------------------------------------------------------------------
# Execution flags

class ExecFlag(object):
	"""
	Available execution flags (for :meth:`Generator.executeSequence()`).
	These flags can be combined with a logical or (|).

	- ``ASYNC_PULSE_RESULT``: Sends pulse measures asynchronously during execution.
	- ``ASYNC_EXECUTION_RESULT``: Sends one final execution result (after all executions).
	- ``TRIGGER_RAISING``: Trigger mode on rising edge of signal.
	- ``TRIGGER_FALLING``: Trigger mode on falling edge of signal.
	- ``TRIGGER_PULSE_MODE``: Only used if ``TRIGGER_RAISING`` or ``TRIGGER_FALLING`` is set,
	  should be 0 otherwise.

	  - 0 = sequence mode (one trigger=starts one execution) requires nb_executions
	    trigger events to execute all shots.
	  - 1 = pulse mode (one trigger=execute the next pulse in the sequence),
	    requires nb_executions*nb_pulses_in_sequence trigger events to execute all shots.

	    .. note:: in this mode the delay of each pulse is spent **before** emitting ultrasounds.

	- ``TRIGGER_IGNORE_UNEXPECTED``: Only used if ``TRIGGER_RAISING`` or ``TRIGGER_FALLING`` is set,
	  should be 0 otherwise.

	  - 0 = if an unexpected trigger_in event is received (while already executing a pulse/sequence)
	    the current execution is stopped and an error (system event) is returned
	  - 1 = the unexpected event is simply ignored.

	- ``TRIM_RESULTS_10``: Asks the generator to only send pulse results every 10 executions.
	  Only one TRIM_RESULTS_* can be used at a time.
	  Only available if TRIM_RESULTS is set in the FEATURE_FLAGS parameter.
	- ``TRIM_RESULTS_100``: Same as :data:`TRIM_RESULTS_10`, but once every 100 executions.
	- ``TRIM_RESULTS_1000``: Same as :data:`TRIM_RESULTS_10`, but once every 1000 executions.

	"""

	ASYNC_PULSE_RESULT        = 1 << 0
	"""Sends pulse measures asynchronously during execution."""

	ASYNC_EXECUTION_RESULT    = 1 << 1
	"""Sends one final execution result (after all executions)."""

	TRIGGER_RAISING           = 1 << 2
	"""Trigger mode on rising edge of signal."""

	TRIGGER_FALLING           = 1 << 3
	"""Trigger mode on falling edge of signal."""

	TRIGGER_PULSE_MODE        = 1 << 4
	"""Only used if :data:`TRIGGER_RAISING` or :data:`TRIGGER_FALLING` is set, should be 0 otherwise.

	- 0 = sequence mode (one trigger=starts one execution) requires nb_executions
	  trigger events to execute all shots.
	- 1 = pulse mode (one trigger=execute the next pulse in the sequence),
	  requires nb_executions*nb_pulses_in_sequence trigger events to execute all shots.

	  .. note:: in this mode the delay of each pulse is spent **before** emitting ultrasounds.
	"""

	TRIGGER_IGNORE_UNEXPECTED = 1 << 5
	"""
	Only used if :data:`TRIGGER_RAISING` or :data:`TRIGGER_FALLING` is set, should be 0 otherwise.

	- 0 = if an unexpected trigger_in event is received (while already executing a pulse/sequence)
	  the current execution is stopped and an error (system event) is returned
	- 1 = the unexpected event is simply ignored.
	"""

	TRIM_RESULTS_10           = 1 << 6
	"""
	Asks the generator to only send pulse results every 10 executions.
	Only one TRIM_RESULTS_* can be used at a time.
	Only available if TRIM_RESULTS is set in the FEATURE_FLAGS parameter.
	"""

	TRIM_RESULTS_100          = 1 << 7
	"""Same as :data:`TRIM_RESULTS_10`, but once every 100 executions."""

	TRIM_RESULTS_1000         = (1 << 6) | (1 << 7)
	"""Same as :data:`TRIM_RESULTS_10`, but once every 1000 executions."""


#--------------------------------------------------------------------
# Error messages

class PGAError(Exception):
	"""Custom exception type for PGA errors."""

	def __init__(self, msg):
		Exception.__init__(self, msg)
#


# Base error messages.
# Warning: some expect an argument, some do not!
_ERROR_MESSAGE = {
100: "Bad packet size (%d).",
101: "Forbidden character at position %d.",
102: "CRC error (as seen by the generator).",

110: "Unknown command.",
111: "Bad argument size (%d).",
112: "Bad argument at index %d.",
113: "Bad combination of arguments (id: %d).",
113001: "Pulse length is too small.",
113002: "No pulse measures requested, but trim mode (10/100/1000) set.",
113003: "Pulse duty cycle is above maximum.",

120: "No sequence defined, thus no execution is possible.",
121: "Command canceled because it takes too long.",
122: "Impossible to execute for hardware reason.",
123: "This command is not possible during an execution.",
124: "Parameter (get/set) not initialized (id: %d).",
125: "Subsystem not ready (id: %d).",
125001: "Watchdog not initialized.",
130: "System unable to execute this command.",

# errors below this line are synchronous errors (but can be raised when clearing status)
200: "Security threshold override: forward power.",
201: "Security threshold override: reverse power.",
202: "Security threshold override: power ratio.",
203: "Security threshold override: transmitted power.",
204: "Security threshold override: amplifier temperature.",
205: "Security threshold override: amplifier current.",
206: "Security threshold override: amplifier voltage.",
207: "Security threshold override: amplifier power.",
208: "Security threshold override: pulse duration tolerance.",
209: "Security threshold override: pulse length tolerance.",

220: "Emergency stop (state=%d).",
221: "Watchdog error.",
222: "Unexpected trigger-in pulse received.",

230: "Internal message queue is full.",
}

def _ErrorMessage (code, value):
	# Special cases first
	if code in (113, 125) and value > 113000 and value in _ERROR_MESSAGE:
		return _ERROR_MESSAGE[value]
	# Messages using 'value'
	if code in (100, 101, 111, 112, 113, 124, 125):
		return _ERROR_MESSAGE[code] % value
	# Simple messages where 'value' is ignored
	if code in _ERROR_MESSAGE:
		return _ERROR_MESSAGE[code]
	return "Unknown error (sorry)."
#


def hardwareVersionToString (hwversion):
	"""
	Converts a raw integer value into a human readable string a.b.c.d.

	:param int hwversion: raw value as received from the generator
	:return str: a human readable string 'a.b.c.d'.
	"""
	if ((hwversion >> 30) & 1) != 0:
		# new format 30-22 + 21-16
		# mask here with 0xFF instead of 0x3FF to ignore the first two bits
		a = (hwversion >> 22) & 0xFF
		# this one should always be 17
		b = (hwversion >> 16) & 0x3F
		c = (hwversion >> 8) & 0xFF
		d = (hwversion & 0xFF)
	else:
		# old format
		a = 2000 + ((hwversion >> 26) & 0x3F)  # 2000 + first 6 bits (MSB)
		b = (hwversion >> 22) & 0x0F  # 4 next bits
		c = (hwversion >> 16) & 0x3F  # 6 next bits
		d = (hwversion & 0xFFFF)  # last 16 bits (LSB)
	return "%d.%d.%d.%d" % (a, b, c, d)
#


def firmwareVersionToString (fwversion):
	"""
	Converts a raw integer value into a human readable string a.b.c.d.

	:param int fwversion: raw value as received from the generator
	:return str: a human readable string 'a.b.c.d'.
	"""
	a = (fwversion >> 24) & 0xFF
	b = (fwversion >> 16) & 0xFF
	c = (fwversion >> 8) & 0xFF
	d = fwversion & 0xFF
	return "%d.%d.%d.%d" % (a, b, c, d)
#


def _computePolyVal(poly, value):
	"""
	Evaluates a polynomial at a specific value.
	
	:param poly: a list of polynomial coefficients, (first item = highest degree to last item = constant term).
	:param value: number used to evaluate poly
	:return: a number, the evaluation of poly with value
	"""
	#return numpy.polyval(poly, value)
	acc = 0
	for c in poly:
		acc = acc * value + c
	return acc


class LogLevel(object):
	"""Possible log levels. Messages above the selected level are ignored.

	- ``NOTHING``: Disable any output.
	- ``ERROR``: Only print error messages.
	- ``EVENT``: Print event messages from the firmware.
	- ``INFO``: Print general information.
	- ``VERBOSE``: Print more details.
	"""

	NOTHING = 0
	"""Disable any output."""

	ERROR = 10
	"""Only print error messages."""

	EVENT = 20
	"""Print event messages from the firmware."""

	INFO = 30
	"""Print general information."""

	VERBOSE = 40
	"""Print more details."""

	PACKET = 50
	ALL = 100
#


class Generator(object):
	"""The main class that respresents the hardware generator."""

	_CMD_PARAM_GET = "gp"
	_CMD_PARAM_SET = "sp"
	_CMD_SEQUENCE_SEND = "ws"
	_CMD_SEQUENCE_EXECUTE = "xs"
	_CMD_SEQUENCE_STOP = "st"
	_CMD_EXEC_STATUS_READ = "rs"
	_CMD_EXEC_STATUS_ASYNC = "es"   # not implemented
	_CMD_PULSE_MEASURE_READ = "mp"
	_CMD_PULSE_MEASURE_ASYNC = "pm"
	_CMD_AMPLI_POWER_ENABLE = "ap"
	_CMD_AMPLI_OUTPUT = "od"
	_CMD_ERROR = "ko"
	_CMD_EVENT_ASYNC = "sy"
	_CMD_DEBUG = "dg"


	def __init__ (self, loglevel = LogLevel.EVENT):
		"""
		Constructor. Creates an instance.

		:param loglevel: the default :class:`LogLevel` to set.
		"""
		self._port = serial.Serial(timeout=0.1)
		self._logLevel = loglevel
		self._cmdCounter = 1   # to generate unique command indices
		self._execCounter = 1  # to generate unique execution IDs
		self._config = None    # None if not loaded, a dict otherwise
		self._initDone = False

		# used as a marker to protect some commands, to make sure they are executed
		# no matter what is received (when disconnecting, on error for example)
		self._ignoreAsync = 0
		self._protocolVersion = None # set in connect()


	def logLevel(self):
		"""
		Returns the current log level.

		:return: an integer (usually a :class:`LogLevel`).
		"""
		return self._logLevel

	def setLogLevel(self, level):
		"""
		Changes the current log level to accept or ignore future messages.

		:param int level: the new log level to set, a :class:`LogLevel`.
		"""
		self._logLevel = int(level)

	def _log (self, level, msg):
		"""
		Prints a message, only if its level is important enough.

		:param int level: level of this message, a :class:`LogLevel`
		:param str msg: the content of the message.
		"""
		if level > self._logLevel:
			return
		print (msg)

	def _throw (self, msg):
		"""Raises a :class:`PGAError` exception with the given message, and logs the same message before."""
		self._log(LogLevel.ERROR, msg)
		raise PGAError(msg)


	def loadConfig (self, fname):
		"""
		Loads generator settings from a JSON config file. Throws on error.

		:param str fname: Name of the JSON file to load.
		"""
		with open (fname, "r") as f:
			self._config = json.load (f)


	def connect (self, port = None):
		"""
		Initializes the serial port settings, and tries to open it.

		:param port: the name of the port to use.
			On Linux, usually something like "/dev/ttySx" or "/dev/ttyUSBx".
			On Windows, "COMx" or "\\.\COMx", you can call "CHANGE PORT /QUERY" in a DOS console, to see the list of available ports.
			Can also be simply 0 for the first one.
		:raise: PGAError on error
		"""
		if self._config is None and port is None:
			self._throw ("Connect() requires a serial port if no configuration has been loaded first.")
		if port is None:
			self._port.port = self._config["port"]["device"]
			self._port.baudrate = self._config["port"]["speed"]
		else:
			self._port.port = port
			self._port.baudrate = 460800
		self._port.bytesize = serial.EIGHTBITS
		self._port.parity = serial.PARITY_NONE
		self._port.stopbits = serial.STOPBITS_ONE
		self._port.xonxoff = False
		self._port.rtscts = False
		self._port.timeout = 0.1 # in seconds
		try:
			self._port.open()
		except SerialException as ex:
			self._throw("Can not open serial port: "+str(ex))

		self.resetBoard()
		self._initDone = False
		self._cmdCounter = 1
		self._execCounter = 1
		self._ignoreAsync = 0
		# Set the protocol version from the firmware version (first byte only)
		# since we need it to build and parse the right packet format
		self._protocolVersion = self.readParameter (Param.FIRMWARE_VERSION) >> 24

		if self._config:
			# Send parameters values to the board
			params = self._config["parameters"]
			for p in list(params.keys()):
				try:
					if not p.startswith("PARAM_"): continue
					self.writeParameter(getattr(Param, p[6:]), params[p])
				except PGAError as ex:
					self._throw("Failed to init parameter %s: " % p + str(ex))
			self._initDone = True
		return True


	def autoConnect(self):
		"""
		Try to automatically find a suitable serial port to connect to,
		among the list of available ports on the system.

		:return: True on success, False on error.
		"""
		allPorts = serial.tools.list_ports.comports()
		# :type port: Tuple(str,str,str), examples:
		# - ('COM1', 'Port de communication (COM1)', 'ACPI\\PNP0501\\1')
		# - ('COM8', 'USB Serial Port (COM8)', 'FTDIBUS\\VID_0403+PID_6010+6&22DD3F6C&0&1&1\\0000')
		# - ('COM7', 'USB Serial Port (COM7)', 'FTDIBUS\\VID_0403+PID_6010+6&22DD3F6C&0&1&2\\0000')

		# build a list of "USB" ports only, sorted in numerical order
		usbPorts = []
		#print([p.description for p in allPorts])
		for p in allPorts:
			if p.description.startswith("FTDIBUS") or p.description.startswith("USB"):
				usbPorts.append(p)
		usbPorts.sort(key=lambda x: x[0][3:])
		# try to connect to every port, in that order, until one works
		for p in usbPorts:
			try:
				portName = p.device
				if os.name == "nt":
					portName = "\\\\.\\"+portName
				self.connect(portName)
				return True
			except PGAError:
				pass
		return False


	def disconnect (self):
		"""Closes the port."""
		if self._port.isOpen():
			if self._initDone:
				self._ignoreAsync += 1
				self.stopSequence()
				self.enableAmplifier (False)
				self._ignoreAsync -= 1
			self._port.close()
		self._ignoreAsync = 0


	def readParameter (self, param):
		"""
		Reads the value of a generator parameter.

		:param param: one of :class:`Param`.
		:return: the value of the specified parameter on success.
		:raises: :class:`PGAError` on bad parameter.
		"""
		if param < Param.FIRST or param > Param.LAST:
			self._throw("Parameter index out of range (%d)" % param)

		packet = self._encode (self._CMD_PARAM_GET, struct.pack ("<I", Param.DEFAULTS[param].id))
		self._send (packet)

		answer = self._receive (self._CMD_PARAM_GET)
		value = struct.unpack ("<II", answer)[1]  # ignore cc
		return value


	def writeParameter (self, param, value):
		"""
		Changes the value of a generator parameter.

		:param int param: one of :class:`Param`.
		:param int value: the new value to set (must be an integer).
		:raises: :class:`PGAError` on bad parameter.
		"""
		if param < Param.FIRST or param > Param.LAST:
			self._throw("Parameter index out of range (%d)" % param)
		if not Param.DEFAULTS[param].editable:
			self._throw("This parameter is not editable.")
		value = int(value)  # raise on unexpected type

		packet = self._encode (self._CMD_PARAM_SET, struct.pack ("<II", Param.DEFAULTS[param].id, value))
		self._send (packet)
		self._receive (self._CMD_PARAM_SET)


	def clearSequence (self):
		packet = self._encode (self._CMD_SEQUENCE_SEND, struct.pack ("<I", 0))
		self._send (packet)
		self._receive (self._CMD_SEQUENCE_SEND)


	def sendSequence (self, sequence):
		"""
		Sends a sequence definition (install it into the generator's buffer).

		:param sequence: a list of :class:`Pulse` objects.
		"""
		params = struct.pack ("<I", len(sequence))
		for pulse in sequence:
			params += struct.pack ("<IIII", pulse.amplitude, pulse.frequency, pulse.duration, pulse.delay)
		packet = self._encode (self._CMD_SEQUENCE_SEND, params)
		self._send (packet)
		self._receive (self._CMD_SEQUENCE_SEND)


	def executeSequence (self, execs = 1, delay = 0, flags = 0):
		"""
		Starts one or more executions of the current sequence.

		:param int execs: number of executions (at least 1)
		:param int delay: the delay between executions in microseconds
		:param int flags: OR-combination of :class:`ExecFlags`.
		"""
		if self._protocolVersion < 2:
			v1mask = 0x003F
			if (flags & v1mask) != flags:
				self._throw("Some flags are not allowed in this version of the protocol. Please check ExecFlag documentation.")
			packet = self._encode (self._CMD_SEQUENCE_EXECUTE, struct.pack ("<III", execs, delay, flags))
		else:
			packet = self._encode (self._CMD_SEQUENCE_EXECUTE, struct.pack ("<IIIH", execs, delay, flags, self._nextExecutionCounter()))
		self._send (packet)
		self._receive (self._CMD_SEQUENCE_EXECUTE)


	def stopSequence (self):
		"""
		Stops the execution of the current sequence (if any).
		"""
		packet = self._encode (self._CMD_SEQUENCE_STOP)
		self._send (packet)
		self._ignoreAsync += 1
		self._receive (self._CMD_SEQUENCE_STOP)
		self._ignoreAsync -= 1


	def readExecutionStatus (self):
		"""
		Returns information about the currently executed sequence (or the last one).

		:return: an :class:`ExecutionStatus` object.
		"""
		packet = self._encode (self._CMD_EXEC_STATUS_READ)
		self._send (packet)

		answer = self._receive (self._CMD_EXEC_STATUS_READ)
		return ExecutionStatus (self._protocolVersion, answer)


	def readPulseMeasure (self):
		"""
		Returns information about the last measured pulse.

		:return: a :class:`PulseResult` object.
		"""
		packet = self._encode (self._CMD_PULSE_MEASURE_READ)
		self._send (packet)

		answer = self._receive (self._CMD_PULSE_MEASURE_READ)
		return PulseResult(self._protocolVersion, answer[4:])  # ignore the cmd counter


	def readAsyncPulse (self):
		"""
		Reads the next asynchronous pulse result, sent by the executeSequence command.

		:return: a :class:`PulseResult` object.
		"""
		answer = self._receive (self._CMD_PULSE_MEASURE_ASYNC)
		return PulseResult(self._protocolVersion, answer)


	def enableAmplifier (self, state):
		"""
		Enables or disables the amplifier power supply.

		:param bool state: True to enable, False to disable.
		"""
		if state:
			state = 1
		else:
			state = 0
		packet = self._encode (self._CMD_AMPLI_POWER_ENABLE, struct.pack ("<I", state))
		self._send (packet)
		self._receive (self._CMD_AMPLI_POWER_ENABLE)


	def isAmplifierEnabled (self):
		"""
		Tells if the amplifier power supply is enabled or not.

		:return bool: True if the amplifier is active, False otherwise (executions will fail).
		"""
		packet = self._encode (self._CMD_AMPLI_POWER_ENABLE)
		self._send (packet)
		answer = self._receive (self._CMD_AMPLI_POWER_ENABLE)
		val = struct.unpack ("<II", answer)[1]  # ignore cmd counter
		return val == 1


	def selectOutput (self, output):
		"""
		Selects which generator output to use.

		:param int output: :attr:`Output.INTERNAL` or :attr:`Output.EXTERNAL`.
		"""
		if output != Output.INTERNAL and output != Output.EXTERNAL:
			self._throw ("Invalid output value.")
		packet = self._encode (self._CMD_AMPLI_OUTPUT, struct.pack ("<I", output))
		self._send (packet)
		self._receive (self._CMD_AMPLI_OUTPUT)


	def output (self):
		"""Tells which output is currently used to emit ultrasounds.

		:return: :attr:`Output.INTERNAL` or :attr:`Output.EXTERNAL`."""
		packet = self._encode (self._CMD_AMPLI_OUTPUT)
		self._send (packet)
		answer = self._receive (self._CMD_AMPLI_OUTPUT)
		return struct.unpack ("<II", answer)[1]  # ignore cmd counter


	def convertTemperature(self, adcValue):
		"""
		Converts a raw ADC value (as returned in an ExecutionStatus) into a Celsius value.
		
		:param int adcValue: a raw ADC value
		:return: the converted value in Celsius.
		:raises: if the required polynomial is missing from the config file.
		"""
		try:
			poly = self._config["conversions"]["temperature"]
		except:
			raise PGAError("Missing polynomial from config file, or not loaded.")
		return _computePolyVal(poly, adcValue)


	def convertCurrent(self, adcValue):
		"""
		Converts a raw ADC value (as returned in an ExecutionStatus) into an Ampere value.
		
		:param int adcValue: a raw ADC value
		:return: the converted value in Ampere.
		:raises: if the required polynomial is missing from the config file.
		"""
		try:
			poly = self._config["conversions"]["current"]
		except:
			raise PGAError("Missing polynomial from config file, or not loaded.")
		return _computePolyVal(poly, adcValue)


	def convertVoltage(self, adcValue):
		"""
		Converts a raw ADC value (as returned in an ExecutionStatus) into a Volt value.
		
		:param int adcValue: a raw ADC value
		:return: the converted value in Volt.
		:raises: if the required polynomial is missing from the config file.
		"""
		try:
			poly = self._config["conversions"]["voltage"]
		except:
			raise PGAError("Missing polynomial from config file, or not loaded.")
		return _computePolyVal(poly, adcValue)


	def convertPower(self, adcValue, forward=True, output=Output.EXTERNAL):
		"""
		Converts a raw ADC value (as returned in an ExecutionStatus) into a Volt value.
		
		:param int adcValue: a raw ADC value
		:param bool forward: True (default) for Forward power, False for Reverse power
		:param Output output: Output.EXTERNAL (default) or .INTERNAL
		:return: the converted value in Volt.
		:raises: if the required polynomial is missing from the config file.
		"""
		polyname = "external" if output == Output.EXTERNAL else "external"
		polyname += "Forward" if forward else "Reverse"
		polyname += "Power"
		try:
			poly = self._config["conversions"][polyname]
		except:
			raise PGAError("Missing polynomial from config file, or not loaded.")
		return _computePolyVal(poly, adcValue)

	#------------------------------------------------------------------------
	# end of user commands

	def enableBoard (self, enable, delay = 0.0):
		"""
		Changes the reset-pin state for some time.

		:param bool enable: state to apply
		:param float delay: time to wait in seconds
		"""
		self._port.setRTS (not enable)  # the signal is reversed
		if delay > 0:
			time.sleep (delay)


	def resetBoard (self):
		"""Forces a hardware reset of the board.
		Will block for about 6 seconds until it has properly restarted."""
		resetTime = 5.5
		self._log(LogLevel.VERBOSE, "Generator board init, please wait %g s..." % (resetTime+0.5))
		self.enableBoard (False, 0.5)
		self.enableBoard (True, resetTime)
		self._port.flushInput()


	def _nextCommandCounter (self):
		cc = self._cmdCounter
		self._cmdCounter += 1
		return cc


	def _nextExecutionCounter (self):
		ec = self._execCounter
		self._execCounter += 1
		return ec


	def _encode (self, cmd, data=b""):
		"""
		Prepares a command packet.
		Adds (and increments) the command counter, converts the data content in ASCII hexa,
		then computes and appends the CRC, and finally the end markers.

		:param str cmd: 2-letters string, one of _CMD_*
		:param str data: packed data string
		"""
		hdata = cmd
		for c in struct.pack("<I", self._nextCommandCounter())+data:
			hdata += "%02X" % c
		crc = _computeCRC(hdata)
		hdata += "%02X" % (crc & 0xFF)
		hdata += "%02X" % (crc >> 8)
		hdata += "\x0D\x0A" # "\r\n"
		return hdata


	def _send (self, data):
		self._log(LogLevel.PACKET, "SEND: "+repr(data))
		n = self._port.write (data.encode())
		self._log(LogLevel.VERBOSE, "%d bytes written" % n)


	def _decode (self, data):
		"""
		Decodes the received string and returns a tuple (command, data, crc), where:

		- command is a 2-letters command
		- data is encoded data ready to be unpacked
		- crc is a 16 bits integer CRC

		:raises: on bad CRC or not-convertible character (not ASCII hexa).
		"""
		if len(data) < 8:
			self._throw ("Message too short (%d)" % len(data))

		cmd = data[0:2]

		ddata = ""
		i = 2
		end = len(data) - 2  # ignore 0x0D 0x0A at the end
		if data[-3:] == "\r\r\n":
			end -= 1
		# convert all up to the end (even the CRC)
		while i < end:
			try:
				ddata += chr (int (data[i:i+2], 16))
			except:
				self._throw("Can not convert character %d." % i)
			i += 2
		
		crc = struct.unpack ("<H", ddata[-2:].encode('charmap'))[0]
		computedCRC = _computeCRC(data[:end-4])

		if crc != computedCRC:
			self._throw("Bad CRC (received: %d, computed: %d)" % (crc, computedCRC))
		return (cmd.decode(), ddata.encode('charmap')[:-2], crc)


	def _errorMessage(self, rcv):
		"""
		Builds a standard error message based on received packet.

		:param rcv: tuple (cmd, data, CRC) as returned by _decode().
		"""
		# [4] cmd counter
		# [4] error code
		# [4] error value
		if rcv[0] == self._CMD_ERROR:
			_, errcode, errvalue = struct.unpack ("<III", rcv[1][0:12]) # ignores cmd counter
			msg = "Error: "
		elif rcv[0] == self._CMD_EVENT_ASYNC:
			# [4] event code
			# [4] index
			# [4] value
			errcode, _, errvalue = struct.unpack ("<III", rcv[1]) # ignores index
			msg = "Event: "
		else:
			msg = "??? "
			errcode = 123456
			errvalue = 654321
		msg += "code=%d, value=%d, msg=" % (errcode, errvalue)
		msg += _ErrorMessage(errcode, errvalue)
		return msg


	def _isAsync (self, cmd):
		return cmd in (
			self._CMD_EXEC_STATUS_ASYNC,
			self._CMD_PULSE_MEASURE_ASYNC,
			self._CMD_ERROR,
			self._CMD_EVENT_ASYNC,
			self._CMD_DEBUG)

	def _receive (self, cmd):
		"""
		Receives one message from the serial port, decodes it and performs some checks.
		If the received packet matches cmd, it is always return, no matter its type (even errors).
		It will always raise on error (if cmd is not _CMD_ERROR).
		It will (log and) ignore debug messages (if cmd is not _CMD_DEBUG).
		It will (log and) ignore events and asynchronous answers if ignoreAsync is True.

		:param cmd: the expected command to receive
		:return: the data received (without command and CRC)
		:raises: :class:`PGAError` on errors.
		"""
		while True:
			incoming = self._readline()
			self._log(LogLevel.PACKET, "RECV: "+repr(incoming))
			
			rcv = self._decode (incoming)  # contains (cmd, data, CRC)
			self._log(LogLevel.PACKET, " CMD: %s CRC: 0x%04X DATA: %d bytes" % (rcv[0], rcv[2], len(rcv[1])))
			if rcv[0] == self._CMD_ERROR:
				msg = self._errorMessage(rcv)
				if rcv[0] == cmd:
					self._log(LogLevel.ERROR, msg)
					return rcv[1]
				self._throw (msg)
			elif rcv[0] == self._CMD_EVENT_ASYNC:
				msg = self._errorMessage(rcv)
				if rcv[0] == cmd:
					self._log(LogLevel.EVENT, msg)
					return rcv[1]
				self._throw (msg)
			elif rcv[0] == self._CMD_DEBUG:
				# Debug messages from the generator firmware
				# [8] timestamp
				# [4] mask
				# [2] n = message length (incl. \0)
				# [n] debug message
				msg = "Generator: tstamp=%d, mask=%d, len=%d, msg=" % struct.unpack ("<QIH", rcv[1][:14]) + rcv[1][14:].decode('charmap')
				self._log(LogLevel.INFO, msg)
				if rcv[0] == cmd:
					return rcv[1]
				continue
			elif self._isAsync(rcv[0]) and self._ignoreAsync:
				self._log(LogLevel.VERBOSE, "Ignoring '%s' async packet." % (rcv[0]))
				continue
			if rcv[0] != cmd:
				self._throw ("Unexpected command received (%s, expected: %s)" % (rcv[0], cmd))
			return rcv[1]


	def _readline (self):
		"""
		Was added to debug some problem, but now kept since the serial.readline()
		replaces \n by \r\n -> so we get \r\r\n at the end.
		"""
		data = b''
		while True:
			c = self._port.read(1)
			data += c
			if c == b'\n':
				return data

#--------------------------------------------------------------------
# CRC

_CCITT16_FALSE_TABLE = (
	0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7,
	0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF,
	0x1231, 0x0210, 0x3273, 0x2252, 0x52B5, 0x4294, 0x72F7, 0x62D6,
	0x9339, 0x8318, 0xB37B, 0xA35A, 0xD3BD, 0xC39C, 0xF3FF, 0xE3DE,
	0x2462, 0x3443, 0x0420, 0x1401, 0x64E6, 0x74C7, 0x44A4, 0x5485,
	0xA56A, 0xB54B, 0x8528, 0x9509, 0xE5EE, 0xF5CF, 0xC5AC, 0xD58D,
	0x3653, 0x2672, 0x1611, 0x0630, 0x76D7, 0x66F6, 0x5695, 0x46B4,
	0xB75B, 0xA77A, 0x9719, 0x8738, 0xF7DF, 0xE7FE, 0xD79D, 0xC7BC,
	0x48C4, 0x58E5, 0x6886, 0x78A7, 0x0840, 0x1861, 0x2802, 0x3823,
	0xC9CC, 0xD9ED, 0xE98E, 0xF9AF, 0x8948, 0x9969, 0xA90A, 0xB92B,
	0x5AF5, 0x4AD4, 0x7AB7, 0x6A96, 0x1A71, 0x0A50, 0x3A33, 0x2A12,
	0xDBFD, 0xCBDC, 0xFBBF, 0xEB9E, 0x9B79, 0x8B58, 0xBB3B, 0xAB1A,
	0x6CA6, 0x7C87, 0x4CE4, 0x5CC5, 0x2C22, 0x3C03, 0x0C60, 0x1C41,
	0xEDAE, 0xFD8F, 0xCDEC, 0xDDCD, 0xAD2A, 0xBD0B, 0x8D68, 0x9D49,
	0x7E97, 0x6EB6, 0x5ED5, 0x4EF4, 0x3E13, 0x2E32, 0x1E51, 0x0E70,
	0xFF9F, 0xEFBE, 0xDFDD, 0xCFFC, 0xBF1B, 0xAF3A, 0x9F59, 0x8F78,
	0x9188, 0x81A9, 0xB1CA, 0xA1EB, 0xD10C, 0xC12D, 0xF14E, 0xE16F,
	0x1080, 0x00A1, 0x30C2, 0x20E3, 0x5004, 0x4025, 0x7046, 0x6067,
	0x83B9, 0x9398, 0xA3FB, 0xB3DA, 0xC33D, 0xD31C, 0xE37F, 0xF35E,
	0x02B1, 0x1290, 0x22F3, 0x32D2, 0x4235, 0x5214, 0x6277, 0x7256,
	0xB5EA, 0xA5CB, 0x95A8, 0x8589, 0xF56E, 0xE54F, 0xD52C, 0xC50D,
	0x34E2, 0x24C3, 0x14A0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
	0xA7DB, 0xB7FA, 0x8799, 0x97B8, 0xE75F, 0xF77E, 0xC71D, 0xD73C,
	0x26D3, 0x36F2, 0x0691, 0x16B0, 0x6657, 0x7676, 0x4615, 0x5634,
	0xD94C, 0xC96D, 0xF90E, 0xE92F, 0x99C8, 0x89E9, 0xB98A, 0xA9AB,
	0x5844, 0x4865, 0x7806, 0x6827, 0x18C0, 0x08E1, 0x3882, 0x28A3,
	0xCB7D, 0xDB5C, 0xEB3F, 0xFB1E, 0x8BF9, 0x9BD8, 0xABBB, 0xBB9A,
	0x4A75, 0x5A54, 0x6A37, 0x7A16, 0x0AF1, 0x1AD0, 0x2AB3, 0x3A92,
	0xFD2E, 0xED0F, 0xDD6C, 0xCD4D, 0xBDAA, 0xAD8B, 0x9DE8, 0x8DC9,
	0x7C26, 0x6C07, 0x5C64, 0x4C45, 0x3CA2, 0x2C83, 0x1CE0, 0x0CC1,
	0xEF1F, 0xFF3E, 0xCF5D, 0xDF7C, 0xAF9B, 0xBFBA, 0x8FD9, 0x9FF8,
	0x6E17, 0x7E36, 0x4E55, 0x5E74, 0x2E93, 0x3EB2, 0x0ED1, 0x1EF0
)

def _computeCRC (data):
	"""
	Computes a 16 bits CCITT CRC on the given data.
	(Little Endian implementation based on a table, Poly=0x1021, Check=0x29B1).
	print "CRC test:", pga._computeCRC("123456789"), 0x29B1
	"""
	crc = 0xFFFF

	for char in data:
		if type(char) is str:
			c = ord(char)
		else:
			c = char
		tmp = ((crc >> 8) ^ c) & 0xFF
		crc = (crc << 8) ^ _CCITT16_FALSE_TABLE[tmp]
	return crc & 0xFFFF
#
