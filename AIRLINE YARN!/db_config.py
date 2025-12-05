import mysql.connector
import sys
import os

# HELPER: Clears the terminal screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# HELPER: Pauses so you can read the success message
def pause():
    input("\nPress Enter to continue...")

# HELPER: Forces user to type something (Input Validation)
def get_valid_input(prompt, input_type=str):
    while True:
        value = input(prompt).strip() # Removes accidental spaces
        
        if not value:
            print("   [!] Error: Input cannot be empty. Please try again.")
            continue
            
        if input_type == int:
            try:
                return int(value)
            except ValueError:
                print("   [!] Error: Please enter a valid number.")
                continue
        
        return value

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