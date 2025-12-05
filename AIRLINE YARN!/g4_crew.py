from db_config import get_db_connection, clear_screen, pause, get_valid_input, OperationCancelled

def menu():
    while True:
        clear_screen()
        print("--- [G4] CREW MANAGEMENT ---")
        print("1. View Crew Roster")
        print("2. Assign Crew to Flight")
        print("3. View Flight Assignments")
        print("4. Hire New Crew Member")
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")
        
        if choice == '1': view_crew(); pause()
        elif choice == '2': assign_crew(); pause()
        elif choice == '3': view_assignments(); pause()
        elif choice == '4': add_crew(); pause()
        elif choice == '0': break

def view_crew():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM crew")
    print("\n--- CREW ROSTER ---")
    print(f"{'ID':<5} {'NAME':<20} {'ROLE':<15} {'STATUS'}")
    print("-" * 55)
    for c in cursor.fetchall():
        print(f"{c['crew_id']:<5} {c['name']:<20} {c['role']:<15} {c['status']}")
    conn.close()

def assign_crew():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT flight_id, flight_number, destination FROM flights WHERE status='Scheduled'")
    flights = cursor.fetchall()
    print("\n--- SCHEDULED FLIGHTS ---")
    for f in flights: print(f"ID {f['flight_id']} | {f['flight_number']} to {f['destination']}")
    
    try:
        fid = get_valid_input("\nEnter Flight ID", int)
        view_crew()
        cid = get_valid_input("\nEnter Crew ID to assign", int)
        
        cursor.execute("INSERT INTO flight_crew (flight_id, crew_id) VALUES (%s, %s)", (fid, cid))
        cursor.execute("UPDATE crew SET status = 'On-Duty' WHERE crew_id = %s", (cid,))
        conn.commit()
        print(f"\n[SUCCESS] Crew Member assigned to flight.")
        
    except OperationCancelled:
        print("\n[!] Assignment Cancelled.")
    except Exception as e:
        print(f"\n[ERROR] Assignment failed (Check IDs): {e}")
    conn.close()

def view_assignments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT f.flight_number, c.name, c.role
        FROM flight_crew fc
        JOIN flights f ON fc.flight_id = f.flight_id
        JOIN crew c ON fc.crew_id = c.crew_id
        ORDER BY f.flight_number
    """
    cursor.execute(query)
    print("\n--- FLIGHT ASSIGNMENTS ---")
    print(f"{'FLIGHT':<10} {'CREW MEMBER':<20} {'ROLE'}")
    print("-" * 50)
    for row in cursor.fetchall():
        print(f"{row['flight_number']:<10} {row['name']:<20} {row['role']}")
    conn.close()

def add_crew():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("\n--- HIRE NEW CREW ---")
    
    try:
        name = get_valid_input("Enter Name")
        print("Roles: Pilot, Co-Pilot, Cabin Crew")
        role = get_valid_input("Enter Role").title()
        
        cursor.execute("INSERT INTO crew (name, role, status) VALUES (%s, %s, 'Available')", (name, role))
        conn.commit()
        print(f"\n[SUCCESS] {name} added to roster.")
        
    except OperationCancelled:
        print("\n[!] Hiring Cancelled.")
    except Exception as e:
        print(f"[ERROR] {e}")
    conn.close()