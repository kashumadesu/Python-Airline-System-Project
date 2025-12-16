import time
from db_config import get_db_connection, clear_screen, pause, get_valid_input, OperationCancelled

def menu():
    while True:
        clear_screen()
        print("--- [G6] PASSENGER RELATIONS & SUPPORT DESK ---")
        print("1. Manage Passengers (View/Add/Edit)")
        print("2. SUPPORT DESK (Complaints & Inquiries)") 
        print("0. Back to Main Menu")
        
        choice = input("\nSelect: ")
        
        if choice == '1': passenger_menu()
        elif choice == '2': support_desk_menu()
        elif choice == '0': 
            print("Returning to Main Menu...")
            time.sleep(1)
            break
        else:
            print("[!] Invalid Selection")
            pause()

# ==========================================
#      PART 1: PASSENGER MANAGEMENT
# ==========================================
def passenger_menu():
    while True:
        clear_screen()
        print("--- PASSENGER MANAGEMENT ---")
        print("1. View All Passengers")
        print("2. Add New Passenger")
        print("3. Edit Passenger Details")
        print("0. Back")
        
        choice = input("\nSelect: ")
        if choice == '1': view_passengers()
        elif choice == '2': add_passenger()
        elif choice == '3': edit_passenger()
        elif choice == '0': return
        else: print("[!] Invalid."); pause()

def view_passengers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM passengers")
        passengers = cursor.fetchall()
        
        if not passengers:
            print("[!] No passengers found.")
            return 

        print(f"\n{'ID':<5} {'NAME':<30} {'EMAIL':<30} {'TIER'}")
        print("-" * 75)
        for p in passengers:
            # Handle potential None values safely
            p_name = p['name'] if p['name'] else "Unknown"
            p_email = p['email'] if p['email'] else "No Email"
            p_tier = p['tier'] if p['tier'] else "Blue"
            print(f"{p['passenger_id']:<5} {p_name:<30} {p_email:<30} {p_tier}")
        
        print("\n[Enter Passenger ID to View Profile & History]")
        print("[0] Back")
        
        pid_input = input("Select ID: ")
        if pid_input == '0': return
        
        if pid_input.isdigit():
            view_single_profile(int(pid_input), conn) 
        else:
            print("[!] Invalid ID.")
            
    except Exception as e: print(f"[!] Error: {e}")
    finally: conn.close()

def view_single_profile(pid, conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM passengers WHERE passenger_id = %s", (pid,))
    p = cursor.fetchone()
    
    if not p:
        print("[!] Passenger not found."); pause(); return

    while True:
        clear_screen()
        print(f"--- PROFILE: {p['name']} ---")
        print(f"ID:     {p['passenger_id']}")
        print(f"Email:  {p['email']}")
        print(f"Phone:  {p['phone']}")
        print(f"Tier:   {p['tier']}")
        print(f"Points: {p['loyalty_points']}")
        
        print("\n--- ACTIONS ---")
        print("[1] Edit Contact Info")
        print("[2] View Support History (Complaints/Logs)") 
        print("[0] Back to List")
        
        choice = input("\nSelect: ")
        if choice == '1': 
            conn.close() 
            edit_passenger_direct(pid)
            return
        elif choice == '2':
            view_passenger_logs(pid)
        elif choice == '0': return

def add_passenger():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("\n--- REGISTER NEW PASSENGER ---")
    try:
        name = get_valid_input("Full Name")
        email = get_valid_input("Email")
        phone = get_valid_input("Phone")
        
        # Insert defaults for Tier (Blue) and Points (0)
        cursor.execute("INSERT INTO passengers (name, email, phone, tier, loyalty_points) VALUES (%s, %s, %s, 'Blue', 0)", 
                       (name, email, phone))
        conn.commit()
        print(f"\n[SUCCESS] Passenger {name} added!")
    except Exception as e: print(f"[ERROR] {e}")
    finally: conn.close(); pause()

def edit_passenger_direct(pid):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        new_email = get_valid_input("Enter New Email")
        cursor.execute("UPDATE passengers SET email = %s WHERE passenger_id = %s", (new_email, pid))
        conn.commit()
        print("[SUCCESS] Updated.")
    except Exception as e: print(f"[ERROR] {e}")
    finally: conn.close(); pause()

def edit_passenger():
    print("Please use 'View All Passengers' to select a profile to edit."); pause()

# ==========================================
#      PART 2: SUPPORT DESK (ADAPTED)
# ==========================================
def support_desk_menu():
    while True:
        clear_screen()
        print("--- SUPPORT DESK & TICKETING SYSTEM ---")
        print("1. File New Case (Complaint/Inquiry)")
        print("2. Search Case by SERIAL ID (View Logs/Update)") 
        print("3. View All Active Cases")
        print("0. Back")
        
        choice = input("\nSelect: ")
        
        if choice == '1': file_new_case()
        elif choice == '2': manage_case_by_id()
        elif choice == '3': view_all_cases()
        elif choice == '0': return
        else: print("[!] Invalid."); pause()

def file_new_case():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    print("\n--- FILE NEW SUPPORT CASE ---")
    
    try:
        # Step 1: Link to Passenger
        pid_input = input("Enter Passenger ID (or 0 to cancel): ")
        if pid_input == '0': return
        
        cursor.execute("SELECT name FROM passengers WHERE passenger_id = %s", (pid_input,))
        p = cursor.fetchone()
        if not p:
            print("[!] Passenger not found."); pause(); return
            
        print(f"Selected: {p['name']}")
        
        # Step 2: Categorize
        print("\nCategories: [1] Complaint  [2] Inquiry  [3] Feedback  [4] Refund")
        cat_map = {'1': 'Complaint', '2': 'Inquiry', '3': 'Feedback', '4': 'Refund Request'}
        cat_opt = input("Select Category: ")
        if cat_opt not in cat_map: print("[!] Invalid category."); pause(); return
        category = cat_map[cat_opt]
        
        # Step 3: Subject
        subject = get_valid_input("Subject / Issue Summary")
        
        # Step 4: Save
        cursor.execute("INSERT INTO support_cases (passenger_id, category, subject, status) VALUES (%s, %s, %s, 'Open')", 
                       (pid_input, category, subject))
        conn.commit()
        
        case_id = cursor.lastrowid
        
        # Create Initial Log
        cursor.execute("INSERT INTO case_logs (case_id, log_note) VALUES (%s, 'Case created manually by Admin.')", (case_id,))
        conn.commit()
        
        print(f"\n[SUCCESS] Case Filed! SERIAL NUMBER: #{case_id}")
        
    except Exception as e: print(f"[ERROR] {e}")
    finally: conn.close(); pause()

def manage_case_by_id():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        case_id = input("\nEnter Case / Serial ID to Search (0 to Back): ")
        if case_id == '0': return
        if not case_id.isdigit(): print("[!] Invalid ID format."); pause(); return
        
        # Query Case + Passenger Name
        query = """
            SELECT s.*, p.name 
            FROM support_cases s
            JOIN passengers p ON s.passenger_id = p.passenger_id
            WHERE s.case_id = %s
        """
        cursor.execute(query, (case_id,))
        case = cursor.fetchone()
        
        if not case:
            print("[!] Case ID not found."); pause(); return
            
        while True:
            clear_screen()
            print(f"--- CASE #{case['case_id']} DETAILS ---")
            print(f"Passenger: {case['name']}")
            print(f"Category:  {case['category']}")
            print(f"Subject:   {case['subject']}")
            print(f"Status:    {case['status'].upper()}")
            print(f"Filed On:  {case['created_at']}")
            
            print("\n--- CASE LOGS & NOTES ---")
            cursor.execute("SELECT * FROM case_logs WHERE case_id = %s ORDER BY log_date ASC", (case_id,))
            logs = cursor.fetchall()
            if not logs: print("   (No logs yet)")
            for log in logs:
                print(f"   [{log['log_date']}] {log['log_note']}")
            
            print("\n--- ACTIONS ---")
            print("[1] Add Note / Update Log")
            print("[2] Change Status (Open/Closed)")
            print("[0] Back")
            
            choice = input("\nSelect: ")
            
            if choice == '1':
                note = get_valid_input("Enter Note")
                cursor.execute("INSERT INTO case_logs (case_id, log_note) VALUES (%s, %s)", (case_id, note))
                conn.commit()
                print("[OK] Log Added.")
                time.sleep(1)
                
            elif choice == '2':
                print("Status: [1] Open  [2] In Progress  [3] Resolved  [4] Closed")
                s_map = {'1': 'Open', '2': 'In Progress', '3': 'Resolved', '4': 'Closed'}
                s_opt = input("Select New Status: ")
                if s_opt in s_map:
                    new_status = s_map[s_opt]
                    cursor.execute("UPDATE support_cases SET status = %s WHERE case_id = %s", (new_status, case_id))
                    
                    log_msg = f"*** Status changed to {new_status} ***"
                    cursor.execute("INSERT INTO case_logs (case_id, log_note) VALUES (%s, %s)", (case_id, log_msg))
                    conn.commit()
                    
                    case['status'] = new_status
                    print("[OK] Status Updated.")
                    time.sleep(1)
            
            elif choice == '0': break

    except Exception as e: print(f"[ERROR] {e}")
    finally: conn.close()

def view_all_cases():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT s.case_id, p.name, s.category, s.status, s.subject 
            FROM support_cases s
            JOIN passengers p ON s.passenger_id = p.passenger_id
            ORDER BY s.case_id DESC
        """)
        cases = cursor.fetchall()
        
        print(f"\n{'ID':<5} {'PASSENGER':<25} {'CATEGORY':<12} {'STATUS':<12} {'SUBJECT'}")
        print("-" * 80)
        for c in cases:
            print(f"{c['case_id']:<5} {c['name']:<25} {c['category']:<12} {c['status']:<12} {c['subject']}")
        
        print("\n(Use Option 2 in menu to manage specific cases)")
    
    except Exception as e: print(f"[ERROR] {e}")
    finally: conn.close(); pause()

def view_passenger_logs(pid):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        print("\n--- PASSENGER SUPPORT HISTORY ---")
        cursor.execute("SELECT * FROM support_cases WHERE passenger_id = %s", (pid,))
        cases = cursor.fetchall()
        
        if not cases:
            print("No cases found for this passenger.")
        else:
            for c in cases:
                print(f"CASE #{c['case_id']} | {c['category']} | {c['status']} | {c['subject']}")
                cursor.execute("SELECT log_note FROM case_logs WHERE case_id = %s ORDER BY log_date DESC LIMIT 1", (c['case_id'],))
                last_log = cursor.fetchone()
                if last_log:
                    print(f"   Latest Note: {last_log['log_note']}")
                print("-" * 40)
                
    except Exception as e:
        print(f"[!] Error loading logs: {e}")
    finally:
        if conn: conn.close()
        pause()
