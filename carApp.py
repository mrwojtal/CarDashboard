import can
import cantools
import obd
import os
import time
import RPi.GPIO as GPIO
import sqlite3
import concurrent.futures

from MiniR50 import *
		
GPIO.setwarnings(False)	
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)
GPIO.setup(29, GPIO.OUT)
GPIO.setup(31, GPIO.OUT)		
		
print("Entering idle wait loop, \n wait for user to run script.")
			
while(True):
	if GPIO.input(33) == 1:
		break
	else:
		time.sleep(0.2)
			
class myException(Exception):
	pass
			
pool = concurrent.futures.ThreadPoolExecutor(max_workers=10)
			
#variables
LCD_Value = 0
Vehicle_RPM = 0
Vehicle_Speed = 0
Vehicle_Trip = 0
Vehicle_Range = 0
MAF = 0 #air flow ratio
AF = 14.5 # air to fuel ratio
Engine_Load = 0
Diesel_Fuel_Density = 850 
Fuel_Capacity = 41
Fuel_Consumption = 0
i = 0 

			
LM327 = obd.OBD(fast=False) #used LM327 does not response to fast commands sent with \r

if LM327.is_connected():
	print("Connected to LM327 device.\n" + "Connection status: " + LM327.status() + "\n" + "Protocol used: " + LM327.protocol_name() + "\n")
			
with can.Bus(interface='socketcan', channel='can0', bitrate=500000, receive_own_messages=True) as bus:
	
	try:
		#import created dbc file for easy handling of can messages
		db = cantools.database.load_file('./MiniR50/CAN_Database.dbc')
	except cantools.database.UnsupportedDatabaseFormatError:
		print("Application failed parsing given database, terminating...")
		exit(0)
		
	#creating message objects to store messages description from database
	Cluster = db.get_message_by_name('Cluster')
	LCD = db.get_message_by_name('LCD')
	Tachometer = db.get_message_by_name('Tachometer')
		
	#encoding default data 
	dataCluster = Cluster.encode({'Brightness': 125, 'Cluster_Mode': const._ACTIVE, 'Control_Alert': const._OFF, 'Control_Cruise': const._OFF, 'Control_DDE': const._OFF, 'Control_Seatbelts': const._OFF, 'Tacho_Illumination_1': const._OFF, 'Tacho_Illumination_2': const._OFF, 'Tacho_Illumination_3': const._OFF, 'Tacho_Illumination_4': const._OFF})
	dataLCD = LCD.encode({'LCD_Mode': const._TEMPERATURE, 'LCD_Unit': const._METRIC_EMEA, 'LCD_Value': 250})
	dataTachometer = Tachometer.encode({'RPM': 0})
		
	#construct can messages from encoded data and arbitration id from dbc file
	lastClusterMsg = msgCluster = can.Message(arbitration_id=Cluster.frame_id, is_extended_id=False, data=dataCluster)
	lastLCDMsg = msgLCD = can.Message(arbitration_id=LCD.frame_id, is_extended_id=False, data=dataLCD)
	lastTachoMsg = msgTachometer = can.Message(arbitration_id=Tachometer.frame_id, is_extended_id=False, data=dataTachometer)
	
	print("Database import succeded, entering main loop.")
	
	# main loop
	while (True):
		try:
			#MAIN LOOP STOP
			try:
				if GPIO.input(33) == 0:
					LM327.close()
					raise myException
			except myException as e:
				while(True):
					if GPIO.input(33) == 1:
						LM327 = obd.OBD(fast=False)	
						break
					else:
						time.sleep(0.2)
					
			#obd readings iterator
			i += 1
			
			#Send and save Cluster Message periodically on CAN bus
			bus.send(msgCluster)
			lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)

			#Send and save Tachometer Message periodically on CAN bus
			cmd = obd.commands.RPM
			response = LM327.query(cmd)
			if not response.is_null():
				print(response)
				Vehicle_RPM=response.value.magnitude

			msgTachometer = canutils.setSignal(db, lastTachoMsg, 'RPM', Vehicle_RPM)
			bus.send(msgTachometer)
			lastTachoMsg = canutils.recvMsg(bus, Tachometer.frame_id)

			#if structures to set and send LCD_Frame
			if (GPIO.input(3) == 1):# TRIP on LCD, DISTANCE_W_MIL from OBD2
				cmd = obd.commands.DISTANCE_W_MIL
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					Vehicle_Trip = response.value.magnitude
					
				LCD_Value = Vehicle_Trip * 10
				msgLCD = canutils.setSignal(db, lastLCDMsg, 'LCD_Mode', const._TRIP)
				bus.send(msgLCD)
				lastLCDMsg = canutils.recvMsg(bus, LCD.frame_id)
				msgLCD = canutils.setSignal(db, lastLCDMsg, 'LCD_Value', LCD_Value)
				bus.send(msgLCD)
				lastLCDMsg = canutils.recvMsg(bus, LCD.frame_id)
			elif (GPIO.input(5) == 1):# Vehicle Speed
				cmd = obd.commands.SPEED
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					Vehicle_Speed = response.value.magnitude
					
				LCD_Value = Vehicle_Speed * 10
				msgLCD = canutils.setSignal(db, lastLCDMsg, 'LCD_Mode', const._SPEED)
				bus.send(msgLCD)
				lastLCDMsg = canutils.recvMsg(bus, LCD.frame_id)
				msgLCD = canutils.setSignal(db, lastLCDMsg, 'LCD_Value', LCD_Value)
				bus.send(msgLCD)
				lastLCDMsg = canutils.recvMsg(bus, LCD.frame_id)
			elif (GPIO.input(7) == 1):# Intake Air Temperature
				cmd = obd.commands.INTAKE_TEMP
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					Intake_Air_Temp = response.value.magnitude
					
				LCD_Value=Intake_Air_Temp * 10
				msgLCD = canutils.setSignal(db, lastLCDMsg, 'LCD_Mode', const._TEMPERATURE)
				bus.send(msgLCD)
				lastLCDMsg = canutils.recvMsg(bus, LCD.frame_id)
				msgLCD = canutils.setSignal(db, lastLCDMsg, 'LCD_Value', LCD_Value)
				bus.send(msgLCD)
				lastLCDMsg = canutils.recvMsg(bus, LCD.frame_id)
			elif (GPIO.input(29) == 1): #range based on fuel capacity
				
				cmd = obd.commands.SPEED
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					Vehicle_Speed = response.value.magnitude
				
				cmd = obd.commands.MAF
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					MAF = response.value.magnitude
					
				cmd = obd.commands.ENGINE_LOAD
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					Engine_Load = response.value.magnitude
					
				if Engine_Load == 0:
					Fuel_Consumption = 0
					
				if Vehicle_Speed == 0 or Vehicle_Speed < 25:
					Fuel_Consumption = 0
				else:
					FF = (MAF*3600)/(14.5*850)
					Fuel_Consumption = (FF/Vehicle_Speed) * 100 * (Engine_Load/100)
					print(Fuel_Consumption)
					if Fuel_Consumption > 9990:
						Fuel_Consumption=9990
				
				if Fuel_Consumption == 0:
					Vehicle_Range = 9990
				else:	
					Vehicle_Range = (Fuel_Capacity/Fuel_Consumption) * 1000
				
				if Vehicle_Range > 9990:
					Vehicle_Range = 9990
					
				LCD_Value = Vehicle_Range
				msgLCD = canutils.setSignal(db, lastLCDMsg, 'LCD_Value', LCD_Value)
				bus.send(msgLCD)
				lastLCDMsg = canutils.recvMsg(bus, LCD.frame_id)
					
				LCD_Value = Vehicle_Range
				msgLCD = canutils.setSignal(db, lastLCDMsg, 'LCD_Mode', const._RANGE)
				bus.send(msgLCD)
				lastLCDMsg = canutils.recvMsg(bus, LCD.frame_id)
			elif (GPIO.input(31) == 1): #Calculated fuel consumption
				
				cmd = obd.commands.SPEED
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					Vehicle_Speed = response.value.magnitude
				
				cmd = obd.commands.MAF
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					MAF = response.value.magnitude
					
				cmd = obd.commands.ENGINE_LOAD
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					Engine_Load = response.value.magnitude
					
				if Engine_Load == 0 or Vehicle_Speed < 25:
					Fuel_Consumption = 0
				else:
					FF = (MAF*3600)/(14.5*850)
					Fuel_Consumption = (FF/Vehicle_Speed) * 100 * (Engine_Load/100)
					print(Fuel_Consumption)
					if Fuel_Consumption > 9990:
						Fuel_Consumption=9990
				
				LCD_Value = round(Fuel_Consumption, 2) * 10 #*10 for proper displaying on LCD
				msgLCD = canutils.setSignal(db, lastLCDMsg, 'LCD_Mode', const._CONSUMPTION)
				bus.send(msgLCD)
				lastLCDMsg = canutils.recvMsg(bus, LCD.frame_id)
					
				msgLCD = canutils.setSignal(db, lastLCDMsg, 'LCD_Value', LCD_Value)
				bus.send(msgLCD)
				lastLCDMsg = canutils.recvMsg(bus, LCD.frame_id)
			#if structures to set and send Cluster_Frame
			if GPIO.input(5) == 1:
				msgCluster = canutils.setSignal(db, lastClusterMsg, 'Control_Cruise', const._ON)
				bus.send(msgCluster)
				lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)
			else:
				msgCluster = canutils.setSignal(db, lastClusterMsg, 'Control_Cruise', const._OFF)
				bus.send(msgCluster)
				lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)
			if (Vehicle_Speed >= 50):
				msgCluster = canutils.setSignal(db, lastClusterMsg, 'Control_Alert', const._ON)
				bus.send(msgCluster)
				lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)
			else:
				msgCluster = canutils.setSignal(db, lastClusterMsg, 'Control_Alert', const._OFF)
				bus.send(msgCluster)
				lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)
			if (Vehicle_RPM >= 2000):
				msgCluster = canutils.setSignal(db, lastClusterMsg, 'Control_Seatbelts', const._ON)
				bus.send(msgCluster)
				lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)
			else:
				msgCluster = canutils.setSignal(db, lastClusterMsg, 'Control_Seatbelts', const._OFF)
				bus.send(msgCluster)
				lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)
			if (GPIO.input(31) == 1):
				msgCluster = canutils.setSignal(db, lastClusterMsg, 'Control_DDE', const._ON)
				bus.send(msgCluster)
				lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)
			else:
				msgCluster = canutils.setSignal(db, lastClusterMsg, 'Control_DDE', const._OFF)
				bus.send(msgCluster)
				lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)
			if (Vehicle_RPM >= 5000):
				msgCluster = canutils.setSignal(db, lastClusterMsg, 'Tacho_Illumination_1', const._ON)
				bus.send(msgCluster)
				lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)
			else:
				msgCluster = canutils.setSignal(db, lastClusterMsg, 'Tacho_Illumination_1', const._OFF)
				bus.send(msgCluster)
				lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)
			if (Vehicle_RPM >= 5250):
				msgCluster = canutils.setSignal(db, lastClusterMsg, 'Tacho_Illumination_2', const._ON)
				bus.send(msgCluster)
				lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)
			else:
				msgCluster = canutils.setSignal(db, lastClusterMsg, 'Tacho_Illumination_2', const._OFF)
				bus.send(msgCluster)
				lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)
			if (Vehicle_RPM >= 5500):
				msgCluster = canutils.setSignal(db, lastClusterMsg, 'Tacho_Illumination_3', const._ON)
				bus.send(msgCluster)
				lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)
			else:
				msgCluster = canutils.setSignal(db, lastClusterMsg, 'Tacho_Illumination_3', const._OFF)
				bus.send(msgCluster)
				lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)
			if (Vehicle_RPM >= 6000):
				msgCluster = canutils.setSignal(db, lastClusterMsg, 'Tacho_Illumination_4', const._ON)
				bus.send(msgCluster)
				lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)
			else:
				msgCluster = canutils.setSignal(db, lastClusterMsg, 'Tacho_Illumination_4', const._OFF)
				bus.send(msgCluster)
				lastClusterMsg = canutils.recvMsg(bus, Cluster.frame_id)
			
			#execute queries to database (insert data from CAN bus to database)
			query = """
					INSERT INTO Tachometer_Frame (RPM) 
					VALUES (%d);
					"""%(canutils.getSignal(db, lastTachoMsg, 'RPM'))
			pool.submit(sqltools.database_query(query))
			
			#execute queries to database (insert data from CAN bus to database)
			query = """
					INSERT INTO LCD_Frame (LCD_Mode, LCD_Unit, LCD_Value) 
					VALUES (\'%s\', \'%s\', %d);
					"""%(canutils.getSignal(db, lastLCDMsg, 'LCD_Mode'), 
						 canutils.getSignal(db, lastLCDMsg, 'LCD_Unit'), 
						 canutils.getSignal(db, lastLCDMsg, 'LCD_Value')/10
						)
			pool.submit(sqltools.datasbase_query(query))
			
			#execute queries to database (insert data from CAN bus to database)
			query = """
					INSERT INTO Cluster_Frame (Brightness, Cluster_Mode, Control_Alert, Control_Cruise, Control_DDE, Control_Seatbelts, Tacho_Illumination_1, Tacho_Illumination_2, Tacho_Illumination_3, Tacho_Illumination_4) 
					VALUES (%d, \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\');
					"""%(canutils.getSignal(db, lastClusterMsg, 'Brightness'), 
						 canutils.getSignal(db, lastClusterMsg, 'Cluster_Mode'), 
						 canutils.getSignal(db, lastClusterMsg, 'Control_Alert'), 
						 canutils.getSignal(db, lastClusterMsg, 'Control_Cruise'), 
						 canutils.getSignal(db, lastClusterMsg, 'Control_DDE'), 
						 canutils.getSignal(db, lastClusterMsg, 'Control_Seatbelts'), 
						 canutils.getSignal(db, lastClusterMsg, 'Tacho_Illumination_1'), 
						 canutils.getSignal(db, lastClusterMsg, 'Tacho_Illumination_2'), 
						 canutils.getSignal(db, lastClusterMsg, 'Tacho_Illumination_3'), 
						 canutils.getSignal(db, lastClusterMsg, 'Tacho_Illumination_4')
						)
			pool.submit(sqltools.database_query(query))
			
			if i == 5:
				cmd = obd.commands.OBD_COMPLIANCE
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					Obd_Compliance = response.value
					query = """
							INSERT INTO OBD_Readings (OBD_Parameter_Name, OBD_Parameter_Value) 
							VALUES (\'%s\', \'%s\');
							"""%("OBD_Compliance", Obd_Compliance)
					pool.submit(sqltools.database_query(query))
					
			if i == 10:
				cmd = obd.commands.ELM_VOLTAGE
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					ELM_Voltage = response.value.magnitude
					query = """
							INSERT INTO OBD_Readings (OBD_Parameter_Name, OBD_Parameter_Value) 
							VALUES (\'%s\', \'%s\');
							"""%("ELM_Voltage", ELM_Voltage)
					pool.submit(sqltools.database_query(query))
					
			if i == 15:
				cmd = obd.commands.DISTANCE_W_MIL
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					Distance_With_MIL = response.value.magnitude
					query = """
							INSERT INTO OBD_Readings (OBD_Parameter_Name, OBD_Parameter_Value) 
							VALUES (\'%s\', \'%s\');
							"""%("Distance_With_MIL", Distance_With_MIL)
					pool.submit(sqltools.database_query(query))
					
			if i == 20:
				cmd = obd.commands.COOLANT_TEMP
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					Coolant_Temp = response.value.magnitude
					query = """
							INSERT INTO OBD_Readings (OBD_Parameter_Name, OBD_Parameter_Value) 
							VALUES (\'%s\', \'%s\');
							"""%("Coolant_Temperature", Coolant_Temp)
					pool.submit(sqltools.database_query(query))
					
			if i == 25:
				cmd = obd.commands.INTAKE_TEMP
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					Intake_Air_Temp = response.value.magnitude
					query = """
							INSERT INTO OBD_Readings (OBD_Parameter_Name, OBD_Parameter_Value) 
							VALUES (\'%s\', \'%s\');
							"""%("Intake_Air_Temperature", Intake_Air_Temp)
					pool.submit(sqltools.database_query(query))
			
			if i == 30:
				cmd = obd.commands.MAF
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					MAF = response.value.magnitude
					query = """
							INSERT INTO OBD_Readings (OBD_Parameter_Name, OBD_Parameter_Value) 
							VALUES (\'%s\', \'%s\');
							"""%("MAF", MAF)
					pool.submit(sqltools.database_query(query))
					
			if i == 35:
				cmd = obd.commands.ENGINE_LOAD
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					Engine_Load = round(response.value.magnitude, 2)
					query = """
							INSERT INTO OBD_Readings (OBD_Parameter_Name, OBD_Parameter_Value) 
							VALUES (\'%s\', \'%s\');
							"""%("Engine_Load", Engine_Load)
					pool.submit(sqltools.database_query(query))
			
			if i == 40:
				cmd = obd.commands.INTAKE_PRESSURE
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					Intake_Pressure = response.value.magnitude
					query = """
							INSERT INTO OBD_Readings (OBD_Parameter_Name, OBD_Parameter_Value) 
							VALUES (\'%s\', \'%s\');
							"""%("Intake_Pressure", Intake_Pressure)
					pool.submit(sqltools.database_query(query))
					
			if i == 45:
				cmd = obd.commands.FUEL_RAIL_PRESSURE_DIRECT
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					Fuel_Rail_Pressure = response.value.magnitude
					query = """
							INSERT INTO OBD_Readings (OBD_Parameter_Name, OBD_Parameter_Value) 
							VALUES (\'%s\', \'%s\');
							"""%("Fuel_Rail_Pressure", Fuel_Rail_Pressure)
					pool.submit(sqltools.database_query(query))
					
			if i == 50:
				cmd = obd.commands.SPEED
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					Vehicle_Speed = response.value.magnitude
					query = """
							INSERT INTO OBD_Readings (OBD_Parameter_Name, OBD_Parameter_Value)
							VALUES (\'%s\', \'%s\');
							"""%("Vehicle_Speed", Vehicle_Speed)
					pool.submit(sqltools.database_query(query))
			
			if i == 55:
				i = 0
				cmd = obd.commands.RPM
				response = LM327.query(cmd)
				if not response.is_null():
					print(response)
					Vehicle_RPM = response.value.magnitude
					query = """
							INSERT INTO OBD_Readings (OBD_Parameter_Name, OBD_Parameter_Value)
							VALUES (\'%s\', \'%s\');
							"""%("Vehicle_RPM", Vehicle_RPM)
					pool.submit(sqltools.database_query(query))
			
		except KeyboardInterrupt:
			LM327.close()
			print("Terminating")
			exit(0)

	
