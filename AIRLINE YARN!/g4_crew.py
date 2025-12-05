from db_config import get_db_connection, clear_screen, pause, get_valid_input, OperationCancelled

def menu():
    apply_database_patch()
    
    while True:
        clear_screen()
        print("--- [G4] CREW MANAGEMENT ---")
        print("1. View Crew Roster (Profiles)")
        print("2. Assign Crew to Flight")
        print("3. View Flight Assignments (Attendance)")
        print("4. Payroll System (View & Edit)") 
        print("5. Manage Certifications")
        print("6. Hire New Crew Member")
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")
        
        if choice == '1': view_crew(); pause()
        elif choice == '2': assign_crew(); pause()
        elif choice == '3': view_assignments(); pause()
        elif choice == '4': view_payroll() 
        elif choice == '5': manage_certifications(); pause()
        elif choice == '6': add_crew(); pause()
        elif choice == '0': break

def apply_database_patch():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE crew ADD COLUMN salary_rate INT DEFAULT 5000")
        cursor.execute("ALTER TABLE crew ADD COLUMN license_status VARCHAR(50) DEFAULT 'Active'")
        cursor.execute("ALTER TABLE crew ADD COLUMN flight_hours INT DEFAULT 0")
        conn.commit()
    except:
        pass
    conn.close()

def view_crew():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM crew")
    print(f"\n{'ID':<5} {'NAME':<20} {'ROLE':<15} {'CERTIFICATION':<15} {'STATUS'}")
    print("-" * 75)
    for c in cursor.fetchall():
        lic = c.get('license_status', 'Active')
        print(f"{c['crew_id']:<5} {c['name']:<20} {c['role']:<15} {lic:<15} {c['status']}")
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
        
        cursor.execute("SELECT * FROM crew WHERE status='Available' AND license_status='Active'")
        available_crew = cursor.fetchall()
        
        if not available_crew:
            print("\n[!] No crew available (Check Rest Periods or Certifications).")
            conn.close()
            return

        print("\n--- AVAILABLE CREW ---")
        for c in available_crew:
            print(f"ID {c['crew_id']}: {c['name']} ({c['role']})")

        cid = get_valid_input("\nEnter Crew ID to assign", int)
        
        cursor.execute("INSERT INTO flight_crew (flight_id, crew_id) VALUES (%s, %s)", (fid, cid))
        cursor.execute("UPDATE crew SET status = 'On-Duty', flight_hours = flight_hours + 4 WHERE crew_id = %s", (cid,))
        conn.commit()
        print(f"\n[SUCCESS] Crew Member assigned. Status set to On-Duty.")
        
    except OperationCancelled:
        print("\n[!] Assignment Cancelled.")
    except Exception as e:
        print(f"\n[ERROR] Assignment failed: {e}")
    conn.close()

def view_assignments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT f.flight_number, f.flight_date, c.name, c.role
        FROM flight_crew fc
        JOIN flights f ON fc.flight_id = f.flight_id
        JOIN crew c ON fc.crew_id = c.crew_id
        ORDER BY f.flight_number
    """
    cursor.execute(query)
    print("\n--- ATTENDANCE LOG (FLIGHT HISTORY) ---")
    print(f"{'DATE':<12} {'FLIGHT':<10} {'CREW MEMBER':<20} {'ROLE'}")
    print("-" * 60)
    for row in cursor.fetchall():
        print(f"{str(row['flight_date']):<12} {row['flight_number']:<10} {row['name']:<20} {row['role']}")
    conn.close()

def view_payroll():
    # Loop keeps user in Payroll menu until they choose to leave
    while True:
        clear_screen()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        print("--- PAYROLL SYSTEM ---")
        print("Rates per Flight: Captain=₱25k | Co-Pilot=₱15k | Cabin Crew=₱4.5k")
        
        query = """
            SELECT c.crew_id, c.name, c.role, c.salary_rate, COUNT(fc.assignment_id) as trip_count
            FROM crew c
            LEFT JOIN flight_crew fc ON c.crew_id = fc.crew_id
            GROUP BY c.crew_id
        """
        cursor.execute(query)
        
        print(f"\n{'ID':<5} {'NAME':<20} {'ROLE':<15} {'RATE':<10} {'TRIPS':<6} {'TOTAL PAY'}")
        print("-" * 75)
        for c in cursor.fetchall():
            rate = c.get('salary_rate', 0)
            total = rate * c['trip_count']
            print(f"{c['crew_id']:<5} {c['name']:<20} {c['role']:<15} ₱{rate:<9} {c['trip_count']:<6} ₱{total:,}")
        
        print("\n[1] Edit Salary Rate (Give Raise)")
        print("[0] Back")
        
        choice = input("\nSelect: ")
        
        if choice == '1':
            edit_salary(conn) # Pass connection to save reopening it
        elif choice == '0':
            conn.close()
            break
        else:
            conn.close()

def edit_salary(conn):
    try:
        print("\n--- EDIT SALARY RATE ---")
        cid = get_valid_input("Enter Crew ID to update", int)
        
        # Check if ID exists (using existing connection)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, salary_rate FROM crew WHERE crew_id = %s", (cid,))
        crew = cursor.fetchone()
        
        if not crew:
            print("[!] Crew ID not found.")
            pause()
            return

        print(f"Current Rate for {crew['name']}: ₱{crew['salary_rate']}")
        new_rate = get_valid_input("Enter New Salary Rate", int)
        
        cursor.execute("UPDATE crew SET salary_rate = %s WHERE crew_id = %s", (new_rate, cid))
        conn.commit()
        print(f"\n[SUCCESS] Salary for {crew['name']} updated to ₱{new_rate:,}.")
        pause()
        
    except OperationCancelled:
        print("\n[!] Cancelled.")
        pause()
    except Exception as e:
        print(f"[ERROR] {e}")
        pause()

def manage_certifications():
    view_crew()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cid = get_valid_input("\nEnter Crew ID to update", int)
        print("Options: [1] Active  [2] Expired  [3] Suspended")
        opt = get_valid_input("Select New Status")
        status_map = {'1': 'Active', '2': 'Expired', '3': 'Suspended'}
        
        if opt in status_map:
            cursor.execute("UPDATE crew SET license_status = %s WHERE crew_id = %s", (status_map[opt], cid))
            conn.commit()
            print(f"\n[SUCCESS] Certification status updated.")
        else:
            print("[!] Invalid Option.")
    except OperationCancelled:
        print("\n[!] Cancelled.")
    conn.close()

def add_crew():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("\n--- HIRE NEW CREW MEMBER ---")
    try:
        name = get_valid_input("Enter Full Name")
        
        print("\nSelect Role:")
        print("[1] Captain (Pilot)       - Rate: ₱25,000/flight")
        print("[2] First Officer (Co-Pilot) - Rate: ₱15,000/flight")
        print("[3] Cabin Crew            - Rate: ₱4,500/flight")
        
        role_opt = get_valid_input("Select Option")
        
        if role_opt == '1':
            role = "Captain"
            rate = 25000
        elif role_opt == '2':
            role = "First Officer"
            rate = 15000
        elif role_opt == '3':
            role = "Cabin Crew"
            rate = 4500
        else:
            print("[!] Invalid Role Selection.")
            return

        cursor.execute("""
            INSERT INTO crew (name, role, salary_rate, status, license_status) 
            VALUES (%s, %s, %s, 'Available', 'Active')
        """, (name, role, rate))
        
        conn.commit()
        print(f"\n[SUCCESS] {name} hired as {role} with rate ₱{rate:,}.")
        
    except OperationCancelled:
        print("\n[!] Hiring Cancelled.")
    except Exception as e:
        print(f"[ERROR] {e}")
    conn.close()
