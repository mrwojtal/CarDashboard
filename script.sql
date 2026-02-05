DROP TABLE IF EXISTS Tachometer_Frame;
DROP TABLE IF EXISTS Cluster_Frame;
DROP TABLE IF EXISTS LCD_Frame;

CREATE TABLE Tachometer_Frame
(
	RPM						INT				NOT NULL,
	Frame_Timestamp			DATETIME		TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE Cluster_Frame
(
	Brightness				INT				NOT NULL,
	Cluster_Mode			VARCHAR(30),
	Control_Alert			VARCHAR(10),
	Control_Cruise			VARCHAR(10),
	Control_DDE				VARCHAR(10),
	Control_Seatbelts		VARCHAR(10),
	Tacho_Illumination_1	VARCHAR(10),
	Tacho_Illumination_2	VARCHAR(10),
	Tacho_Illumination_3	VARCHAR(10),
	Tacho_Illumination_4	VARCHAR(10),
	Frame_Timestamp			DATETIME		TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE LCD_Frame
(
	LCD_Mode				VARCHAR(30),
	LCD_Unit				VARCHAR(30),
	LCD_Value				FLOAT			NOT NULL,
	Frame_Timestamp			DATETIME		TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE OBD_Readings
(
	OBD_Parameter_Name		VARCHAR(30),
	OBD_Parameter_Value		VARCHAR(30),
	OBD_Reading_Timestamp	DATETIME		TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL	
);

