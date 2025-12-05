from db_config import get_db_connection, clear_screen, pause, get_valid_input, OperationCancelled

def menu():
    while True:
        clear_screen()
        print("--- [G6] CUSTOMER MANAGEMENT & SUPPORT ---")
        print("1. View Top Customers (Loyalty)")
        print("2. Customer Support Portal (File Complaint)") 
        print("3. Support Desk (Admin View)")               
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")
        
        if choice == '1': view_customers(); pause()
        elif choice == '2': file_complaint(); pause()
        elif choice == '3': support_desk(); pause()
        elif choice == '0': break

def view_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("UPDATE passengers SET tier = 'Gold' WHERE loyalty_points > 10000")
    cursor.execute("UPDATE passengers SET tier = 'Silver' WHERE loyalty_points BETWEEN 5000 AND 10000")
    conn.commit()
    
    cursor.execute("SELECT * FROM passengers ORDER BY loyalty_points DESC")
    print(f"\n{'ID':<5} {'NAME':<20} {'POINTS':<10} {'TIER'}")
    print("-" * 50)
    for p in cursor.fetchall():
        print(f"{p['passenger_id']:<5} {p['name']:<20} {p['loyalty_points']:<10} {p['tier']}")
    conn.close()

def file_complaint():
    print("\n--- CUSTOMER SERVICE PORTAL ---")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        email = get_valid_input("Enter Passenger Email")
        cursor.execute("SELECT passenger_id, name FROM passengers WHERE email = %s", (email,))
        p = cursor.fetchone()
        
        if not p:
            print("[!] Email not found. Please register first.")
            return

        print(f"Hello, {p['name']}. How can we help?")
        print("[1] Complaint  [2] Inquiry  [3] Feedback")
        cat_opt = get_valid_input("Select Category")
        category = "Complaint" if cat_opt == '1' else "Inquiry" if cat_opt == '2' else "Feedback"
        
        message = get_valid_input("Please describe your concern")
        
        cursor.execute("INSERT INTO feedback (passenger_id, category, message) VALUES (%s, %s, %s)", 
                       (p['passenger_id'], category, message))
        conn.commit()
        print("\n[SUCCESS] Your ticket has been submitted to our Support Desk.")
        
    except OperationCancelled:
        print("\n[!] Cancelled.")
    except Exception as e:
        print(f"[ERROR] {e}")
    conn.close()

def support_desk():
    print("\n--- SUPPORT DESK DASHBOARD ---")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT f.feedback_id, p.name, f.category, f.message, f.status 
        FROM feedback f JOIN passengers p ON f.passenger_id = p.passenger_id
        WHERE f.status = 'Open'
    """)
    tickets = cursor.fetchall()
    
    if not tickets:
        print("[OK] No open tickets.")
        conn.close()
        return

    print(f"{'ID':<5} {'PASSENGER':<20} {'CATEGORY':<10} {'MESSAGE'}")
    print("-" * 60)
    for t in tickets:
        print(f"{t['feedback_id']:<5} {t['name']:<20} {t['category']:<10} {t['message']}")
        
    print("\n[1] Resolve Ticket")
    print("[0] Back")
    
    try:
        opt = input("\nSelect: ")
        if opt == '1':
            tid = get_valid_input("Enter Ticket ID to Close", int)
            cursor.execute("UPDATE feedback SET status = 'Resolved' WHERE feedback_id = %s", (tid,))
            conn.commit()
            print("[SUCCESS] Ticket marked as Resolved.")
    except Exception as e:
        print(f"[ERROR] {e}")
    conn.close()
