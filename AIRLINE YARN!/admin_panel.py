from db_config import get_db_connection, clear_screen, pause, get_valid_input, OperationCancelled
import mysql.connector

def menu():
    while True:
        clear_screen()
        print("="*60)
        print("   GOD MODE: SYSTEM ADMINISTRATOR")
        print("="*60)
        print("1. [USERS]   Manage Passengers (Edit Points / Ban)")
        print("2. [STAFF]   Manage Crew (Fire / Reset Status)")
        print("3. [OPS]     Manage Flights (Super Delete)")
        print("4. [FLEET]   Manage Aircraft (Force Remove)")
        print("5. [FINANCE] Manage Bookings (Force Cancel)")
        print("9. [DANGER]  FACTORY RESET SYSTEM")
        print("0. Return to Main Menu")
        
        choice = input("\nGOD_MODE > ")
        
        if choice == '1': manage_passengers()
        elif choice == '2': manage_crew()
        elif choice == '3': manage_flights()
        elif choice == '4': manage_fleet()
        elif choice == '5': manage_bookings()
        elif choice == '9': factory_reset()
        elif choice == '0': break
        else: pause()

# ==========================================
# 1. PASSENGER GOD MODE
# ==========================================
def manage_passengers():
    clear_screen()
    print("--- MANAGE PASSENGERS ---")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # List all
    cursor.execute("SELECT * FROM passengers")
    for p in cursor.fetchall():
        print(f"ID {p['passenger_id']} | {p['name']} | Pts: {p['loyalty_points']} | {p['tier']}")
        
    print("\n[1] Edit Loyalty Points")
    print("[2] Delete Passenger (Ban)")
    print("[0] Cancel")
    
    try:
        opt = get_valid_input("Select Action")
        if opt == '1':
            pid = get_valid_input("Passenger ID", int)
            pts = get_valid_input("New Point Balance", int)
            cursor.execute("UPDATE passengers SET loyalty_points = %s WHERE passenger_id = %s", (pts, pid))
            conn.commit()
            print("[SUCCESS] Points Updated.")
            
        elif opt == '2':
            pid = get_valid_input("Passenger ID to DELETE", int)
            confirm = get_valid_input("This will delete all their bookings. Confirm? (Y/N)").upper()
            if confirm == 'Y':
                # Cascade Delete Logic
                cursor.execute("DELETE FROM bookings WHERE passenger_id = %s", (pid,))
                cursor.execute("DELETE FROM passengers WHERE passenger_id = %s", (pid,))
                conn.commit()
                print("[SUCCESS] Passenger Banned and records wiped.")
                
    except OperationCancelled: return
    except Exception as e: print(f"[ERROR] {e}")
    finally: conn.close(); pause()

# ==========================================
# 2. CREW GOD MODE
# ==========================================
def manage_crew():
    clear_screen()
    print("--- MANAGE CREW ---")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM crew")
    for c in cursor.fetchall():
        print(f"ID {c['crew_id']} | {c['name']} | {c['role']} | {c['status']}")
        
    print("\n[1] Delete Crew Member")
    print("[2] Reset Status to Available")
    print("[0] Cancel")
    
    try:
        opt = get_valid_input("Select Action")
        if opt == '1':
            cid = get_valid_input("Crew ID to Fire", int)
            cursor.execute("DELETE FROM flight_crew WHERE crew_id = %s", (cid,)) # Remove assignments first
            cursor.execute("DELETE FROM crew WHERE crew_id = %s", (cid,))
            conn.commit()
            print("[SUCCESS] Crew member removed.")
        elif opt == '2':
            cid = get_valid_input("Crew ID to Reset", int)
            cursor.execute("UPDATE crew SET status = 'Available' WHERE crew_id = %s", (cid,))
            conn.commit()
            print("[SUCCESS] Crew status reset.")
            
    except OperationCancelled: return
    except Exception as e: print(f"[ERROR] {e}")
    finally: conn.close(); pause()

# ==========================================
# 3. FLIGHT GOD MODE
# ==========================================
def manage_flights():
    clear_screen()
    print("--- MANAGE FLIGHTS ---")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT flight_id, flight_number, status FROM flights")
    for f in cursor.fetchall():
        print(f"ID {f['flight_id']} | {f['flight_number']} | {f['status']}")
        
    print("\n[1] SUPER DELETE FLIGHT (Removes Flight + Bookings + Crew assignments)")
    print("[0] Cancel")
    
    try:
        opt = get_valid_input("Select Action")
        if opt == '1':
            fid = get_valid_input("Flight ID to Nuke", int)
            confirm = get_valid_input("WARNING: This destroys all data for this flight. Confirm? (Y/N)").upper()
            if confirm == 'Y':
                # Manual Cascade Delete
                cursor.execute("DELETE FROM bookings WHERE flight_id = %s", (fid,))
                cursor.execute("DELETE FROM flight_crew WHERE flight_id = %s", (fid,))
                cursor.execute("DELETE FROM flights WHERE flight_id = %s", (fid,))
                conn.commit()
                print("[SUCCESS] Flight Record Obliterated.")
                
    except OperationCancelled: return
    except Exception as e: print(f"[ERROR] {e}")
    finally: conn.close(); pause()

# ==========================================
# 4. FLEET GOD MODE
# ==========================================
def manage_fleet():
    clear_screen()
    print("--- MANAGE FLEET ---")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM aircrafts")
    for a in cursor.fetchall():
        print(f"ID {a['aircraft_id']} | {a['model']} | {a['status']}")
        
    print("\n[1] Force Delete Aircraft")
    print("[0] Cancel")
    
    try:
        if get_valid_input("Select Action") == '1':
            aid = get_valid_input("Aircraft ID", int)
            # Standard delete (might fail if foreign keys exist, unless we update flights to NULL)
            try:
                cursor.execute("DELETE FROM aircrafts WHERE aircraft_id = %s", (aid,))
                conn.commit()
                print("[SUCCESS] Aircraft deleted.")
            except mysql.connector.Error:
                print("[!] Cannot delete: Active flights exist. Delete the flights first.")
                
    except OperationCancelled: return
    except Exception as e: print(f"[ERROR] {e}")
    finally: conn.close(); pause()

# ==========================================
# 5. BOOKING GOD MODE
# ==========================================
def manage_bookings():
    clear_screen()
    print("--- MANAGE BOOKINGS ---")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT booking_id, pnr, status FROM bookings")
    for b in cursor.fetchall():
        print(f"ID {b['booking_id']} | PNR: {b['pnr']} | {b['status']}")
        
    print("\n[1] Force Delete Booking (Remove from DB)")
    print("[0] Cancel")
    
    try:
        if get_valid_input("Select Action") == '1':
            bid = get_valid_input("Booking ID", int)
            cursor.execute("DELETE FROM checkin WHERE booking_id = %s", (bid,))
            cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (bid,))
            conn.commit()
            print("[SUCCESS] Booking deleted from history.")
    except OperationCancelled: return
    except Exception as e: print(f"[ERROR] {e}")
    finally: conn.close(); pause()

# ==========================================
# 9. FACTORY RESET (NUCLEAR OPTION)
# ==========================================
def factory_reset():
    clear_screen()
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("          DANGER: FACTORY RESET             ")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("This will DELETE ALL DATA in the system.")
    print("Passengers, Flights, Bookings will be gone.")
    
    try:
        confirm = get_valid_input("Type 'RESET' to confirm").upper()
        if confirm == 'RESET':
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Disable FK checks to allow truncate
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            tables = ['checkin', 'bookings', 'flight_crew', 'flights', 'passengers', 'crew']
            for t in tables:
                cursor.execute(f"TRUNCATE TABLE {t}")
                print(f" > Wiping {t}...")
                
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            conn.commit()
            conn.close()
            print("\n[SYSTEM RESET COMPLETE] Database is clean.")
    except OperationCancelled: return
    except Exception as e: print(f"[ERROR] {e}")
    pause()