import mysql.connector
import sys
import os

# HELPER: Clears the terminal screen
def clear_screen():
    # If Windows use 'cls', else use 'clear'
    os.system('cls' if os.name == 'nt' else 'clear')

# HELPER: Pauses so you can read the success message
def pause():
    input("\nPress Enter to continue...")

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="airline_system"
        )
        return conn
    except mysql.connector.Error as err:
        clear_screen()
        print(f"\n[CRITICAL ERROR] Database Connection Failed: {err}")
        print("Please ensure XAMPP MySQL is running.")
        sys.exit()