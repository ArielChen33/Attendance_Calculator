# Updated Full Code with Monthly Attendance Tracking

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime
import shutil
from collections import defaultdict
import calendar
import csv
import pandas as pd

# === Load and Save Functions ===
DEFAULT_STAFF = {}


def get_data_path():
    appdata = os.getenv('APPDATA') or os.getcwd()
    app_folder = os.path.join(appdata, "StaffApp")
    os.makedirs(app_folder, exist_ok=True)
    return os.path.join(app_folder, "staff.json")


def get_default_json_path():
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(bundle_dir, "staff.json")


def load_staff():
    target_path = get_data_path()
    if not os.path.exists(target_path):
        try:
            shutil.copy(get_default_json_path(), target_path)
        except FileNotFoundError:
            with open(target_path, "w") as f:
                json.dump(DEFAULT_STAFF, f, indent=4)
    with open(target_path, "r") as f:
        return json.load(f)


def save_staff():
    target_path = get_data_path()
    with open(target_path, "w") as f:
        json.dump(staffList, f, indent=4)


# === Helper Functions ===
def get_month_key(date):
    return date[:7]  # 'YYYY-MM'
from collections import defaultdict
from datetime import datetime

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def calc_monthly_stats(attendance):
    stats = defaultdict(lambda: {
        "workdays": 0,
        "absences": 0,
        "tardiness": 0,
        "attended_hours": 0,
    })
    for date, hours in attendance.items():
        if not is_valid_date(date):
            continue  # Skip non-date keys like "2025-05"

        month = date[:7]  # or use get_month_key(date)
        stats[month]["workdays"] += 1

        print("attendance", attendance)
        print("month: ", month)
        print("hours: ", hours)

        stats[month]["attended_hours"] += hours
        if hours >= 8:
            continue
        elif hours == 0:
            stats[month]["absences"] += 1
        else:
            stats[month]["tardiness"] += 1
    return stats



# === Core Logic ===
staffList = load_staff()
current_name = None


# === GUI Functional Logic ===
def find_staff():
    global current_name
    name_input = entry.get().strip().lower()
    if not name_input:
        messagebox.showerror("Error", "Please enter a name.")
        return

    matches = [name for name in staffList if name.lower().startswith(name_input)]

    if not matches:
        messagebox.showerror("Not Found", "No matching staff found.")
        clear_table()
        update_btn("disabled")
    elif len(matches) == 1:
        current_name = matches[0]
        show_staff(current_name)
        update_btn("normal")
    else:
        clear_table()
        for name in sorted(matches):
            show_staff(name, single=False)
        update_btn("disabled")


def record_attendance():
    if not current_name:
        return

    try:
        hours = simpledialog.askfloat("Attendance", "Enter hours attended today:")
        if hours is None or hours < 0 or hours > 24:
            raise ValueError
    except:
        messagebox.showerror("Invalid", "Please enter a valid number between 0 and 24.")
        return

    staff = staffList[current_name]
    date = datetime.now().strftime("%Y-%m-%d")
    staff.setdefault("attendance", {})[date] = hours
    staff["lastUpdate"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_staff()
    show_staff(current_name)
    messagebox.showinfo("Recorded", f"{current_name}'s attendance recorded: {hours} hours")


def delete_staff(name):
    if name in staffList:
        confirm = messagebox.askyesno("Confirm", f"Are you sure to delete {name}?")
        if confirm:
            del staffList[name]
            save_staff()
            clear_table()
            update_btn("disabled")


def list_all_staff():
    clear_table()
    for name in sorted(staffList):
        show_staff(name, single=False)
    update_btn("disabled")


def show_staff(name, single=True):
    if single:
        clear_table()
    staff = staffList[name]
    stats = calc_monthly_stats(staff.get("attendance", {}))
    this_month = datetime.now().strftime("%Y-%m")
    month_stat = stats.get(this_month, {})

    workdays = month_stat.get("workdays", 0)
    absences = month_stat.get("absences", 0)
    tardiness = month_stat.get("tardiness", 0)
    hours = month_stat.get("attended_hours", 0)
    attendance_pct = round((hours / (workdays * 8) * 100) if workdays else 0, 2)

    tree.insert("", "end", values=(
        name,
        workdays,
        absences,
        tardiness,
        f"{attendance_pct}%",
        staff.get("lastUpdate", "N/A")
    ))
    global current_name
    current_name = name


def clear_table():
    for item in tree.get_children():
        tree.delete(item)


def update_btn(state):
    recordBtn.config(state=state)
    deleteBtn.config(state=state)


def export_to_excel():
    filename = f"staff_attendance_{datetime.now().strftime('%Y%m%d')}.csv"
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Total Workdays", "Total Absences", "Total Tardiness", "Attendance %", "Last Updated"])
        for name in sorted(staffList):
            staff = staffList[name]
            stats = calc_monthly_stats(staff.get("attendance", {}))
            month_stat = stats.get(datetime.now().strftime("%Y-%m"), {})
            workdays = month_stat.get("workdays", 0)
            absences = month_stat.get("absences", 0)
            tardiness = month_stat.get("tardiness", 0)
            hours = month_stat.get("attended_hours", 0)
            attendance_pct = round((hours / (workdays * 8) * 100) if workdays else 0, 2)
            writer.writerow([name, workdays, absences, tardiness, f"{attendance_pct}%", staff.get("lastUpdate", "N/A")])
    messagebox.showinfo("Exported", f"Data saved to {filename}")

def import_excel():
    filepath = filedialog.askopenfilename(
        title="Select File",
        filetypes=[("CSV or Excel files", "*.csv *.xlsx *.xls")]
    )
    if not filepath:
        return

    try:
        if filepath.endswith(".csv"):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath, engine="openpyxl")  # Only used for real Excel files

        imported_count = 0

        for _, row in df.iterrows():
            name = row.get("Name")
            date = str(row.get("Date"))[:10]
            hours_str = row.get("Hours") or row.get("Attended Hours")  # depending on your column header
            try:
                hours = float(hours_str)
            except (ValueError, TypeError):
                hours = 0.0

            if name and date:
                staff = staffList.get(name)
                if not staff:
                    staff = {"name": name, "attendance": {}}
                    staffList[name] = staff
                staff.setdefault("attendance", {})[date] = hours
                imported_count += 1

        list_all_staff()
        messagebox.showinfo("Import Successful", f"Imported {imported_count} attendance records.")
    except Exception as e:
        messagebox.showerror("Import Failed", str(e))

def add_staff(name):
    name = name.strip()
    if not name:
        messagebox.showerror("Error", "Name cannot be empty.")
        return
    if name in staffList:
        messagebox.showerror("Error", "Staff already exists.")
        return
    staffList[name] = {
        "attendance": {},
        "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    save_staff()
    messagebox.showinfo("Added", f"{name} has been added.")
    new_entry.delete(0, tk.END)
    toggle_add_frame()
    show_staff(name)


def toggle_add_frame():
    global frame_add_visible
    if frame_add_visible:
        frame_add.pack_forget()
        frame_add_visible = False
    else:
        frame_add.pack(pady=5)
        frame_add_visible = True


def on_row_select(event):
    selected = tree.selection()
    if not selected:
        return
    item = tree.item(selected[0])
    name = item["values"][0]
    if name in staffList:
        global current_name
        current_name = name
        update_btn("normal")


# === GUI Layout ===
root = tk.Tk()
root.title("Staff Monthly Attendance")
root.geometry("800x500")

frame_search = tk.Frame(root)
frame_search.pack(pady=10)
tk.Label(frame_search, text="Enter Staff Name:").pack(side=tk.LEFT)
entry = tk.Entry(frame_search)
entry.pack(side=tk.LEFT, padx=5)
entry.bind("<Return>", lambda event: find_staff())
tk.Button(frame_search, text="Find", command=find_staff).pack(side=tk.LEFT)

frame_controls = tk.Frame(root)
frame_controls.pack(pady=5)
tk.Button(frame_controls, text="List All", command=list_all_staff).pack(side=tk.LEFT, padx=5)
tk.Button(frame_controls, text="Add Staff", command=toggle_add_frame).pack(side=tk.LEFT, padx=5)
tk.Button(frame_controls, text="Export to Excel", command=export_to_excel).pack(side=tk.LEFT, padx=5)
tk.Button(frame_controls, text="Import Excel", command=import_excel).pack(side=tk.LEFT, pady=5)

frame_add = tk.Frame(root)
frame_add_visible = False
tk.Label(frame_add, text="New Staff Name:").pack(side=tk.LEFT)
new_entry = tk.Entry(frame_add)
new_entry.pack(side=tk.LEFT, padx=5)
new_entry.bind("<Return>", lambda event: add_staff(new_entry.get()))
tk.Button(frame_add, text="Confirm", command=lambda: add_staff(new_entry.get())).pack(side=tk.LEFT)

columns = ("Name", "Total Workdays", "Total Absences", "Total Tardiness", "Attendance %", "Last Updated")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER, width=120)
tree.pack(pady=15)
tree.bind("<<TreeviewSelect>>", on_row_select)

frame_actions = tk.Frame(root)
frame_actions.pack(pady=10)
recordBtn = tk.Button(frame_actions, text="Record Attendance", command=record_attendance, state="disabled")
deleteBtn = tk.Button(frame_actions, text="Delete", command=lambda: delete_staff(current_name), state="disabled")
recordBtn.pack(side=tk.LEFT, padx=10)
deleteBtn.pack(side=tk.LEFT, padx=10)

root.mainloop()
