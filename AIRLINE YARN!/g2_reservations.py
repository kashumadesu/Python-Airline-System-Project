from db_config import get_db_connection, clear_screen, pause, get_valid_input, OperationCancelled
import random
import string
import time

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

def get_valid_name(prompt):
    while True:
        name = input(f"{prompt}: ").strip()
        if all(c.isalpha() or c.isspace() for c in name) and name:
            return name
        print("Invalid name. Letters and spaces only.")

def menu():
    while True:
        clear_screen()
        print("--- [G2] RESERVATION & TICKETING SYSTEM ---")
        print("1. Book a Ticket")
        print("2. View My Bookings")
        print("3. Cancel a Booking")
        print("4. Upgrade Booking Class")
        print("5. Check-in for Flight")
        print("0. Back to Main Menu")

        choice = input("\nSelect: ")

        if choice == '1': book_ticket(); pause()
        elif choice == '2': view_my_bookings(); pause()
        elif choice == '3': cancel_booking(); pause()
        elif choice == '4': upgrade_booking(); pause()
        elif choice == '5': check_in(); pause()
        elif choice == '0': break

def show_seat_map(conn, flight_id):
    print("\n" + "="*22 + " SEAT MAP " + "="*22)
    print("      [A] [B] [C]     [D] [E] [F]")

    cursor = conn.cursor()
    cursor.execute(
        "SELECT seat_number FROM bookings WHERE flight_id=%s AND status='Confirmed'",
        (flight_id,)
    )
    taken = [row[0] for row in cursor.fetchall()]

    rows = 30
    cols = ['A','B','C','D','E','F']
    valid_codes = []

    for r in range(1, rows+1):
        line = f"Row {r:<2}| "
        for i,c in enumerate(cols):
            seat = f"{r}{c}"
            valid_codes.append(seat)
            line += "[X] " if seat in taken else "[ ] "
            if i == 2:
                line += "   "
        print(line)

    print("="*54)
    return taken, valid_codes

def book_ticket():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        while True:
            email = get_valid_input("Enter Passenger Email", "email")
            if is_valid_email_domain(email):
                break
            print("[!] Invalid email domain.")

        cursor.execute("SELECT * FROM passengers WHERE email=%s", (email,))
        passenger = cursor.fetchone()

        if passenger:
            pid = passenger['passenger_id']
            pname = passenger['name']
        else:
            pname = get_valid_name("Full Name")
            cursor.execute(
                "INSERT INTO passengers (name, email) VALUES (%s,%s)",
                (pname, email)
            )
            conn.commit()
            pid = cursor.lastrowid

        cursor.execute(
            "SELECT flight_id, flight_number, destination, flight_date FROM flights WHERE status='Scheduled'"
        )
        flights = cursor.fetchall()

        print("\n--- AVAILABLE FLIGHTS ---")
        for f in flights:
            print(f"ID {f['flight_id']} | {f['flight_number']} to {f['destination']} on {f['flight_date']}")

        while True:
            fid = get_valid_input("Enter Flight ID", int)
            cursor.execute("SELECT * FROM flights WHERE flight_id=%s", (fid,))
            flight = cursor.fetchone()
            if flight and flight['status'] == 'Scheduled':
                break
            print("[!] Invalid flight.")

        taken, valid = show_seat_map(conn, fid)

        while True:
            seat = get_valid_input("Select Seat (e.g. 12A)").upper()
            if seat in valid and seat not in taken:
                break
            print("[!] Invalid or taken seat.")

        while True:
            seat_class = get_valid_input("Class (Economy/Business)").upper()
            if is_valid_class(seat_class):
                break
            print("[!] Invalid class.")

        seat_class = seat_class.title()
        price = 5000 if seat_class == "Economy" else 15000

        print(f"\nProcessing payment of ₱{price}...")
        time.sleep(1)
        print("[SUCCESS] Payment Authorized.")

        pnr = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        cursor.execute("""
            INSERT INTO bookings (pnr, flight_id, passenger_id, seat_class, seat_number, price, status)
            VALUES (%s,%s,%s,%s,%s,%s,'Confirmed')
        """, (pnr, fid, pid, seat_class, seat, price))

        points = int(price * 0.10)
        cursor.execute(
            "UPDATE passengers SET loyalty_points = loyalty_points + %s WHERE passenger_id=%s",
            (points, pid)
        )

        conn.commit()

        print("\n--- E-TICKET ---")
        print("PNR:", pnr)
        print("Passenger:", pname)
        print("Seat:", seat, seat_class)
        print("Price:", price)

    except OperationCancelled:
        print("[!] Booking cancelled.")
    finally:
        conn.close()

def view_my_bookings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        email = get_valid_input("Enter Email", "email")
        cursor.execute("""
            SELECT b.pnr, f.flight_number, f.origin, f.destination, f.flight_date,
                   b.seat_number, b.seat_class, b.status
            FROM bookings b
            JOIN passengers p ON b.passenger_id = p.passenger_id
            JOIN flights f ON b.flight_id = f.flight_id
            WHERE p.email = %s
        """, (email,))

        rows = cursor.fetchall()
        if not rows:
            print("[!] No bookings found.")
            return

        print("\nPNR     FLIGHT   ROUTE              DATE        SEAT  CLASS     STATUS")
        print("-"*75)
        for r in rows:
            print(f"{r['pnr']:<7} {r['flight_number']:<7} "
                  f"{r['origin']}->{r['destination']:<15} "
                  f"{r['flight_date']} {r['seat_number']:<5} "
                  f"{r['seat_class']:<9} {r['status']}")

    except OperationCancelled:
        print("[!] View cancelled.")
    finally:
        conn.close()

def cancel_booking():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        email = get_valid_input("Enter Passenger Email", "email")
        cursor.execute("SELECT passenger_id FROM passengers WHERE email=%s", (email,))
        p = cursor.fetchone()
        if not p:
            print("[!] Passenger not found.")
            return

        cursor.execute("""
            SELECT pnr, price FROM bookings
            WHERE passenger_id=%s AND status='Confirmed'
        """, (p['passenger_id'],))

        rows = cursor.fetchall()
        if not rows:
            print("[!] No active bookings.")
            return

        for r in rows:
            print(f"PNR: {r['pnr']} | Price: ₱{r['price']}")

        pnr = get_valid_input("Enter PNR to cancel").upper()
        cursor.execute("SELECT * FROM bookings WHERE pnr=%s", (pnr,))
        booking = cursor.fetchone()

        if not booking:
            print("[!] Invalid PNR.")
            return

        refund = float(booking['price']) * 0.80
        cursor.execute("UPDATE bookings SET status='Cancelled' WHERE pnr=%s", (pnr,))
        conn.commit()

        print(f"[CANCELLED] Refund Amount: ₱{refund:,.2f}")

    except OperationCancelled:
        print("[!] Cancellation cancelled.")
    finally:
        conn.close()

def upgrade_booking():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        email = get_valid_input("Enter Passenger Email", "email")
        cursor.execute("SELECT passenger_id FROM passengers WHERE email=%s", (email,))
        p = cursor.fetchone()
        if not p:
            print("[!] Passenger not found.")
            return

        cursor.execute("""
            SELECT pnr, price FROM bookings
            WHERE passenger_id=%s AND seat_class='Economy' AND status='Confirmed'
        """, (p['passenger_id'],))

        rows = cursor.fetchall()
        if not rows:
            print("[!] No bookings eligible for upgrade.")
            return

        for r in rows:
            print(f"PNR: {r['pnr']} | Current Price: ₱{r['price']}")

        pnr = get_valid_input("Enter PNR to upgrade").upper()
        upgrade_fee = 15000 - 5000

        confirm = get_valid_input(f"Upgrade fee ₱{upgrade_fee}. Confirm? (Y/N)").upper()
        if confirm != 'Y':
            return

        cursor.execute("""
            UPDATE bookings
            SET seat_class='Business', price=15000
            WHERE pnr=%s
        """, (pnr,))

        conn.commit()
        print("[SUCCESS] Booking upgraded to Business.")

    except OperationCancelled:
        print("[!] Upgrade cancelled.")
    finally:
        conn.close()

def check_in():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        pnr = get_valid_input("Enter Booking PNR").upper()
        cursor.execute("""
            SELECT booking_id, status FROM bookings WHERE pnr=%s
        """, (pnr,))
        booking = cursor.fetchone()

        if not booking or booking['status'] != 'Confirmed':
            print("[!] Invalid booking.")
            return

        cursor.execute("SELECT * FROM checkin WHERE booking_id=%s", (booking['booking_id'],))
        if cursor.fetchone():
            print("[!] Already checked in.")
            return

        bags = get_valid_input("Number of bags", int)
        cursor.execute(
            "INSERT INTO checkin (booking_id, bags_checked) VALUES (%s,%s)",
            (booking['booking_id'], bags)
        )
        conn.commit()

        print("[SUCCESS] Check-in completed.")

    except OperationCancelled:
        print("[!] Check-in cancelled.")
    finally:
        conn.close()
