# ✈️ Airline Management System (Enterprise Edition)

A comprehensive, modular **Airline Management System** built with **Python** and **MySQL**. This system integrates six distinct operational departments (G1-G6) to manage the entire lifecycle of airline operations, from flight scheduling and maintenance to reservations and customer loyalty.

---

## 📋 Project Scope & Modules

This project is divided into **6 integrated modules**, simulating a real-world enterprise environment.

### **[G1] Flight Management Module**
* **Team:** Sapanta, Davis, Redilosa, Mirandilla, Mijares, Cruz
* **Features:**
    * Manage flight schedules, routes, and dates.
    * Gate Management (Gate assignment logic).
    * Real-time status updates (Scheduled, Delayed, Cancelled).
    * **Integration:** Scheduling is blocked by **G5 (Maintenance)** if the selected aircraft is unavailable.

### **[G2] Reservation & Ticketing Module**
* **Team:** Delos Santos, Rolloque, Sulayao
* **Features:**
    * Booking system with automatic **PNR generation**.
    * Seat Class selection (Economy/Business).
    * **Payment Simulation:** Secure dummy payment gateway simulation.
    * **Integration:** Auto-creates customer profiles in **G6**; Checks **G1** for flight availability.

### **[G3] Check-in & Boarding Module**
* **Team:** Gueta, Pecaso, Fallar
* **Features:**
    * Validates PNR and Payment status.
    * Generates visual **ASCII Boarding Passes**.
    * Tracks baggage handling.

### **[G4] Crew Management Module**
* **Team:** Boquiron, Abner, Briones, Irenio, Ramos, Rapanan
* **Features:**
    * Crew Rostering (Pilots/Cabin Crew).
    * Assigns crew to specific flights.
    * Views active flight assignments.

### **[G5] Maintenance & Aircraft Module**
* **Team:** Sace, Pingol, Bello, Cababao
* **Features:**
    * Fleet management (Active vs. In-Maintenance).
    * **Integration:** Locking mechanism that prevents G1 from scheduling flights on broken aircraft.

### **[G6] Customer Management (CRM) Module**
* **Team:** Barcoma, Dutong, Alis, Francisco, Sobiono
* **Features:**
    * Tracks passenger history.
    * **Loyalty System:** Automatically calculates tiers (Blue/Silver/Gold) based on booking points.

---

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Database:** MySQL (via XAMPP/MariaDB)
* **Library:** `mysql-connector-python`
* **Architecture:** Modular CLI Application

---

## 📂 Project Structure

```text
AirlineSystem/
│
├── main.py                # Entry point (Main Dashboard)
├── db_config.py           # Database connection & Input Validation
├── admin_panel.py         # Secret Admin Dashboard (God Mode)
├── database_setup.sql     # SQL Script to create tables (Run this first!)
│
├── g1_flights.py          # Flight operations logic
├── g2_reservations.py     # Booking logic
├── g3_checkin.py          # Boarding pass logic
├── g4_crew.py             # Crew assignment logic
├── g5_maintenance.py      # Aircraft status logic
└── g6_customer.py         # Loyalty program logic
```

---

## 🚀 Installation & Setup

Follow these steps to run the system on your local machine.

### 1. Prerequisites
Ensure you have the following installed:
* [Python](https://www.python.org/downloads/) (**Important:** Check "Add to PATH" during installation)
* [XAMPP](https://www.apachefriends.org/index.html) (For the MySQL Database)

### 2. Install Required Library
Open your Command Prompt (cmd) or Terminal and run:

```bash
pip install mysql-connector-python
or
python -m pip install mysql-connector-python



