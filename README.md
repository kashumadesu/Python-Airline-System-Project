# ✈️ Airline Management System (Enterprise Edition)

A comprehensive, modular Airline Management System built with **Python** and **MySQL**. This system integrates six distinct operational departments (G1-G6) to manage the entire lifecycle of airline operations, from flight scheduling and maintenance to reservations and customer loyalty.

## 📋 Project Scope & Modules

This project is divided into 6 integrated modules, simulating a real-world enterprise environment:

### **[G1] Flight Management Module**
* **Team:** Sapanta, Davis, Redilosa, Mirandilla, Mijares, Cruz
* **Features:**
    * Manage flight schedules and routes.
    * Real-time status updates (Scheduled, Delayed, Cancelled).
    * **Integration:** blocked by G5 (Maintenance) if aircraft is unavailable.

### **[G2] Reservation & Ticketing Module**
* **Team:** Delos Santos, Rolloque, Sulayao
* **Features:**
    * Booking system with PNR generation.
    * Seat Class selection (Economy/Business).
    * **Integration:** Auto-creates customer profiles in G6; Checks G1 for flight availability.

### **[G3] Check-in & Boarding Module**
* **Team:** Gueta, Pecaso, Fallar
* **Features:**
    * Validates PNR and Payment status.
    * Generates visual Boarding Passes.
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

## 🚀 Installation & Setup

### 1. Prerequisites
Ensure you have the following installed:
* [Python](https://www.python.org/downloads/) (Check "Add to PATH" during installation)
* [XAMPP](https://www.apachefriends.org/index.html) (For the MySQL Database)

* STEP 2: INSTALL REQUIRED LIBRARY
Open your Command Prompt (cmd) or Terminal and run this command:

DOS

pip install mysql-connector-python
⚠️ If that doesn't work (error says "pip is not recognized"), try this instead:

DOS

python -m pip install mysql-connector-python

### 3. Clone the Repository
```bash
git clone [https://github.com/yourusername/airline-system.git](https://github.com/yourusername/airline-system.git)
cd airline-system
