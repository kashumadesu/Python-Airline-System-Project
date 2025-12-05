from db_config import get_db_connection, clear_screen, pause, get_valid_input, OperationCancelled
import mysql.connector

def menu():
    while True:
        clear_screen()
        print("--- [G5] AIRCRAFT MAINTENANCE ---")
        print("1. View Fleet Status")
        print("2. Update Status & Log Defects") 
        print("3. Add New Aircraft")
        print("4. Decommission (Delete) Aircraft")
        print("5. View Maintenance Logs")       # <--- NEW
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")

        if choice == '1': view_fleet(); pause()
        elif choice == '2': update_status(); pause()
        elif choice == '3': add_aircraft(); pause()
        elif choice == '4': delete_aircraft(); pause()
        elif choice == '5': view_logs(); pause()
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        aid = get_valid_input("\nEnter Aircraft ID to modify", int)
        new_status = get_valid_input("Set Status (Active/In-Maintenance)").title()
        
        cursor.execute("UPDATE aircrafts SET status = %s WHERE aircraft_id = %s", (new_status, aid))
        
        # DEFECT LOGGING LOGIC
        if new_status == 'In-Maintenance':
            print("\n[MAINTENANCE LOG REQUIRED]")
            issue = get_valid_input("Describe the Defect/Issue")
            action = "Pending Repair"
            cursor.execute("INSERT INTO maintenance_logs (aircraft_id, issue_description, action_taken) VALUES (%s, %s, %s)", 
                           (aid, issue, action))
            print(f"[LOGGED] Defect recorded. G1 Flight Module notified.")
        
        elif new_status == 'Active':
            cursor.execute("INSERT INTO maintenance_logs (aircraft_id, issue_description, action_taken) VALUES (%s, 'Routine Check', 'Cleared')", (aid,))

        conn.commit()
        print(f"\n[UPDATED] Aircraft {aid} is now {new_status}.")
        
    except OperationCancelled:
        print("\n[!] Cancelled.")
    finally:
        conn.close()

def view_logs():
    print("\n--- MAINTENANCE HISTORY LOG ---")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT m.log_date, a.model, m.issue_description, m.action_taken 
        FROM maintenance_logs m JOIN aircrafts a ON m.aircraft_id = a.aircraft_id
        ORDER BY m.log_date DESC
    """)
    print(f"{'DATE':<20} {'AIRCRAFT':<15} {'ISSUE':<25} {'ACTION'}")
    print("-" * 75)
    for r in cursor.fetchall():
        print(f"{str(r['log_date']):<20} {r['model']:<15} {r['issue_description']:<25} {r['action_taken']}")
    conn.close()

def add_aircraft():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("\n--- ACQUIRE NEW AIRCRAFT ---")
    try:
        model = get_valid_input("Enter Aircraft Model (e.g. Boeing 777)")
        confirm = get_valid_input(f"Confirm purchase of '{model}'? (Y/N)").upper()
        if confirm != 'Y': return

        cursor.execute("INSERT INTO aircrafts (model, status) VALUES (%s, 'Active')", (model,))
        conn.commit()
        print(f"\n[SUCCESS] {model} successfully added to fleet.")
    except OperationCancelled:
        print("\n[!] Cancelled.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()

def delete_aircraft():
    view_fleet()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        aid = get_valid_input("Enter Aircraft ID to DELETE", int)
        confirm = get_valid_input(f"WARNING: Delete ID {aid}? (Y/N)").upper()
        if confirm != 'Y': return
            
        cursor.execute("DELETE FROM aircrafts WHERE aircraft_id = %s", (aid,))
        conn.commit()
        print(f"\n[SUCCESS] Aircraft {aid} removed.")
    except mysql.connector.Error as err:
        if err.errno == 1451:
            print(f"\n[CRITICAL ERROR] Cannot delete. Aircraft linked to existing records.")
        else:
            print(f"[ERROR] {err}")
    except OperationCancelled:
        print("\n[!] Cancelled.")
    finally:
        conn.close()