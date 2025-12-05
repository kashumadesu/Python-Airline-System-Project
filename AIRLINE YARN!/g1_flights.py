from db_config import get_db_connection, clear_screen, pause, get_valid_input, OperationCancelled

def menu():
    # AUTO-PATCH: This fixes the database automatically on startup
    apply_database_patch()
    
    while True:
        clear_screen()
        print("--- [G1] FLIGHT OPERATIONS ---")
        print("1. View Flight Schedule")
        print("2. Schedule New Flight")
        print("3. Update Flight Status")
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")
        
        if choice == '1': view_schedule(); pause()
        elif choice == '2': add_flight(); pause()
        elif choice == '3': update_status(); pause()
        elif choice == '0': break

def apply_database_patch():
    """Checks if the 'gate' column exists in flights, and adds it if missing."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Try to add the column. If it exists, MySQL throws an error, which we ignore.
        cursor.execute("ALTER TABLE flights ADD COLUMN gate VARCHAR(10) AFTER flight_date")
        conn.commit()
    except:
        pass # Column likely already exists
    conn.close()

def view_schedule():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # The query works now because the patch above ensures 'gate' exists
    cursor.execute("""
        SELECT f.flight_number, f.origin, f.destination, f.flight_date, f.status, f.gate, a.model 
        FROM flights f JOIN aircrafts a ON f.aircraft_id = a.aircraft_id
    """)
    print(f"\n{'FLIGHT':<10} {'ROUTE':<25} {'DATE':<12} {'GATE':<6} {'STATUS':<12} {'AIRCRAFT'}")
    print("-" * 80)
    for r in cursor.fetchall():
        gate_display = r['gate'] if r['gate'] else "TBA"
        print(f"{r['flight_number']:<10} {r['origin']}->{r['destination']:<21} {str(r['flight_date']):<12} {gate_display:<6} {r['status']:<12} {r['model']}")
    conn.close()

def add_flight():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM aircrafts WHERE status = 'Active'")
    fleet = cursor.fetchall()
    if not fleet:
        print("\n[!] CRITICAL: No aircraft available. All are In-Maintenance.")
        conn.close()
        return

    print("\n--- AVAILABLE AIRCRAFT ---")
    for plane in fleet: print(f"ID {plane['aircraft_id']}: {plane['model']}")

    try:
        f_num = get_valid_input("\nFlight Number (e.g. PR100)").upper()
        origin = get_valid_input("Origin").title()
        dest = get_valid_input("Destination").title()
        date = get_valid_input("Date (YYYY-MM-DD)")
        
        # GATE INPUT
        gate = get_valid_input("Gate Number (e.g. G4)") 
        
        aid = get_valid_input("Select Aircraft ID", int)
        
        cursor.execute("""
            INSERT INTO flights (flight_number, origin, destination, flight_date, gate, aircraft_id) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (f_num, origin, dest, date, gate, aid))
        
        conn.commit()
        print(f"\n[SUCCESS] Flight {f_num} successfully scheduled at Gate {gate}.")
        
    except OperationCancelled:
        print("\n[!] Flight Scheduling Cancelled.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()

def update_status():
    view_schedule()
    # FIX: Connect first so 'conn' exists if we cancel
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        f_num = get_valid_input("\nEnter Flight Number")
        new_stat = get_valid_input("New Status (Delayed/Cancelled/Arrived)").title()
        
        cursor.execute("UPDATE flights SET status = %s WHERE flight_number = %s", (new_stat, f_num))
        conn.commit()
        print("[UPDATED] Status changed. G6 Customer Module will be notified.")
        
    except OperationCancelled:
        print("\n[!] Update Cancelled.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()
