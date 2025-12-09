import time
from db_config import get_db_connection, clear_screen, pause, get_valid_input, OperationCancelled

def menu():
    while True:
        clear_screen()
        print("--- [G4] CREW MANAGEMENT (DYNAMIC ROLES) ---")
        print("1. View Crew Roster")
        print("2. Assign Crew to Flight")
        print("3. View Assignments")
        print("4. Payroll System") 
        print("5. Manage Certifications")
        print("6. Hire New Crew Member")
        print("7. Reassign Role")  
        print("8. Manage Job Roles")    
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")
        
        if choice == '1': view_crew(); pause()
        elif choice == '2': assign_crew(); pause()
        elif choice == '3': view_assignments(); pause()
        elif choice == '4': view_payroll() 
        elif choice == '5': manage_certifications(); pause()
        elif choice == '6': add_crew(); pause()
        elif choice == '7': reassign_role(); pause()
        elif choice == '8': manage_job_roles(); pause()
        elif choice == '0': 
            print("Going back to menu...")
            time.sleep(1)
            break
        else:
            print("[!] Invalid Selection")
            pause()

def view_crew():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM crew")
    print(f"\n{'ID':<5} {'NAME':<20} {'ROLE':<15} {'CERTIFICATION':<15} {'STATUS'}")
    print("-" * 75)
    for c in cursor.fetchall():
        lic = c.get('license_status', 'Active')
        role_display = c['role'] if c['role'] else "Unknown"
        print(f"{c['crew_id']:<5} {c['name']:<20} {role_display:<15} {lic:<15} {c['status']}")
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
            print("\n[!] No crew available.")
            conn.close()
            return

        print("\n--- AVAILABLE CREW ---")
        for c in available_crew:
            print(f"ID {c['crew_id']}: {c['name']} ({c['role']})")

        cid = get_valid_input("\nEnter Crew ID to assign", int)
        cursor.execute("INSERT INTO flight_crew (flight_id, crew_id) VALUES (%s, %s)", (fid, cid))
        cursor.execute("UPDATE crew SET status = 'On-Duty', flight_hours = flight_hours + 4 WHERE crew_id = %s", (cid,))
        conn.commit()
        print(f"\n[SUCCESS] Crew Member assigned.")
    except OperationCancelled:
        print("\n[!] Cancelled.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
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
    print("\n--- ATTENDANCE LOG ---")
    print(f"{'DATE':<12} {'FLIGHT':<10} {'CREW MEMBER':<20} {'ROLE'}")
    print("-" * 60)
    for row in cursor.fetchall():
        print(f"{str(row['flight_date']):<12} {row['flight_number']:<10} {row['name']:<20} {row['role']}")
    conn.close()

def view_payroll():
    while True:
        clear_screen()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        print("--- PAYROLL SYSTEM ---")
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
        
        print("\n[1] Edit Salary Rate")
        print("[0] Back")
        if input("\nSelect: ") == '0': conn.close(); break
        else: edit_salary(conn)

def edit_salary(conn):
    try:
        cid = get_valid_input("Enter Crew ID", int)
        rate = get_valid_input("Enter New Rate", int)
        cursor = conn.cursor()
        cursor.execute("UPDATE crew SET salary_rate = %s WHERE crew_id = %s", (rate, cid))
        conn.commit()
        print("[SUCCESS] Salary Updated.")
    except: pass

def manage_certifications():
    view_crew()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cid = get_valid_input("\nEnter Crew ID", int)
        print("[1] Active  [2] Expired  [3] Suspended")
        opt = get_valid_input("Select Status")
        status_map = {'1': 'Active', '2': 'Expired', '3': 'Suspended'}
        if opt in status_map:
            cursor.execute("UPDATE crew SET license_status = %s WHERE crew_id = %s", (status_map[opt], cid))
            conn.commit()
            print("[SUCCESS] Updated.")
    except: pass
    conn.close()

# --- 1. MANAGE JOB ROLES (Add 'Police', etc.) ---
def manage_job_roles():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("\n--- JOB ROLES DATABASE ---")
    cursor.execute("SELECT * FROM crew_roles")
    roles = cursor.fetchall()
    
    print(f"{'ID':<5} {'ROLE NAME':<20} {'DEFAULT SALARY'}")
    print("-" * 45)
    for r in roles:
        print(f"{r['role_id']:<5} {r['role_name']:<20} ₱{r['default_salary']:,}")
        
    print("\n[1] Add New Role (e.g. Police)")
    print("[0] Back")
    
    try:
        choice = input("\nSelect: ")
        if choice == '1':
            name = get_valid_input("Enter New Role Name (e.g. Police)")
            sal = get_valid_input("Enter Default Salary", int)
            
            cursor.execute("INSERT INTO crew_roles (role_name, default_salary) VALUES (%s, %s)", (name, sal))
            conn.commit()
            print(f"\n[SUCCESS] Role '{name}' added to database.")
            
    except Exception as e:
        print(f"[ERROR] {e}")
    conn.close()

# --- 2. REASSIGN ROLE (Promote/Change Job) ---
def reassign_role():
    view_crew()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cid = get_valid_input("\nEnter Crew ID to Reassign", int)
        
        # Show available roles from DB
        print("\nSelect New Role:")
        cursor.execute("SELECT * FROM crew_roles")
        roles = cursor.fetchall()
        for r in roles:
            print(f"[{r['role_id']}] {r['role_name']}")
            
        rid = get_valid_input("Select Role ID", int)
        selected = next((r for r in roles if r['role_id'] == rid), None)
        
        if selected:
            cursor.execute("UPDATE crew SET role = %s, salary_rate = %s WHERE crew_id = %s", 
                           (selected['role_name'], selected['default_salary'], cid))
            conn.commit()
            print(f"\n[SUCCESS] Role changed to {selected['role_name']}.")
            
    except OperationCancelled: pass
    except Exception as e: print(f"[ERROR] {e}")
    conn.close()

# --- 3. ADD CREW (Dynamic List) ---
def add_crew():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    print("\n--- HIRE NEW CREW MEMBER ---")
    try:
        name = get_valid_input("Enter Full Name")
        
        print("\nSelect Job Role:")
        cursor.execute("SELECT * FROM crew_roles")
        roles = cursor.fetchall()
        
        for r in roles:
            print(f"[{r['role_id']}] {r['role_name']:<15} - Rate: ₱{r['default_salary']:,}")
        
        rid = get_valid_input("Select Option", int)
        selected = next((r for r in roles if r['role_id'] == rid), None)
        
        if selected:
            cursor.execute("""
                INSERT INTO crew (name, role, salary_rate, status, license_status) 
                VALUES (%s, %s, %s, 'Available', 'Active')
            """, (name, selected['role_name'], selected['default_salary']))
            conn.commit()
            print(f"\n[SUCCESS] {name} hired as {selected['role_name']}.")
        else:
            print("[!] Invalid Role.")
            
    except OperationCancelled: pass
    except Exception as e: print(f"[ERROR] {e}")
    conn.close()
