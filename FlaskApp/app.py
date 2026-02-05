import RPi.GPIO as GPIO
import time
import sqlite3
import sys
from flask import Flask, render_template, url_for, request, jsonify, json

from MiniR50 import sqltools

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')
	
@app.route('/control')
def control():
	return render_template('control.html')
		
@app.route('/trip')
def trip():
	if request.is_json:
		query = """
				SELECT LCD_Value 
				FROM LCD_Frame 
				WHERE LCD_Mode = 'Trip' 
				ORDER BY Frame_Timestamp DESC LIMIT 1;
				"""
		tripValue = sqltools.database_query(query, 'SELECT')
		return jsonify(tripValue=tripValue)
		
	GPIO.output(3, GPIO.HIGH)
	GPIO.output(5, GPIO.LOW)
	GPIO.output(7, GPIO.LOW)
	GPIO.output(29, GPIO.LOW)
	GPIO.output(31, GPIO.LOW)
	time.sleep(0.2) #delay for demo.py script to enter data to database
	
	query = """
			SELECT LCD_Value 
			FROM LCD_Frame 
			WHERE LCD_Mode = 'Trip' 
			ORDER BY Frame_Timestamp DESC LIMIT 1;
			"""
	tripValue = sqltools.database_query(query, 'SELECT')	
	return render_template('control.html', tripValue=tripValue)
	
@app.route('/speed')
def speed():
	if request.is_json:
		query = """
				SELECT LCD_Value 
				FROM LCD_Frame 
				WHERE LCD_Mode = 'Speed' 
				ORDER BY Frame_Timestamp DESC LIMIT 1;
				"""
		speedValue = sqltools.database_query(query, 'SELECT')
		return jsonify(speedValue=speedValue)
		
	GPIO.output(3, GPIO.LOW)
	GPIO.output(5, GPIO.HIGH)
	GPIO.output(7, GPIO.LOW)
	GPIO.output(29, GPIO.LOW)
	GPIO.output(31, GPIO.LOW)
	time.sleep(0.2) #delay for demo.py script to enter data to database
	
	query = """
			SELECT LCD_Value 
			FROM LCD_Frame 
			WHERE LCD_Mode = 'Speed' 
			ORDER BY Frame_Timestamp DESC LIMIT 1;
			"""
	speedValue = sqltools.database_query(query, 'SELECT')
	return render_template('control.html', speedValue=speedValue)
	
@app.route('/temperature')
def temperature():
	if request.is_json:
		query = """
				SELECT LCD_Value 
				FROM LCD_Frame 
				WHERE LCD_Mode = 'Temperature' 
				ORDER BY Frame_Timestamp DESC LIMIT 1;
				"""
		tempValue = sqltools.database_query(query, 'SELECT')
		return jsonify(tempValue=tempValue)
	
	GPIO.output(3, GPIO.LOW)
	GPIO.output(5, GPIO.LOW)
	GPIO.output(7, GPIO.HIGH)
	GPIO.output(29, GPIO.LOW)
	GPIO.output(31, GPIO.LOW)
	time.sleep(0.2) #delay for demo.py script to enter data to database
	
	query = """
			SELECT LCD_Value 
			FROM LCD_Frame 
			WHERE LCD_Mode = 'Temperature' 
			ORDER BY Frame_Timestamp DESC LIMIT 1;
			"""
	tempValue = sqltools.database_query(query, 'SELECT')
	return render_template('control.html', tempValue=tempValue)
	
@app.route('/range')
def range():
	if request.is_json:
		query = """
				SELECT LCD_Value 
				FROM LCD_Frame 
				WHERE LCD_Mode = 'Range' 
				ORDER BY Frame_Timestamp DESC LIMIT 1;
				"""
		rangeValue = sqltools.database_query(query, 'SELECT')
		return jsonify(rangeValue=rangeValue)
	
	GPIO.output(3, GPIO.LOW)
	GPIO.output(5, GPIO.LOW)
	GPIO.output(7, GPIO.LOW)
	GPIO.output(29, GPIO.HIGH)
	GPIO.output(31, GPIO.LOW)
	time.sleep(0.2) #delay for demo.py script to enter data to database
	
	query = """
			SELECT LCD_Value 
			FROM LCD_Frame 
			WHERE LCD_Mode = 'Range' 
			ORDER BY Frame_Timestamp DESC LIMIT 1;
			"""
	rangeValue = sqltools.database_query(query, 'SELECT')
	return render_template('control.html', rangeValue=rangeValue)
	
@app.route('/consumption')
def consumption():
	if request.is_json:
		query = """
				SELECT LCD_Value 
				FROM LCD_Frame 
				WHERE LCD_Mode = 'Consumption' 
				ORDER BY Frame_Timestamp DESC LIMIT 1;
				"""
		consValue = sqltools.database_query(query, 'SELECT')
		return jsonify(consValue=consValue)
		
	GPIO.output(3, GPIO.LOW)
	GPIO.output(5, GPIO.LOW)
	GPIO.output(7, GPIO.LOW)
	GPIO.output(29, GPIO.LOW)
	GPIO.output(31, GPIO.HIGH)
	time.sleep(0.2) #delay for demo.py script to enter data to database
	
	query = """
			SELECT LCD_Value 
			FROM LCD_Frame 
			WHERE LCD_Mode = 'Consumption' 
			ORDER BY Frame_Timestamp DESC LIMIT 1;
			"""
	consValue = sqltools.database_query(query, 'SELECT')
	return render_template('control.html', consValue=consValue)
	
@app.route('/rpm')
def rpm():
	if request.is_json:
		query = """
				SELECT RPM 
				FROM Tachometer_Frame 
				ORDER BY Frame_Timestamp DESC LIMIT 1;
				"""
		rpmValue = sqltools.database_query(query, 'SELECT')
		return jsonify(rpmValue=rpmValue)
	
@app.route('/obd_parameters')
def obd_parameters():
	if request.is_json:
		query = """
				SELECT OBD_Parameter_Value 
				FROM OBD_Readings 
				WHERE OBD_Parameter_Name = 'OBD_Compliance' 
				ORDER BY OBD_Reading_Timestamp DESC LIMIT 1;
				"""
		obdComplianceValue = sqltools.database_query(query, 'SELECT')
		
		query = """
				SELECT OBD_Parameter_Value 
				FROM OBD_Readings 
				WHERE OBD_Parameter_Name = 'ELM_Voltage' 
				ORDER BY OBD_Reading_Timestamp DESC LIMIT 1;
				"""
		elmVoltageValue = sqltools.database_query(query, 'SELECT')
		
		query = """
				SELECT OBD_Parameter_Value 
				FROM OBD_Readings 
				WHERE OBD_Parameter_Name = 'Distance_With_MIL' 
				ORDER BY OBD_Reading_Timestamp DESC LIMIT 1;
				"""
		distanceWithMILValue = sqltools.database_query(query, 'SELECT')
		
		query = """
				SELECT OBD_Parameter_Value 
				FROM OBD_Readings 
				WHERE OBD_Parameter_Name = 'Coolant_Temperature' 
				ORDER BY OBD_Reading_Timestamp DESC LIMIT 1;
				"""
		coolantTemperatureValue = sqltools.database_query(query, 'SELECT')
		
		query = """
				SELECT OBD_Parameter_Value 
				FROM OBD_Readings 
				WHERE OBD_Parameter_Name = 'Intake_Air_Temperature' 
				ORDER BY OBD_Reading_Timestamp DESC LIMIT 1;
				"""
		intakeAirTemperatureValue = sqltools.database_query(query, 'SELECT')
		
		query = """
				SELECT OBD_Parameter_Value 
				FROM OBD_Readings 
				WHERE OBD_Parameter_Name = 'MAF' 
				ORDER BY OBD_Reading_Timestamp DESC LIMIT 1;
				"""
		mafValue = sqltools.database_query(query, 'SELECT')
		
		query = """
				SELECT OBD_Parameter_Value 
				FROM OBD_Readings 
				WHERE OBD_Parameter_Name = 'Engine_Load' 
				ORDER BY OBD_Reading_Timestamp DESC LIMIT 1;
				"""
		engineLoadValue = sqltools.database_query(query, 'SELECT')
		
		query = """
				SELECT OBD_Parameter_Value 
				FROM OBD_Readings 
				WHERE OBD_Parameter_Name = 'Vehicle_Speed' 
				ORDER BY OBD_Reading_Timestamp DESC LIMIT 1;
				"""
		vehicleSpeedValue = sqltools.database_query(query, 'SELECT')
		
		query = """
				SELECT OBD_Parameter_Value 
				FROM OBD_Readings 
				WHERE OBD_Parameter_Name = 'Vehicle_RPM' 
				ORDER BY OBD_Reading_Timestamp DESC LIMIT 1;
				"""
		vehicleRPMValue = sqltools.database_query(query, 'SELECT')
		
		query = """
				SELECT OBD_Parameter_Value 
				FROM OBD_Readings 
				WHERE OBD_Parameter_Name = 'Intake_Pressure' 
				ORDER BY OBD_Reading_Timestamp DESC LIMIT 1;
				"""
		intakePressureValue = sqltools.database_query(query, 'SELECT')
		
		query = """
				SELECT OBD_Parameter_Value 
				FROM OBD_Readings 
				WHERE OBD_Parameter_Name = 'Fuel_Rail_Pressure' 
				ORDER BY OBD_Reading_Timestamp DESC LIMIT 1;
				"""
		fuelRailPressureValue = sqltools.database_query(query, 'SELECT')
		
		return jsonify(obdComplianceValue=obdComplianceValue, 
					   elmVoltageValue=elmVoltageValue,
					   distanceWithMILValue=distanceWithMILValue,
					   coolantTemperatureValue=coolantTemperatureValue,
					   intakeAirTemperatureValue=intakeAirTemperatureValue,
					   mafValue=mafValue, 
					   engineLoadValue=engineLoadValue,
					   vehicleSpeedValue=vehicleSpeedValue,
					   vehicleRPMValue=vehicleRPMValue,
					   intakePressureValue=intakePressureValue,
					   fuelRailPressureValue=fuelRailPressureValue
					   )
					   
	GPIO.output(3, GPIO.HIGH)
	GPIO.output(5, GPIO.LOW)
	GPIO.output(7, GPIO.LOW)
	GPIO.output(29, GPIO.LOW)
	GPIO.output(31, GPIO.LOW)
	
	return render_template('obd.html')
	
@app.route('/run_script')
def run_script():
	GPIO.output(33, GPIO.HIGH)
	return render_template('control.html')
	
@app.route('/stop_script')
def stop_script():
	GPIO.output(33, GPIO.LOW)
	return render_template('control.html')
	
		
if __name__ == '__main__':
	
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(3, GPIO.OUT)
	GPIO.setup(5, GPIO.OUT)
	GPIO.setup(7, GPIO.OUT)
	GPIO.setup(33, GPIO.OUT)
	GPIO.setup(29, GPIO.OUT)
	GPIO.setup(31, GPIO.OUT)
	GPIO.output(3, GPIO.HIGH)
	GPIO.output(5, GPIO.LOW)
	GPIO.output(7, GPIO.LOW)
	GPIO.output(33, GPIO.LOW)
	GPIO.output(29, GPIO.LOW)
	GPIO.output(31, GPIO.LOW)
	
	app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)
