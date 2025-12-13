import time
from db_config import get_db_connection, clear_screen, pause, get_valid_input, OperationCancelled

def menu():
    while True:
        clear_screen()
        print("--- [G4] CREW MANAGEMENT (SECURE) ---")
        print("1. View Crew Roster")
        print("2. Assign Crew to Flight (Batch Mode)")
        print("3. View Assignments")
        print("4. Payroll System") 
        print("5. Manage License Status")
        print("6. Deploy or Add New Crew Member")
        print("7. Reassign Role")  
        print("8. Manage Job Roles")    
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")
        
        if choice == '1': view_crew(); pause()
        elif choice == '2': assign_crew() 
        elif choice == '3': view_assignments(); pause()
        elif choice == '4': view_payroll() 
        elif choice == '5': manage_certifications(); pause()
        elif choice == '6': add_crew(); pause()
        elif choice == '7': reassign_role(); pause()
        elif choice == '8': manage_job_roles()
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
    print(f"\n{'ID':<5} {'NAME':<20} {'ROLE':<20} {'LICENSE':<10} {'STATUS'}")
    print("-" * 75)
    for c in cursor.fetchall():
        lic = c.get('license_status', 'Active')
        role_display = c['role'] if c['role'] else "Unknown"
        print(f"{c['crew_id']:<5} {c['name']:<20} {role_display:<20} {lic:<10} {c['status']}")
    conn.close()

# --- 2. ASSIGN CREW (WITH UNIVERSAL BACK/CANCEL) ---
def assign_crew():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    while True: 
        clear_screen()
        print("--- ASSIGN CREW TO FLIGHT ---")
        
        try:
            # STEP 1: Select Flight
            cursor.execute("SELECT flight_id, flight_number, destination FROM flights WHERE status='Scheduled'")
            flights = cursor.fetchall()
            
            if not flights:
                print("[!] No scheduled flights found.")
                input("Press Enter to return..."); return

            valid_flight_ids = []
            for f in flights: 
                valid_flight_ids.append(f['flight_id'])
                print(f"ID {f['flight_id']} | {f['flight_number']} to {f['destination']}")
            
            print("\n[0] Back to G4 Menu")
            fid_input = input("Enter Flight ID: ")
            if fid_input == '0': return # <--- BACK OPTION 1
            
            if not fid_input.isdigit() or int(fid_input) not in valid_flight_ids:
                print("[!] Invalid Flight ID.")
                time.sleep(1); continue 

            fid = int(fid_input)

            # STEP 2: Define Mission Profile
            print("\n--- DEFINE CREW COMPOSITION ---")
            print("(Enter 0 to skip a role, or type 'cancel' to exit)")
            requirements = []
            
            def get_qty(prompt):
                val = input(prompt)
                if val.lower() == 'cancel': raise OperationCancelled
                return int(val) if val.isdigit() else 0

            try:
                # We catch the 'cancel' keyword here
                qty_cap = get_qty("How many Captains? ")
                if qty_cap > 0: requirements.append(('Captain', qty_cap))
                
                qty_fo = get_qty("How many First Officers? ")
                if qty_fo > 0: requirements.append(('First Officer', qty_fo))
                
                qty_fa = get_qty("How many Flight Attendants? ")
                if qty_fa > 0: requirements.append(('Flight Attendant', qty_fa))
            
            except OperationCancelled:
                print("\n[!] Process Cancelled.")
                return # <--- BACK OPTION 2

            # Strict Loop for Optional Roles
            while True:
                spec_choice = input("\nAdd specialized role (e.g. Purser/Nurse)? (Y/N) [0 to Cancel]: ").strip().upper()
                
                if spec_choice == '0':
                    print("\n[!] Process Cancelled.")
                    return # <--- BACK OPTION 3
                
                if spec_choice == 'Y':
                    spec_role = input("Enter Role Name (e.g. Purser): ").strip()
                    try:
                        spec_qty = int(input(f"How many {spec_role}s? "))
                        if spec_qty > 0: requirements.append((spec_role, spec_qty))
                    except ValueError: pass
                    break 
                elif spec_choice == 'N':
                    break 
                else:
                    print("[!] Invalid input. Type 'Y', 'N', or '0' to Cancel.")
            
            if not requirements:
                print("[!] No crew requested. Assignment cancelled.")
                time.sleep(1); continue

            # STEP 3: PRE-VALIDATION
            print("\n[SYSTEM] Checking Roster Availability...")
            time.sleep(0.5)
            
            check_failed = False
            for role_name, required_qty in requirements:
                cursor.execute(
                    "SELECT COUNT(*) as cnt FROM crew WHERE role LIKE %s AND status='Available' AND license_status='Active'", 
                    (role_name,)
                )
                res = cursor.fetchone()
                available_qty = res['cnt']
                
                if available_qty < required_qty:
                    check_failed = True
                    print(f"\n[!] ERROR: Insufficient {role_name}s.")
                    print(f"    Required: {required_qty} | Available: {available_qty}")
                    if available_qty == 0:
                        print(f"    [!] ALERT: Role '{role_name}' is not deployed/available.")
            
            if check_failed:
                print("\n[!] SYSTEM HALT: Not enough crew.")
                input("Press Enter to modify requirements..."); continue 
            
            # STEP 4: SELECTION LOOP (With Cancel Logic)
            print("\n[SYSTEM] Roster confirmed. Proceeding to selection...")
            
            pending_assignments = [] 
            session_chosen_ids = [] 
            
            for role_name, quantity in requirements:
                for i in range(1, quantity + 1):
                    cursor.execute("SELECT * FROM crew WHERE role LIKE %s AND status='Available' AND license_status='Active'", (role_name,))
                    candidates = cursor.fetchall()
                    
                    print(f"\n--- SELECTING {role_name.upper()} #{i} of {quantity} ---")
                    valid_ids = []
                    
                    candidates_found = False
                    for c in candidates:
                        if c['crew_id'] not in session_chosen_ids:
                            valid_ids.append(c['crew_id'])
                            print(f"ID {c['crew_id']}: {c['name']}")
                            candidates_found = True
                    
                    if not candidates_found:
                        print(f"[!] CRITICAL ERROR: Run out of unique {role_name}s.")
                        raise Exception("Duplicate selection prevention.")

                    while True:
                        # THE KEY CANCEL OPTION
                        user_in = input(f"Enter Crew ID for {role_name} [0 to Cancel]: ")
                        
                        if user_in == '0':
                            print("\n[!] ABORTING... No changes were saved.")
                            return # <--- BACK OPTION 4 (Exits entire function)

                        if user_in.isdigit():
                            cid = int(user_in)
                            if cid in valid_ids:
                                pending_assignments.append(cid)
                                session_chosen_ids.append(cid)
                                print(f"[OK] {role_name} selected.")
                                break
                            else:
                                print(f"[!] Invalid ID. Please pick from the list.")
                        else:
                            print("[!] Enter a number.")

            # STEP 5: FINAL COMMIT
            print("\n[SYSTEM] Finalizing Assignments...")
            for cid in pending_assignments:
                cursor.execute("INSERT INTO flight_crew (flight_id, crew_id) VALUES (%s, %s)", (fid, cid))
                cursor.execute("UPDATE crew SET status = 'On-Duty', flight_hours = flight_hours + 4 WHERE crew_id = %s", (cid,))
            
            conn.commit()
            print("\n[SUCCESS] Flight Crew Assembly Finalized and Saved.")
            input("Press Enter to continue...")
            return 

        except Exception as e:
            print(f"\n[ERROR] Process Aborted: {e}")
            input("Press Enter...")
            return
    
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
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM crew WHERE crew_id = %s", (cid,))
        if not cursor.fetchone():
            print("[!] Crew ID not found.")
            pause(); return

        rate = get_valid_input("Enter New Rate", int)
        cursor.execute("UPDATE crew SET salary_rate = %s WHERE crew_id = %s", (rate, cid))
        conn.commit()
        print("[SUCCESS] Salary Updated.")
        pause()
    except OperationCancelled: pass

# --- 5. MANAGE LICENSE ---
def manage_certifications():
    view_crew()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cid = get_valid_input("\nEnter Crew ID to update", int)
        
        cursor.execute("SELECT status, name FROM crew WHERE crew_id = %s", (cid,))
        crew = cursor.fetchone()
        
        if not crew:
            print("[!] Error: Crew ID not found.")
            conn.close(); return

        if crew['status'] == 'On-Duty':
            print(f"[!] SAFETY ALERT: Cannot change license while {crew['name']} is On-Duty.")
            conn.close(); return

        print("[1] Active  [2] Expired  [3] Suspended")
        opt = get_valid_input("Select License Status")
        status_map = {'1': 'Active', '2': 'Expired', '3': 'Suspended'}
        
        if opt in status_map:
            cursor.execute("UPDATE crew SET license_status = %s WHERE crew_id = %s", (status_map[opt], cid))
            conn.commit()
            print("[SUCCESS] License Status Updated.")
        else:
            print("[!] Invalid Option.")
            
    except OperationCancelled: print("\n[!] Cancelled.")
    conn.close()

# --- 6. DEPLOY/ADD CREW ---
def add_crew():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    print("\n--- DEPLOY NEW CREW MEMBER ---")
    try:
        name = get_valid_input("Enter Full Name")
        
        print("\nSelect Job Role:")
        cursor.execute("SELECT * FROM crew_roles")
        roles = cursor.fetchall()
        valid_role_ids = []
        
        for r in roles:
            valid_role_ids.append(r['role_id'])
            print(f"[{r['role_id']}] {r['role_name']}")
        
        while True:
            rid = get_valid_input("Select Role ID", int)
            if rid in valid_role_ids: break
            print("[!] Invalid Role Selection.")

        selected = next((r for r in roles if r['role_id'] == rid), None)
        
        salary = get_valid_input(f"Enter Salary Rate for {name}", int)
        
        cursor.execute("""
            INSERT INTO crew (name, role, salary_rate, status, license_status) 
            VALUES (%s, %s, %s, 'Available', 'Active')
        """, (name, selected['role_name'], salary))
        conn.commit()
        print(f"\n[SUCCESS] {name} deployed as {selected['role_name']} with rate ₱{salary:,}.")
            
    except OperationCancelled: print("\n[!] Cancelled.")
    except Exception as e: print(f"[ERROR] {e}")
    conn.close()

# --- 7. REASSIGN ROLE ---
def reassign_role():
    view_crew()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cid = get_valid_input("\nEnter Crew ID to Reassign", int)
        
        cursor.execute("SELECT name, status, role FROM crew WHERE crew_id = %s", (cid,))
        crew = cursor.fetchone()
        
        if not crew:
            print("[!] Crew ID not found."); conn.close(); return

        if crew['status'] == 'On-Duty':
            print(f"[!] SAFETY ALERT: Cannot reassign while {crew['name']} is On-Duty."); conn.close(); return

        current_role = crew['role']
        print(f"\nCurrent Role: {current_role}")
        
        # --- HIERARCHY LOGIC ---
        flight_deck = ['Captain', 'First Officer', 'Second Officer', 'Flight Engineer']
        
        is_flight_deck = current_role in flight_deck
        
        if is_flight_deck:
            print("Category: FLIGHT DECK (Cockpit Crew Only)")
            cursor.execute("SELECT * FROM crew_roles WHERE role_name IN ('Captain', 'First Officer', 'Second Officer', 'Flight Engineer')")
        else:
            print("Category: CABIN SERVICE (Cabin & Support Crew Only)")
            cursor.execute("SELECT * FROM crew_roles WHERE role_name NOT IN ('Captain', 'First Officer', 'Second Officer', 'Flight Engineer')")

        roles = cursor.fetchall()
        valid_role_ids = []
        
        for r in roles:
            valid_role_ids.append(r['role_id'])
            print(f"[{r['role_id']}] {r['role_name']}")
            
        while True:
            rid = get_valid_input("Select New Role ID", int)
            if rid in valid_role_ids: break
            print("[!] Invalid Selection. You can only swap within the same category.")

        selected = next((r for r in roles if r['role_id'] == rid), None)
        
        cursor.execute("UPDATE crew SET role = %s WHERE crew_id = %s", (selected['role_name'], cid))
        conn.commit()
        print(f"\n[SUCCESS] Role changed to {selected['role_name']}.")
            
    except OperationCancelled: print("\n[!] Cancelled.")
    except Exception as e: print(f"[ERROR] {e}")
    conn.close()

def manage_job_roles():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    while True:
        clear_screen()
        print("\n--- JOB ROLES DATABASE ---")
        cursor.execute("SELECT * FROM crew_roles")
        roles = cursor.fetchall()
        
        print(f"{'ID':<5} {'ROLE NAME':<20}")
        print("-" * 45)
        for r in roles:
            print(f"{r['role_id']:<5} {r['role_name']:<20}")
            
        print("\n[1] Add New Role (e.g. Flight Nurse)")
        print("[0] Back")
        
        choice = input("\nSelect: ")
        
        if choice == '1':
            try:
                name = get_valid_input("Enter New Role Name")
                cursor.execute("INSERT INTO crew_roles (role_name, default_salary) VALUES (%s, 0)", (name,))
                conn.commit()
                print(f"\n[SUCCESS] Role '{name}' added.")
                pause()
            except Exception as e:
                if "Duplicate entry" in str(e): print(f"[!] Error: Role '{name}' already exists.")
                else: print(f"[ERROR] {e}")
                pause()
        elif choice == '0': break
        else:
            print("[!] Invalid Selection.")
            pause()
    conn.close()
