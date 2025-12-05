from db_config import get_db_connection, clear_screen, pause, get_valid_input, OperationCancelled
import mysql.connector

def menu():
    while True:
        clear_screen()
        print("--- [G5] AIRCRAFT MAINTENANCE ---")
        print("1. View Fleet Status")
        print("2. Update Aircraft Status")
        print("3. Add New Aircraft")
        print("4. Decommission (Delete) Aircraft")
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")

        if choice == '1': view_fleet(); pause()
        elif choice == '2': update_status(); pause()
        elif choice == '3': add_aircraft(); pause()
        elif choice == '4': delete_aircraft(); pause()
        elif choice == '0': break

def view_fleet():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM aircrafts")
    print(f"\n{'ID':<5} {'MODEL':<20} {'STATUS'}")
    print("-" * 40)
    for a in cursor.fetchall():
        print(f"{a['aircraft_id']:<5} {a['model']:<20} {a['status']}")
    conn.close()

def update_status():
    view_fleet()
    # FIX: Connect first
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        aid = get_valid_input("\nEnter Aircraft ID to modify", int)
        new_status = get_valid_input("Set Status (Active/In-Maintenance)").title()
        
        cursor.execute("UPDATE aircrafts SET status = %s WHERE aircraft_id = %s", (new_status, aid))
        conn.commit()
        print(f"\n[UPDATED] Aircraft {aid} is now {new_status}.")
        
        if new_status == 'In-Maintenance':
            print("[ALERT] G1 Flight Module has been notified. This plane cannot be scheduled.")
    except OperationCancelled:
        print("\n[!] Update Cancelled.")
    finally:
        conn.close()

def add_aircraft():
    # FIX: Connect first
    conn = get_db_connection()
    cursor = conn.cursor()
    print("\n--- ACQUIRE NEW AIRCRAFT ---")
    
    try:
        model = get_valid_input("Enter Aircraft Model (e.g. Boeing 777)")
        
        confirm = get_valid_input(f"Confirm purchase of '{model}'? (Y/N)").upper()
        if confirm != 'Y':
            print("\n[!] Operation Cancelled. Aircraft NOT added.")
            return # Returns to menu, finally block handles close

        cursor.execute("INSERT INTO aircrafts (model, status) VALUES (%s, 'Active')", (model,))
        conn.commit()
        print(f"\n[SUCCESS] {model} successfully added to fleet.")
        
    except OperationCancelled:
        print("\n[!] Acquisition Cancelled.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()

def delete_aircraft():
    view_fleet()
    print("\n--- DECOMMISSION AIRCRAFT ---")
    # FIX: Connect first
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        aid = get_valid_input("Enter Aircraft ID to DELETE", int)
        
        confirm = get_valid_input(f"WARNING: Are you sure you want to delete ID {aid}? (Y/N)").upper()
        if confirm != 'Y':
            print("\n[!] Deletion Cancelled.")
            return
            
        cursor.execute("DELETE FROM aircrafts WHERE aircraft_id = %s", (aid,))
        conn.commit()
        print(f"\n[SUCCESS] Aircraft {aid} has been removed from the database.")
        
    except mysql.connector.Error as err:
        if err.errno == 1451:
            print(f"\n[CRITICAL ERROR] Cannot delete Aircraft {aid}.")
            print("Reason: This aircraft is linked to existing Flight Records (G1).")
            print("Solution: Set status to 'In-Maintenance' instead.")
        else:
            print(f"[ERROR] {err}")
            
    except OperationCancelled:
        print("\n[!] Deletion Cancelled.")
    finally:
        conn.close()