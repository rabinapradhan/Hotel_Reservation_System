import tkinter as tk
from tkinter import messagebox
import psycopg2
import datetime
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

admin_password = hash_password('admin')
staff_password = hash_password('staff')

# Database connection
DB_USER = "hotel_user"
DB_PASSWORD = "velvrin"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "hotel_management"

# Function to connect to the database
def connect_db():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

# Function to execute a query
def execute_query(query, params=()):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
    except Exception as e:
        print(f"Error executing query: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# Function to fetch query results
def fetch_query(query, params=()):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(query, params)
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        return records
    except Exception as e:
        print(f"Error fetching query results: {e}")
        return []

# Login function
def login():
    user = user_entry.get()
    password = password_entry.get()
    
    if not user or not password:
        messagebox.showerror("Login Failed", "Please enter both username and password.")
        return

    # Validate length of username and password
    if len(user) > 50 or len(password) > 50:
        messagebox.showerror("Login Failed", "Username and password should be less than 50 characters.")
        return

    hashed_password = hash_password(password)
    user_record = fetch_query("SELECT role FROM users WHERE username=%s AND password=%s", (user, hashed_password))
    
    if user_record:
        role = user_record[0][0]
        messagebox.showinfo("Login Successful", "You have successfully logged in.")
        if role == "Admin":
            open_admin_dashboard()
        elif role == "Staff":
            open_staff_dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid credentials")


def logout(current_window):
    current_window.destroy()
    show_login_screen()

# Function that opens admin dashboard
def open_admin_dashboard():
    login_screen.destroy()
    dashboard = tk.Tk()
    dashboard.title("Admin Dashboard")
    dashboard.geometry("400x400")
    dashboard.configure(bg="light blue")
    tk.Button(dashboard, text="Reservation", command=open_reservation).pack(pady=10)
    tk.Button(dashboard, text="Guest Information", command=open_guest_info).pack(pady=10)
    tk.Button(dashboard, text="Service Request", command=open_service_request).pack(pady=10)
    tk.Button(dashboard, text="Check-out", command=open_checkout).pack(pady=10)
    tk.Button(dashboard, text="Reports", command=open_reports).pack(pady=10)
    tk.Button(dashboard, text="Add/Edit Rooms", command=open_room_management).pack(pady=10)
    tk.Button(dashboard, text="Logout", command=lambda: logout(dashboard)).pack(pady=10)
    dashboard.mainloop()

# Function that opens staff dashboard
def open_staff_dashboard():
    login_screen.destroy()
    dashboard = tk.Tk()
    dashboard.title("Staff Dashboard")
    dashboard.geometry("400x400")
    dashboard.configure(bg="light green")
    tk.Button(dashboard, text="Reservation", command=open_reservation).pack(pady=10)
    tk.Button(dashboard, text="Guest Information", command=open_guest_info).pack(pady=10)
    tk.Button(dashboard, text="Service Request", command=open_service_request).pack(pady=10)
    tk.Button(dashboard, text="Check-out", command=open_checkout).pack(pady=10)
    tk.Button(dashboard, text="Logout", command=lambda: logout(dashboard)).pack(pady=10)
    dashboard.mainloop()

# Function to open reservation screen
def open_reservation():
    reservation_screen = tk.Tk()
    reservation_screen.title("Reservation")
    reservation_screen.geometry("400x300")
    tk.Label(reservation_screen, text="Room Numbers (comma-separated)").grid(row=0, column=0, pady=5)
    tk.Label(reservation_screen, text="Check-in Date (YYYY-MM-DD)").grid(row=1, column=0, pady=5)
    tk.Label(reservation_screen, text="Check-out Date (YYYY-MM-DD)").grid(row=2, column=0, pady=5)
    room_numbers_entry = tk.Entry(reservation_screen)
    checkin_date_entry = tk.Entry(reservation_screen)
    checkout_date_entry = tk.Entry(reservation_screen)
    room_numbers_entry.grid(row=0, column=1, pady=5)
    checkin_date_entry.grid(row=1, column=1, pady=5)
    checkout_date_entry.grid(row=2, column=1, pady=5)
    tk.Button(reservation_screen, text="Check Availability", command=lambda: check_availability(room_numbers_entry.get(), checkin_date_entry.get(), checkout_date_entry.get())).grid(row=3, column=1, pady=5)
    tk.Button(reservation_screen, text="Confirm Reservation", command=lambda: confirm_reservation(room_numbers_entry.get(), checkin_date_entry.get(), checkout_date_entry.get())).grid(row=4, column=1, pady=5)
    reservation_screen.mainloop()

def is_valid_date(date_str):
    try:
        datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def check_availability(room_numbers, checkin_date, checkout_date):
    if not room_numbers or not checkin_date or not checkout_date:
        messagebox.showerror("Input Error", "All fields must be filled out.")
        return

    if not is_valid_date(checkin_date) or not is_valid_date(checkout_date):
        messagebox.showerror("Date Error", "Dates must be in the format YYYY-MM-DD.")
        return

    try:
        room_list = room_numbers.split(",")
        unavailable_rooms = []
        for room_number in room_list:
            records = fetch_query("SELECT * FROM Room WHERE room_number=%s", (room_number.strip(),))
            if not records:
                messagebox.showerror("Error", f"Room {room_number.strip()} does not exist.")
                return

            room_record = records[0]
            if room_record[4] == 'booked':
                unavailable_rooms.append(room_number.strip())

        if unavailable_rooms:
            messagebox.showerror("Not Available", f"Rooms not available: {', '.join(unavailable_rooms)}")
        else:
            messagebox.showinfo("Available", "All rooms are available.")
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching query results: {e}")

def confirm_reservation(room_numbers, checkin_date, checkout_date):
    if not room_numbers or not checkin_date or not checkout_date:
        messagebox.showerror("Input Error", "All fields must be filled out.")
        return

    if not is_valid_date(checkin_date) or not is_valid_date(checkout_date):
        messagebox.showerror("Date Error", "Dates must be in the format YYYY-MM-DD.")
        return

    try:
        guest_id = 1  # Assuming guest_id is 1 for the demo
        room_list = room_numbers.split(",")
        total_amount = 0

        # Check availability for each room
        for room_number in room_list:
            room_record = fetch_query("SELECT room_id, rate_per_night FROM Room WHERE room_number=%s", (room_number.strip(),))
            if not room_record:
                messagebox.showerror("Error", f"Room {room_number.strip()} not found or unavailable.")
                return

            room_id, rate_per_night = room_record[0]

            if is_room_already_booked(room_id, checkin_date, checkout_date):
                messagebox.showerror("Error", f"Room {room_number.strip()} is already booked for the specified dates.")
                return

            total_days = (datetime.datetime.strptime(checkout_date, '%Y-%m-%d') - datetime.datetime.strptime(checkin_date, '%Y-%m-%d')).days
            if total_days <= 0:
                messagebox.showerror("Error", "Check-out date must be after the check-in date.")
                return

            total_amount += rate_per_night * total_days

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Reservation (guest_id, room_id, check_in_date, check_out_date, total_amount) 
            VALUES (%s, %s, %s, %s, %s) RETURNING reservation_id
        """, (guest_id, room_id,  checkin_date, checkout_date, total_amount))
        reservation_id = cursor.fetchone()[0]
        conn.commit()

        # Insert into RESERVATION_ROOM table
        for room_number in room_list:
            room_id = fetch_query("SELECT room_id FROM Room WHERE room_number=%s", (room_number.strip(),))[0][0]
            cursor.execute("INSERT INTO RESERVATION_ROOM (reservation_id, room_id) VALUES (%s, %s)", (reservation_id, room_id))
            cursor.execute("UPDATE Room SET status='booked' WHERE room_id=%s", (room_id,))

        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", "Reservation confirmed.")
    except Exception as e:
        messagebox.showerror("Error", f"Error processing reservation: {e}")

def is_room_already_booked(room_id, checkin_date, checkout_date):
    records = fetch_query("""
        SELECT *
        FROM Reservation
        INNER JOIN RESERVATION_ROOM ON Reservation.reservation_id = RESERVATION_ROOM.reservation_id
        WHERE RESERVATION_ROOM.room_id = %s AND 
            (Reservation.check_in_date <= %s AND Reservation.check_out_date >= %s)
    """, (room_id, checkout_date, checkin_date))
    return len(records) > 0




# Function to open the guest information screen
def open_guest_info():
    guest_info_screen = tk.Tk()
    guest_info_screen.title("Guest Information")
    guest_info_screen.geometry("400x300")

    tk.Label(guest_info_screen, text="Name").grid(row=0, column=0, pady=5)
    tk.Label(guest_info_screen, text="Contact Number").grid(row=1, column=0, pady=5)
    tk.Label(guest_info_screen, text="Duration of Stay").grid(row=2, column=0, pady=5)
    name_entry = tk.Entry(guest_info_screen)
    contact_number_entry = tk.Entry(guest_info_screen)
    duration_of_stay_entry = tk.Entry(guest_info_screen)
    name_entry.grid(row=0, column=1, pady=5)
    contact_number_entry.grid(row=1, column=1, pady=5)
    duration_of_stay_entry.grid(row=2, column=1, pady=5)

    tk.Button(guest_info_screen, text="Save", command=lambda: save_guest_info(name_entry.get(), contact_number_entry.get(), duration_of_stay_entry.get())).grid(row=4, column=1, pady=5)
    guest_info_screen.mainloop()

def save_guest_info(guest_name, contact_number, duration_of_stay):
    if not guest_name or not contact_number or not duration_of_stay:
        messagebox.showerror("Input Error", "All fields must be filled out.")
        return

    if len(guest_name) > 100:
        messagebox.showerror("Input Error", "Guest name should be less than 100 characters.")
        return

    if not contact_number.isdigit() or len(contact_number) != 10:
        messagebox.showerror("Input Error", "Contact number must be numeric and exactly 10 digits.")
        return
    try:
        execute_query("INSERT INTO Guest (guest_name, contact_number, duration_of_stay) VALUES (%s, %s, %s)", (guest_name, int(contact_number), duration_of_stay))
        messagebox.showinfo("Success", "Guest information added successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# Function to open service request screen
def open_service_request():
    service_request_screen = tk.Tk()
    service_request_screen.title("Service Request")
    service_request_screen.geometry("400x300")
    
    tk.Label(service_request_screen, text="Reservation ID").grid(row=0, column=0, pady=5)
    tk.Label(service_request_screen, text="Service Type").grid(row=1, column=0, pady=5)
    tk.Label(service_request_screen, text="Service Cost").grid(row=2, column=0, pady=5)
    
    reservation_id_entry = tk.Entry(service_request_screen)
    service_type_entry = tk.Entry(service_request_screen)
    service_cost_entry = tk.Entry(service_request_screen)
    
    reservation_id_entry.grid(row=0, column=1, pady=5)
    service_type_entry.grid(row=1, column=1, pady=5)
    service_cost_entry.grid(row=2, column=1, pady=5)
    
    tk.Button(service_request_screen, text="Add Service", command=lambda: add_service(reservation_id_entry.get(), service_type_entry.get(), service_cost_entry.get())).grid(row=4, column=1, pady=5)
    service_request_screen.mainloop()

def add_service(reservation_id, service_type, service_cost):
    if reservation_id and service_type and service_cost:
        execute_query("INSERT INTO Service (reservation_id, service_type, service_cost) VALUES (%s, %s, %s)",
                      (reservation_id, service_type, service_cost))
        messagebox.showinfo("Success", "Service added.")
    else:
        messagebox.showerror("Error", "Reservation ID, Service Type, and Service Cost are required fields.")


# Function to open checkout screen

def open_checkout():
    checkout_screen = tk.Tk()
    checkout_screen.title("Check-out")
    checkout_screen.geometry("400x300")
    
    tk.Label(checkout_screen, text="Reservation ID").grid(row=0, column=0, pady=5)
    
    reservation_id_entry = tk.Entry(checkout_screen)
    reservation_id_entry.grid(row=0, column=1, pady=5)
    
    tk.Button(checkout_screen, text="Generate Invoice", command=lambda: generate_invoice(reservation_id_entry.get())).grid(row=1, column=1, pady=5)
    
    checkout_screen.mainloop()


def generate_invoice(reservation_id):
    services = fetch_query("SELECT service_type, service_cost FROM Service WHERE reservation_id=%s", (reservation_id,))
    reservation = fetch_query("SELECT check_in_date, check_out_date, total_amount FROM Reservation WHERE reservation_id=%s", (reservation_id,))
    
    if reservation:
        total_amount = reservation[0][2]
        service_costs = sum([service[1] for service in services])
        final_amount = total_amount + service_costs
        
        invoice_text = f"Check-in Date: {reservation[0][0]}\nCheck-out Date: {reservation[0][1]}\nRoom Charges: ${total_amount}\nService Charges: ${service_costs}\nTotal Amount: ${final_amount}"
        messagebox.showinfo("Invoice", invoice_text)
    else:
        messagebox.showerror("Error", "Invalid Reservation ID")
    try:
        room_ids = fetch_query("SELECT room_id FROM RESERVATION_ROOM WHERE reservation_id=%s", (reservation_id,))
        for room_id in room_ids:
            execute_query("UPDATE Room SET status='available' WHERE room_id=%s", (room_id[0],))

        messagebox.showinfo("Success", "Check-out completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))



# Function to open the Reports screen
def open_reports():
    reports_screen = tk.Tk()
    reports_screen.title("Reports")
    reports_screen.geometry("400x300")

    tk.Button(reports_screen, text="Occupancy Report", command=generate_occupancy_report).pack(pady=10)
    tk.Button(reports_screen, text="Sales Report", command=generate_sales_report).pack(pady=10)

    reports_screen.mainloop()

def generate_occupancy_report():
    try:
        records = fetch_query("SELECT room_number, status FROM Room")
        report = "Occupancy Report:\n"
        for record in records:
            report += f"Room {record[0]}: {record[1]}\n"
        messagebox.showinfo("Occupancy Report", report)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def generate_sales_report():
    try:
        records = fetch_query("SELECT reservation_id, total_amount FROM Reservation")
        report = "Sales Report:\n"
        for record in records:
            report += f"Reservation {record[0]}: ${record[1]}\n"
        messagebox.showinfo("Sales Report", report)
    except Exception as e:
        messagebox.showerror("Error", str(e))


# Function to open room management screen
def open_room_management():
    room_management_screen = tk.Tk()
    room_management_screen.title("Room Management")
    room_management_screen.geometry("400x300")

    tk.Label(room_management_screen, text="Room Number").grid(row=0, column=0, pady=5)
    tk.Label(room_management_screen, text="Room Type").grid(row=1, column=0, pady=5)
    tk.Label(room_management_screen, text="Rate per Night").grid(row=2, column=0, pady=5)

    room_number_entry = tk.Entry(room_management_screen)
    room_type_entry = tk.Entry(room_management_screen)
    rate_entry = tk.Entry(room_management_screen)

    room_number_entry.grid(row=0, column=1, pady=5)
    room_type_entry.grid(row=1, column=1, pady=5)
    rate_entry.grid(row=2, column=1, pady=5)

    tk.Button(room_management_screen, text="Add Room", command=lambda: add_room(room_number_entry.get(), room_type_entry.get(), rate_entry.get())).grid(row=3, column=1, pady=5)

    room_management_screen.mainloop()

def add_room(room_number, room_type, rate):
    if not room_number or not room_type or not rate:
        messagebox.showerror("Input Error", "All fields must be filled out.")
        return

    try:
        execute_query("INSERT INTO Room (room_number, room_type, rate_per_night, status) VALUES (%s, %s, %s, 'available')", (room_number, room_type, rate))
        messagebox.showinfo("Success", "Room added successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Main Window
def show_login_screen():
    global login_screen, user_entry, password_entry
    login_screen = tk.Tk()
    login_screen.title("Login Screen")
    login_screen.geometry("300x200")

    tk.Label(login_screen, text="Username").pack(pady=10)
    user_entry = tk.Entry(login_screen)
    user_entry.pack(pady=10)

    tk.Label(login_screen, text="Password").pack(pady=10)
    password_entry = tk.Entry(login_screen, show="*")
    password_entry.pack(pady=10)

    tk.Button(login_screen, text="Login", command=login).pack(pady=10)
    login_screen.mainloop()

# Initialize and show the login screen
show_login_screen()