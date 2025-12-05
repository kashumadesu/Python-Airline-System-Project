from db_config import get_db_connection, clear_screen, pause, get_valid_input, OperationCancelled

def menu():
    apply_database_patch()
    
    while True:
        clear_screen()
        print("--- [G1] FLIGHT OPERATIONS ---")
        print("1. View Flight Schedule")
        print("2. Schedule New Flight")
        print("3. Update Flight (Status & Gate)")
        print("4. View Passenger Manifest") 
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")
        
        if choice == '1': view_schedule(); pause()
        elif choice == '2': add_flight(); pause()
        elif choice == '3': update_flight_details(); pause()
        elif choice == '4': view_manifest(); pause() 
        elif choice == '0': break

def apply_database_patch():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE flights ADD COLUMN gate VARCHAR(10) AFTER flight_date")
        conn.commit()
    except:
        pass 
    conn.close()

def view_schedule():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.flight_id, f.flight_number, f.origin, f.destination, f.flight_date, f.status, f.gate, a.model 
        FROM flights f JOIN aircrafts a ON f.aircraft_id = a.aircraft_id
    """)
    print(f"\n{'ID':<5} {'FLIGHT':<10} {'ROUTE':<25} {'DATE':<12} {'GATE':<6} {'STATUS':<12} {'AIRCRAFT'}")
    print("-" * 85)
    for r in cursor.fetchall():
        gate_display = r['gate'] if r['gate'] else "TBA"
        print(f"{r['flight_id']:<5} {r['flight_number']:<10} {r['origin']}->{r['destination']:<21} {str(r['flight_date']):<12} {gate_display:<6} {r['status']:<12} {r['model']}")
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

def update_flight_details():
    view_schedule()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        print("\n--- UPDATE FLIGHT DETAILS ---")
        f_num = get_valid_input("Enter Flight Number to Update").upper()
        
        cursor.execute("SELECT * FROM flights WHERE flight_number = %s", (f_num,))
        if not cursor.fetchone():
            print("[!] Flight not found.")
            return

        print("\n[1] Update Status (Delayed/Cancelled)")
        print("[2] Update Gate Assignment")
        print("[3] Update Both")
        
        opt = get_valid_input("Select Option")
        
        if opt in ['1', '3']:
            new_stat = get_valid_input("New Status").title()
            cursor.execute("UPDATE flights SET status = %s WHERE flight_number = %s", (new_stat, f_num))
            print(f"[UPDATED] Status set to {new_stat}.")

        if opt in ['2', '3']:
            new_gate = get_valid_input("New Gate Number").upper()
            cursor.execute("UPDATE flights SET gate = %s WHERE flight_number = %s", (new_gate, f_num))
            print(f"[UPDATED] Gate set to {new_gate}.")
            
        conn.commit()
        
    except OperationCancelled:
        print("\n[!] Update Cancelled.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()

def view_manifest():
    view_schedule()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        print("\n--- FLIGHT PASSENGER MANIFEST ---")
        fid = get_valid_input("Enter Flight ID to view passengers", int)
        
        # JOIN QUERY: Gets Passenger Name, Seat, and PNR
        query = """
            SELECT p.name, p.email, b.seat_number, b.seat_class, b.pnr, b.status
            FROM bookings b
            JOIN passengers p ON b.passenger_id = p.passenger_id
            WHERE b.flight_id = %s AND b.status = 'Confirmed'
            ORDER BY b.seat_number
        """
        cursor.execute(query, (fid,))
        passengers = cursor.fetchall()
        
        if not passengers:
            print(f"[INFO] No passengers booked for Flight ID {fid} yet.")
        else:
            print(f"\n{'SEAT':<6} {'PASSENGER NAME':<25} {'CLASS':<10} {'PNR':<8}")
            print("-" * 60)
            for p in passengers:
                print(f"{p['seat_number']:<6} {p['name']:<25} {p['seat_class']:<10} {p['pnr']:<8}")
            print("-" * 60)
            print(f"TOTAL PAX: {len(passengers)}")
            
    except OperationCancelled:
        print("\n[!] Cancelled.")
    finally:
        conn.close()
