import mysql.connector
import sys
import os

# 1. SIGNAL TO CANCEL OPERATIONS (This is what was missing)
class OperationCancelled(Exception):
    pass

# 2. HELPER FUNCTIONS
def clear_screen():
    # If Windows use 'cls', else use 'clear'
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\nPress Enter to continue...")

def get_valid_input(prompt, input_type=str):
    """
    Forces user to enter valid data.
    If user types '0', it raises OperationCancelled to go back.
    """
    while True:
        user_input = input(f"{prompt} (0 to Cancel): ").strip()
        
        # Check for Cancel Signal
        if user_input == '0':
            raise OperationCancelled
            
        # Check for Empty Input
        if not user_input:
            print("   [!] Error: Input cannot be empty.")
            continue
            
        # Check for Number Requirement
        if input_type == int:
            try:
                return int(user_input)
            except ValueError:
                print("   [!] Error: Please enter a valid number.")
                continue
        
        return user_input

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
        print(f"[CRITICAL ERROR] Database Connection Failed: {err}")
        sys.exit()
