import can
import cantools
import sqlite3

#function to receive message with requested arbitration_id
def recvMsg(bus, arbitration_id):
	"""
	Function used to catch and return first frame with given arbitration_id
	
	:param bus: Bus object from python-can module on which user wants to recieve frame
	:param arbitration_id: arbitration id of frame to be received, other frames will be ignored
	:return: returns received Message, type can.Message
	"""
	while (True):
		recvd_msg = bus.recv()
		if (recvd_msg.arbitration_id == arbitration_id):
			return recvd_msg
	
#function to set single signal in CAN Message
def setSignal(databaseObject, lastMsg, signal, value):
	"""
	Function used to set single signal in CAN Message
	
	:param databaseObject: loaded dbc database object containing message
	:param lastMsg: CAN Message containing signal to be changed, preferably last sent Message to not lose other signals in Message
	:param signal: name of the signal to set
	:param value: value of signal to set
	:return: returns CAN Message with signal set to given value, type can.Message
	"""
	
	decoded_dictionary = databaseObject.decode_message(lastMsg.arbitration_id, lastMsg.data)
	if signal in decoded_dictionary:
		decoded_dictionary.update({signal : value})	
		updatedData = databaseObject.encode_message(lastMsg.arbitration_id, decoded_dictionary)
		return can.Message(arbitration_id=lastMsg.arbitration_id, is_extended_id=False, data=updatedData)
	else:
		print("Message " + databaseObject.get_message_by_frame_id(lastMsg.arbitration_id).name + "(" + (str(hex(lastMsg.arbitration_id))) +") does not contain signal " + signal)
		return
	
def getSignal(databaseObject, lastMsg, signal):
	"""
	Function used to get single signal value from CAN Message
	
	:param databaseObject: loaded dbc database object containing message
	:param lastMsg: CAN Message containing signal to read
	:param signal: name of the signal to get
	:return: returns signal value
	"""
	decoded_dictionary = databaseObject.decode_message(lastMsg.arbitration_id, lastMsg.data)
	if signal in decoded_dictionary:
		return decoded_dictionary.get(signal)
	else:
		print("Message " + databaseObject.get_message_by_frame_id(lastMsg.arbitration_id).name + "(" + (str(hex(lastMsg.arbitration_id))) +") does not contain signal " + signal)
		return
	
