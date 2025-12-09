from db_config import get_db_connection, clear_screen, pause, get_valid_input, OperationCancelled
import random
import string
import time

# -----------------------------------------------
# NEW: Email domain validator
# -----------------------------------------------
EMAIL_DOMAINS = [
    "@gmail.com",
    "@yahoo.com",
    "@hotmail.com",
    "@outlook.com",
    "@icloud.com"
]

CLASSES = ["ECONOMY", "BUSINESS"]
def is_valid_email_domain(email):
    return any(email.endswith(domain) for domain in EMAIL_DOMAINS)



def is_valid_class(cls):
    return cls.upper() in CLASSES


def menu():
    while True:
        clear_screen()
        print("--- [G2] RESERVATION SYSTEM ---")
        print("1. Book a Ticket")
        print("2. View My Bookings")
        print("3. Cancel a Booking") 
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")
        
        if choice == '1': book_ticket(); pause()
        elif choice == '2': view_my_bookings(); pause()
        elif choice == '3': cancel_booking(); pause()
        elif choice == '0': break


def show_seat_map(conn, flight_id):
    print("\n" + "="*22 + " SEAT MAP " + "="*22)
    print("      [A] [B] [C]     [D] [E] [F]") 

    cursor = conn.cursor()
    cursor.execute("SELECT seat_number FROM bookings WHERE flight_id = %s AND status = 'Confirmed'", (flight_id,))
    taken = [row[0] for row in cursor.fetchall()] 
    
    rows = 30
    cols = ['A', 'B', 'C', 'D', 'E', 'F']
    valid_seat_codes = [] 
    
    for r in range(1, rows + 1):
        row_str = f"{r:<2}" 
        line = f"Row {row_str}| "
        
        for i, c in enumerate(cols):
            seat_code = f"{r}{c}"
            valid_seat_codes.append(seat_code)
            
            if seat_code in taken:
                marker = "[X]"
            else:
                marker = "[ ]"
            
            line += f"{marker} "
            if i == 2:
                line += "    "
        
        print(line)
        
    print("="*54)
    print("Legend: [ ] = Available, [X] = Taken")
    return taken, valid_seat_codes

def get_valid_name(prompt):
    while True:
        name = input(f"{prompt}: ").strip()
        if all(c.isalpha() or c.isspace() for c in name) and name != "":
            return name
        else:
            print("Invalid input. Please enter letters and spaces only.")

def book_ticket():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        while True:
            email = get_valid_input("\nEnter Passenger Email", "email")

            if not is_valid_email_domain(email):
                print("\n[!] ERROR: Email domain not allowed.")
                print("    Allowed domains:")
                for d in EMAIL_DOMAINS:
                    print("   -", d)
                continue

            break
        
        cursor.execute("SELECT * FROM passengers WHERE email = %s", (email,))
        p = cursor.fetchone()
        
        if p:
            print(f"Welcome back, {p['name']} (Tier: {p['tier']})")
            pid = p['passenger_id']
            p_name = p['name']
        else:
            print("New Passenger Detected.")
            p_name = get_valid_name("Full Name")
            cursor.execute("INSERT INTO passengers (name, email) VALUES (%s, %s)", (p_name, email))
            conn.commit()
            pid = cursor.lastrowid

        cursor.execute("SELECT flight_id, flight_number, destination, flight_date FROM flights WHERE status='Scheduled'")
        flights = cursor.fetchall()

        print("\n--- AVAILABLE FLIGHTS ---")
        for f in flights:
            print(f"ID {f['flight_id']} | {f['flight_number']} to {f['destination']} on {f['flight_date']}")
        
        while True:
            fid = get_valid_input("\nEnter Flight ID", int)

            cursor.execute("SELECT * FROM flights WHERE flight_id = %s", (fid,))
            flight = cursor.fetchone()

            if not flight:
                print("[!] Error: Flight ID not found.")
                continue

            if flight["status"] != "Scheduled":
                print(f"[!] Error: Flight {flight['flight_number']} is NOT scheduled.")
                print("    Current status:", flight["status"])
                continue

            break  

        taken_seats, valid_codes = show_seat_map(conn, fid)
        
        while True:
            seat = get_valid_input("Select Seat (e.g. 10A)").upper()
            
            if seat not in valid_codes:
                print(f"   [!] Error: Seat '{seat}' does not exist. Example: 12A")
                continue
            if seat in taken_seats:
                print(f"   [!] Error: Seat '{seat}' is already taken.")
                continue
            break 
        
        while True:
            seat_class = get_valid_input("Class (Economy/Business)").upper()
            if not is_valid_class(seat_class):
                print("\n[!] Invalid class. Allowed:")
                print("   - Economy\n   - Business")
                continue
            break

        seat_class = seat_class.title()
        price = 5000 if seat_class == "Economy" else 15000
        
        print("\n" + "="*40)
        print(f"   SECURE PAYMENT GATEWAY (₱{price:,.2f})")
        print("="*40)
        
        while True:
            card = get_valid_input("Enter Credit Card Number (16 digits)")
            if len(card) == 16 and card.isdigit():
                break
            print("   [!] Invalid card format.")

        while True:
            cvv = get_valid_input("Enter CVV (3-4 digits)")
            if (len(cvv) == 3 or len(cvv) == 4) and cvv.isdigit():
                break
            print("   [!] Invalid CVV format.")
        
        print("\nContacting Bank...", end="", flush=True)
        time.sleep(1)
        print(" Authorized.")
        print(f"[SUCCESS] Payment of ₱{price} Received.")
        print("="*40)

        pnr = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        cursor.execute("""
            INSERT INTO bookings (pnr, flight_id, passenger_id, seat_class, seat_number, price, status) 
            VALUES (%s, %s, %s, %s, %s, %s, 'Confirmed')
        """, (pnr, fid, pid, seat_class, seat, price))
        
        points = int(price * 0.10)
        cursor.execute("UPDATE passengers SET loyalty_points = loyalty_points + %s WHERE passenger_id = %s", (points, pid))
        
        conn.commit()
        
        print("\n" + "="*50)
        print("       ELECTRONIC TICKET RECEIPT")
        print("="*50)
        print(f" PNR REF:   {pnr}")
        print(f" PASSENGER: {p_name}")
        print(f" FLIGHT ID: {fid}")
        print(f" SEAT:      {seat} ({seat_class})")
        print(f" PRICE:     ₱{price:,.2f}")
        print(f" STATUS:    CONFIRMED")
        print("="*50)
        
    except OperationCancelled:
        print("\n[!] Booking Process Cancelled.")
    except Exception as e:
        print(f"[ERROR] Booking Failed: {e}")
    finally:
        conn.close()


def view_my_bookings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        email = get_valid_input("\nEnter your Email to view bookings", 'email')
        
        query = """
            SELECT b.pnr, f.flight_number, f.origin, f.destination, f.flight_date, b.seat_number, b.status
            FROM bookings b
            JOIN passengers p ON b.passenger_id = p.passenger_id
            JOIN flights f ON b.flight_id = f.flight_id
            WHERE p.email = %s
        """
        cursor.execute(query, (email,))
        bookings = cursor.fetchall()
        
        if not bookings:
            print("\n[!] No bookings found for this email.")
        else:
            print(f"\n--- BOOKINGS FOR {email} ---")
            print(f"{'PNR':<8} {'FLIGHT':<8} {'ROUTE':<20} {'DATE':<12} {'SEAT':<6} {'STATUS'}")
            print("-" * 70)
            for b in bookings:
                print(f"{b['pnr']:<8} {b['flight_number']:<8} "
                      f"{b['origin']}->{b['destination']:<16} {str(b['flight_date']):<12} "
                      f"{b['seat_number']:<6} {b['status']}")
        
    except OperationCancelled:
        print("\n[!] Cancelled.")
    finally:
        conn.close()

def cancel_booking():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        print("\n--- CANCEL BOOKING ---")
        email = get_valid_input("\nEnter Passenger Email", 'email')

        cursor.execute("SELECT * FROM passengers WHERE email = %s", (email,))
        passenger = cursor.fetchone()
        if not passenger:
            print("\n[!] Passenger not found.")
            return

        pid = passenger['passenger_id']
        print(f"Passenger found: {passenger['name']}")

        cursor.execute("""
            SELECT b.pnr, b.status, f.flight_number, f.origin, f.destination, f.flight_date
            FROM bookings b
            JOIN flights f ON b.flight_id = f.flight_id
            WHERE b.passenger_id = %s AND b.status = 'Confirmed'
            ORDER BY f.flight_date ASC
        """, (pid,))
        rows = cursor.fetchall()

        if not rows:
            print("\n[!] No ACTIVE bookings to cancel for this passenger.")
            return
        
        print("\n--- ACTIVE BOOKINGS ---")
        print(f"{'PNR':<8} {'FLIGHT':<8} {'ROUTE':<22} {'DATE'}")
        print("-" * 60)

        for r in rows:
            print(f"{r['pnr']:<8} {r['flight_number']:<8} "
                  f"{r['origin']}->{r['destination']:<15} {r['flight_date']}")

        pnr = get_valid_input("\nEnter PNR to cancel").upper()

        cursor.execute("SELECT * FROM bookings WHERE pnr = %s AND passenger_id = %s", (pnr, pid))
        booking = cursor.fetchone()

        if not booking:
            print("\n[!] Invalid PNR for this email.")
            return
        confirm = get_valid_input(f"Cancel booking {pnr}? (Y/N)").upper()
        if confirm != 'Y':
            print("\n[!] Cancellation aborted.")
            return
        cursor.execute("UPDATE bookings SET status = 'Cancelled' WHERE pnr = %s", (pnr,))
        conn.commit()

        print(f"\n[SUCCESS] Booking {pnr} has been CANCELLED.")
    except OperationCancelled:
        print("\n[!] Process cancelled.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()
