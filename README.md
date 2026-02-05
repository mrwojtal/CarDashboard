# Model of a car dashboard (Bachelor's thesis)

CarDashboard is a project that visualizes real-time car data on reverse engineered Tachometer from MiniR50 and local website. 
The system retrieves data from a vehicle via an **ELM327 OBD-II adapter**, transmits it over **Bluetooth** to a **Raspberry Pi**, and controls a physical **Mini R50 tachometer** using **CAN bus**. The tachometer displays actual engine data from the car.
Data is simultaenously displayed on the website, additionally user can control data that is displayed on tachometer.

Data retrieved from car via diagnostic interface is stored in database.
With help of SQL queries data is displayed on the website and transmitted on CAN to tachometer.

## Technologies
- **Python 3** – backend application logic  
- **Flask** – web server and dashboard interface  
- **HTML & CSS** – frontend for interactive views  
- **SQL** – database for storing and querying car data  
- **Bluetooth** – communication with ELM327 based OBD-II interface
- **CAN** - communication with MiniR50 tachometer  
