from db_config import get_db_connection, clear_screen, pause, get_valid_input
import random
import string

def menu():
    while True:
        clear_screen()
        print("--- [G2] RESERVATION SYSTEM ---")
        print("1. Book a Ticket")
        print("2. View My Bookings")
        print("0. Back to Main Menu")
        choice = input("\nSelect: ")
        
        if choice == '1': book_ticket(); pause()
        elif choice == '2': view_my_bookings(); pause()
        elif choice == '0': break

def book_ticket():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Identify Passenger
    email = get_valid_input("\nEnter Passenger Email: ")
    cursor.execute("SELECT * FROM passengers WHERE email = %s", (email,))
    p = cursor.fetchone()
    
    if p:
        print(f"Welcome back, {p['name']} (Tier: {p['tier']})")
        pid = p['passenger_id']
    else:
        print("New Passenger Detected.")
        name = get_valid_input("Full Name: ")
        cursor.execute("INSERT INTO passengers (name, email) VALUES (%s, %s)", (name, email))
        conn.commit()
        pid = cursor.lastrowid

    # 2. Select Flight
    cursor.execute("SELECT flight_id, flight_number, destination, flight_date FROM flights WHERE status='Scheduled'")
    flights = cursor.fetchall()
    print("\n--- AVAILABLE FLIGHTS ---")
    for f in flights: print(f"ID {f['flight_id']} | {f['flight_number']} to {f['destination']} on {f['flight_date']}")
    
    try:
        fid = get_valid_input("\nEnter Flight ID: ", int)
        seat_class = get_valid_input("Class (Economy/Business): ").title()
        price = 5000 if seat_class == "Economy" else 15000
        seat = get_valid_input(f"Select Seat (e.g. 12A): ")
        
        pnr = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        cursor.execute("""
            INSERT INTO bookings (pnr, flight_id, passenger_id, seat_class, seat_number, price, status) 
            VALUES (%s, %s, %s, %s, %s, %s, 'Confirmed')
        """, (pnr, fid, pid, seat_class, seat, price))
        
        points = int(price * 0.10)
        cursor.execute("UPDATE passengers SET loyalty_points = loyalty_points + %s WHERE passenger_id = %s", (points, pid))
        
        conn.commit()
        print(f"\n[SUCCESS] Booking Confirmed!")
        print(f"PNR: {pnr} | Price: ₱{price} | Points Earned: {points}")
    except Exception as e:
        print(f"[ERROR] Booking Failed (Check Flight ID): {e}")
    conn.close()

def view_my_bookings():
    email = get_valid_input("\nEnter your Email to view bookings: ")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
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
            print(f"{b['pnr']:<8} {b['flight_number']:<8} {b['origin']}->{b['destination']:<16} {str(b['flight_date']):<12} {b['seat_number']:<6} {b['status']}")
    conn.close()