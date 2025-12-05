from db_config import get_db_connection, clear_screen, pause

def menu():
    while True:
        clear_screen()
        print("--- [G1] FLIGHT OPERATIONS ---")
        print("1. View Flight Schedule")
        print("2. Schedule New Flight")
        print("3. Update Flight Status")
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")
        
        if choice == '1': 
            view_schedule()
            pause()
        elif choice == '2': 
            add_flight()
            pause()
        elif choice == '3': 
            update_status()
            pause()
        elif choice == '0': 
            break

def view_schedule():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.flight_number, f.origin, f.destination, f.flight_date, f.status, a.model 
        FROM flights f JOIN aircrafts a ON f.aircraft_id = a.aircraft_id
    """)
    print(f"\n{'FLIGHT':<10} {'ROUTE':<25} {'DATE':<12} {'STATUS':<12} {'AIRCRAFT'}")
    print("-" * 75)
    for r in cursor.fetchall():
        print(f"{r['flight_number']:<10} {r['origin']}->{r['destination']:<21} {str(r['flight_date']):<12} {r['status']:<12} {r['model']}")
    conn.close()

def add_flight():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM aircrafts WHERE status = 'Active'")
    fleet = cursor.fetchall()
    if not fleet:
        print("\n[!] CRITICAL: No aircraft available. All are In-Maintenance.")
        return

    print("\n--- AVAILABLE AIRCRAFT ---")
    for plane in fleet: print(f"ID {plane['aircraft_id']}: {plane['model']}")

    try:
        f_num = input("\nFlight Number (e.g. PR100): ").upper()
        origin = input("Origin: ").title()
        dest = input("Destination: ").title()
        date = input("Date (YYYY-MM-DD): ")
        aid = int(input("Select Aircraft ID: "))
        
        cursor.execute("INSERT INTO flights (flight_number, origin, destination, flight_date, aircraft_id) VALUES (%s,%s,%s,%s,%s)",
                       (f_num, origin, dest, date, aid))
        conn.commit()
        print(f"\n[SUCCESS] Flight {f_num} successfully scheduled.")
    except Exception as e:
        print(f"[ERROR] {e}")
    conn.close()

def update_status():
    view_schedule()
    f_num = input("\nEnter Flight Number: ")
    new_stat = input("New Status (Delayed/Cancelled/Arrived): ").title()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE flights SET status = %s WHERE flight_number = %s", (new_stat, f_num))
    conn.commit()
    print("[UPDATED] Status changed. G6 Customer Module will be notified.")
    conn.close()