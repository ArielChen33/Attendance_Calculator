# ===========================
# Seems okay for showing a single staff's info with a selected month
# Updated Full Code with Monthly Attendance Tracking (Hours-based)
import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime, timedelta
import shutil
from collections import defaultdict
import calendar
import csv
import pandas as pd
from tkcalendar import Calendar
import tkinter.simpledialog as sd

DEFAULT_STAFF = {}

# ================== DATA SOURCE ==========================================

# def get_data_path(): # Get the data from my own path
#     path = r"C:\Users\Ariel\OneDrive - FDG\FDG-Shipping server\Ariel\Projects\Attendance Calculator\staff.json"
#     os.makedirs(os.path.dirname(path), exist_ok=True)
#     return path

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
        print("Loading", f.name)
        return json.load(f)


def save_staff():
    target_path = get_data_path()
    with open(target_path, "w") as f:
        json.dump(staffList, f, indent=4)


class DatePicker(simpledialog.Dialog):
    def body(self, master):
        self.title("Select Date")
        self.calendar = Calendar(master, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.pack()
        return self.calendar

    def apply(self):
        self.result = self.calendar.get_date()

class AttendanceInputDialog(tk.Toplevel):
    def __init__(self, parent, week_range):
        super().__init__(parent)
        self.title("Enter Weekly Attendance")
        self.grab_set()
        self.resizable(False, False)

        self.result = None

        # Week label at the top        
        week_start = datetime.strptime(week_range, "%Y-%m-%d")
        week_end = (week_start + timedelta(days=4)).strftime("%Y-%m-%d")
        week_range_label = f"Week: {week_range} to {week_end}"
        tk.Label(self, text=week_range_label, font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=(10, 5))
        
        tk.Label(self, text="Scheduled Hours:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Label(self, text="Attended Hours:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Label(self, text="Tardiness Hours:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Label(self, text="Absent Hours:").grid(row=4, column=0, sticky="e", padx=5, pady=5)

        self.scheduled_var = tk.DoubleVar()
        self.attended_var = tk.DoubleVar()
        self.tardiness_var = tk.DoubleVar()
        self.absent_var = tk.DoubleVar()

        tk.Entry(self, textvariable=self.scheduled_var).grid(row=1, column=1, padx=5, pady=5)
        tk.Entry(self, textvariable=self.attended_var).grid(row=2, column=1, padx=5, pady=5)
        tk.Entry(self, textvariable=self.tardiness_var).grid(row=3, column=1, padx=5, pady=5)
        tk.Entry(self, textvariable=self.absent_var).grid(row=4, column=1, padx=5, pady=5)

        submit_btn = tk.Button(self, text="Submit", command=self.submit)
        submit_btn.grid(row=5, column=0, columnspan=2, pady=10)
        submit_btn.bind("<Return>", lambda event: self.submit)
        self.bind("<Return>", lambda event: self.submit())

    def submit(self):
        try:
            scheduled = float(self.scheduled_var.get())
            attended = float(self.attended_var.get())
            tardiness = float(self.tardiness_var.get())
            absent = float(self.absent_var.get())
            
            if attended + tardiness + absent != scheduled: 
                messagebox.showerror("Error", f"The sum of attended, tardiness, and absent must equal scheduled hours.")
                return

            self.result = {
                "scheduled": scheduled,
                "attended": attended,
                "tardiness": tardiness,
                "absent": absent
            }
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

# ================== DEALING WITH DATA ==========================================

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def get_week_key(date):
    # Given a date, return 'YYYY-MM-DD to YYYY-MM-DD' for that week (Monday-Sunday)
    obj = datetime.strptime(date, "%Y-%m-%d")
    monday = obj - timedelta(days=obj.weekday())
    return monday.strftime("%Y-%m-%d")


def calc_monthly_stats(attendance):
    stats = defaultdict(lambda: {
        "scheduled": 0,
        "attended": 0,
        "tardiness": 0,
        "absent": 0
    })
    for week, hours in attendance.items():
        if not isinstance(hours, dict):
            continue
        if not is_valid_date(week):
            continue

        month = week[:7]
        stats[month]["scheduled"] += hours.get("scheduled", 0)
        stats[month]["attended"] += hours.get("attended", 0)
        stats[month]["tardiness"] += hours.get("tardiness", 0)
        stats[month]["absent"] += hours.get("absent", 0)
    return stats

# ================== HELPER FUNCTIONS ==========================================
def clear_table():
    for item in tree.get_children():
        tree.delete(item)

def update_btn(state):
    recordBtn.config(state=state)
    deleteBtn.config(state=state)
    perfect_check.config(state=state)
    bonusBtn.config(state=state)

# ================== MAIN FEATURES ==========================================

staffList = load_staff()
current_name = None

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

    date_picker = DatePicker(root)
    selected_date = date_picker.result
    if not selected_date:
        return

    # Extract the week key (e.g., "2025-05-12")
    week_key = get_week_key(selected_date)

    # Get the current staff data
    staff = staffList.get(current_name)
    if not staff:
        return

    # Check if the attendance data for the week already exists
    existing_week_data = staff.get("attendance", {}).get(week_key)

    dialog = AttendanceInputDialog(root, week_key)
    root.wait_window(dialog)
    if not dialog.result:
        return
    hours = dialog.result

    # Initialize 'attendance' dictionary if it doesn't exist
    if "attendance" not in staff:
        staff["attendance"] = {}

    # If the week's data exists, update it. Otherwise, create a new entry.
    if existing_week_data:
        existing_week_data.update({
            "scheduled": hours["scheduled"],
            "attended": hours["attended"],
            "tardiness": hours["tardiness"],
            "absent": hours["absent"]
        })
    else:
        # If no existing week data, create a new entry
        staff["attendance"][week_key] = {
            "scheduled": hours["scheduled"],
            "attended": hours["attended"],
            "tardiness": hours["tardiness"],
            "absent": hours["absent"]
        }

    # Update last update timestamp
    staff["lastUpdate"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Save the updated staff data
    save_staff()

    # Display updated staff info
    # Iinstead of
    # show_staff(current_name)
    show_updated_staff(current_name, selected_date) 
    # showing data from the month we just recorded, instead of selected on right top 

    messagebox.showinfo("Recorded", f"Attendance for the week starting {week_key} saved.")


def list_all_staff():
    global current_name  # Add this line to access the global variable
    clear_table()
    print("listtting")
    if current_name:
        current_name = ""
    for name in sorted(staffList):
        # show_staff(name, single=False)
        update_table()
    update_btn("disabled")


def show_staff(name, single=True):
    if single:
        clear_table()

    staff = staffList[name]
    stats = calc_monthly_stats(staff.get("attendance", {}))
    
    selected_month = month_var.get()
    if selected_month: 
        this_month = selected_month
    else: 
        this_month = datetime.now().strftime("%Y-%m")
    # this_month = datetime.now().strftime("%Y-%m")
    month_stat = stats.get(this_month, {})
    bonus_info = staff.get("bonus", {})
    
    bonus = bonus_info["current_bonus"]
    chance = bonus_info["current_chance"]
    scheduled = month_stat.get("scheduled", 0)
    attended = month_stat.get("attended", 0)
    tardiness = month_stat.get("tardiness", 0)
    absent = month_stat.get("absent", 0)
    attendance_pct = round((attended / scheduled * 100) if scheduled else 0, 2)

    tree.insert("", "end", values=(
        name,
        bonus, 
        chance, 
        scheduled,
        attended,
        tardiness,
        absent,
        f"{attendance_pct}%",
        staff.get("lastUpdate", "N/A")
    ))
    global current_name
    current_name = name


def show_updated_staff(name, selected_date ,single=True):
    if single:
        clear_table()
    staff = staffList[name]
    stats = calc_monthly_stats(staff.get("attendance", {}))
    # date_picker = DatePicker(root)
    # selected_date = date_picker.result
    # print(f"selected date: {selected_date}")
    # print(f"selected month: {selected_date[:7]}")
    this_month = selected_date[:7]
    month_stat = stats.get(this_month, {})
    bonus_info = staff.get("bonus", {})
    
    bonus = bonus_info["current_bonus"]
    chance = bonus_info["current_chance"]
    scheduled = month_stat.get("scheduled", 0)
    attended = month_stat.get("attended", 0)
    tardiness = month_stat.get("tardiness", 0)
    absent = month_stat.get("absent", 0)
    attendance_pct = round((attended / scheduled * 100) if scheduled else 0, 2)

    tree.insert("", "end", values=(
        name,
        bonus, 
        chance, 
        scheduled,
        attended,
        tardiness,
        absent,
        f"{attendance_pct}%",
        staff.get("lastUpdate", "N/A")
    ))
    global current_name
    current_name = name


def export_to_excel():
    filename = f"staff_attendance_{datetime.now().strftime('%Y%m%d')}.csv"
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Current Bonus", "Current Chance", "Scheduled Hours", "Attended Hours", "Tardiness Hours", "Absent Hours", "Attendance %", "Last Updated", "Monthly Stats"])
        
        for name in sorted(staffList):
            staff = staffList[name]
            stats = calc_monthly_stats(staff.get("attendance", {}))
            month_stat = stats.get(datetime.now().strftime("%Y-%m"), {})
            scheduled = month_stat.get("scheduled", 0)
            attended = month_stat.get("attended", 0)
            tardiness = month_stat.get("tardiness", 0)
            absent = month_stat.get("absent", 0)
            attendance_pct = round((attended / scheduled * 100) if scheduled else 0, 2)
            
            bonus_info = staff.get("bonus", {})
            current_bonus = bonus_info.get("current_bonus", 20)
            current_chance = bonus_info.get("current_chance", 0)

            writer.writerow([name, current_bonus, current_chance, scheduled, attended, tardiness, absent, f"{attendance_pct}%", staff.get("lastUpdate", "N/A"), month_stat])

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
            df = pd.read_excel(filepath, engine="openpyxl")

        imported_count = 0

        for _, row in df.iterrows():
            name = row.get("Name")
            date = str(row.get("Week Start"))[:10] if "Week Start" in row else datetime.now().strftime("%Y-%m-%d")
            scheduled = row.get("Scheduled Hours", 0)
            attended = row.get("Attended Hours", 0)
            tardiness = row.get("Tardiness Hours", 0)
            absent = row.get("Absent Hours", 0)
            bonus = row.get("Current Bonus", 20)
            chance = row.get("Current Chance", 0)
            print(f"bonus: {bonus}")
            print(f"chance: {chance}")

            try:
                scheduled = float(scheduled or 0)
                attended = float(attended or 0)
                tardiness = float(tardiness or 0)
                absent = float(absent or 0)
                bonus = int(bonus or 20)
                chance = int(chance or 0)
            except Exception:
                continue

            if name and date:
                staff = staffList.get(name)
                if not staff:
                    staff = {"name": name, "attendance": {}, "bonus": {}}
                    staffList[name] = staff

                staff.setdefault("attendance", {})[date] = {
                    "scheduled": scheduled,
                    "attended": attended,
                    "tardiness": tardiness,
                    "absent": absent
                }

                # Update bonus info
                bonus_info = staff.setdefault("bonus", {})
                bonus_info["current_bonus"] = bonus
                bonus_info["current_chance"] = chance

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
        "bonus": {
            "current_bonus": 0, 
            "current_chance": 0, 
            "bonus_history": {}, 
            "bonus_updated": {}
        },
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

def delete_staff(name):
    if not name or name not in staffList:
        return
    confirm = messagebox.askyesno("Delete Staff", f"Are you sure you want to delete {name}?")
    if confirm:
        del staffList[name]
        save_staff()
        clear_table()
        update_btn("disabled")
        messagebox.showinfo("Deleted", f"{name} has been removed.")

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


bonusList = [20, 40, 50]
def calculate_bonus_logic(staff, perfect_attendance):
    current_bonus = staff["bonus"].get("current_bonus", 0)
    current_chance = staff["bonus"].get("current_chance", 0)

    if perfect_attendance:
        if current_bonus == 50:
            current_bonus = 20
            current_chance += 1
        else:
            next_index = bonusList.index(current_bonus) + 1
            current_bonus = bonusList[next_index]
    else:
        if current_chance > 0:
            current_chance -= 1
        else:
            current_bonus = 0

    staff["bonus"]["current_bonus"] = current_bonus
    staff["bonus"]["current_chance"] = current_chance

def calculate_bonus_popup():
    if not current_name or current_name not in staffList:
        return

    staff = staffList[current_name]
    # now_month = datetime.now().strftime("%Y-%m")
    selected_month = month_var.get()  # e.g., "2025-04"
    

    # Get or initialize bonus info
    bonus_info = staff.get("bonus", {})
    bonus_updated = bonus_info.get("bonus_updated", {})
    current_bonus = bonus_info.get("current_bonus", 0)
    current_chance = bonus_info.get("current_chance", 0)
    bonus_history = bonus_info.setdefault("bonus_history", {})
    overwrite_log = bonus_info.setdefault("overwrite_log", {})

    new_perfect = perfect_var.get()
    
    # If already recorded, ask to overwrite only if new difference
    if selected_month in bonus_updated:
        previous_perfect = bonus_updated[selected_month]
        if previous_perfect == new_perfect: 
            messagebox.showinfo(
                "Already Recorded", 
                f"Bonus already recorded for {selected_month} with the same attendance status."
            )
            return 
        else: 
            overwrite = messagebox.askyesno(
                "Record Bonus Record?", 
                f"Bonus for {selected_month} was previously mark as "
                f"{'Perfect' if previous_perfect else 'Imperfect'}.\n"
                f"Do you want to replace it with "
                f"{'Perfect' if new_perfect else 'Imperfect'}?"
            )
            if not overwrite: 
                return # Cancel if user don't want to overwrite
            
            # save old record before overwriting
            old_record = bonus_history.get(selected_month)
            if old_record: 
                overwrite_log.setdefault(selected_month, []).append(old_record)
                


    # Check if checkbox was checked for perfect attendance
    if new_perfect:
        # for new staff
        if current_bonus == 0: 
            current_bonus = 20
            print(f"test: {current_name}'s current bonus is {current_bonus}")
        else: 
            if current_bonus == 50:
                current_bonus = 20
                current_chance += 1
            else:
                next_index = bonusList.index(current_bonus) + 1
                current_bonus = bonusList[next_index]
    else:
        # Assume imperfect attendance
        if current_chance > 0:
            current_chance -= 1
        else:
            current_bonus = 0

    # Save bonus info
    bonus_updated[selected_month] = new_perfect # <-- store true/false
    bonus_history[selected_month] = {
        "bonus": current_bonus, 
        "chance": current_chance
    }
    staff["bonus"] = {
        "current_bonus": current_bonus,
        "current_chance": current_chance,
        "bonus_history": bonus_history, 
        "bonus_updated": bonus_updated,
        "overwrite_log": overwrite_log
    }

    save_staff()
    show_staff(current_name)

    # Show popup
    messagebox.showinfo("Bonus Updated", f"Current Bonus: {current_bonus}\nCurrent Chance: {current_chance}")


# Update the whole table after selecting specific month
def update_table(): 
    clear_table()
    selected_month = month_var.get()
    if not selected_month:
        print("no month selected")
        list_all_staff()  # If no month selected, show all staff
        return
    
    if current_name: 
        print("now is ", selected_month)
        print("Here is ", current_name)
        show_staff(current_name) 
        # now just showing the staff info for the current month

    else: 
        for name, staff_data in sorted(staffList.items()):
            monthly_stats = calc_monthly_stats(staff_data.get("attendance", {}))
            month_stat = monthly_stats.get(selected_month, {})
            bonus_info = staff_data.get("bonus", {})
        
            bonus = bonus_info["current_bonus"]
            chance = bonus_info["current_chance"]
            scheduled = month_stat.get("scheduled", 0)
            attended = month_stat.get("attended", 0)
            tardiness = month_stat.get("tardiness", 0)
            absent = month_stat.get("absent", 0)
            attendance_pct = round((attended / scheduled * 100) if scheduled else 0, 2)

            tree.insert("", "end", values=(
                name,
                bonus, 
                chance, 
                scheduled,
                attended,
                tardiness,
                absent,
                f"{attendance_pct}%",
                staff_data.get("lastUpdate", "N/A")
            ))


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

# Buttons of basic functions
frame_controls = tk.Frame(root)
frame_controls.pack(pady=5)
tk.Button(frame_controls, text="List All", command=list_all_staff).pack(side=tk.LEFT, padx=5)
tk.Button(frame_controls, text="Add Staff", command=toggle_add_frame).pack(side=tk.LEFT, padx=5)
tk.Button(frame_controls, text="Export to Excel", command=export_to_excel).pack(side=tk.LEFT, padx=5)
tk.Button(frame_controls, text="Import Excel", command=import_excel).pack(side=tk.LEFT, pady=5)
frame_bonus = tk.Frame(root)
frame_bonus.pack(pady=5)
perfect_var = tk.BooleanVar()
perfect_check = tk.Checkbutton(frame_bonus, text="Perfect Attendance", variable=perfect_var)
perfect_check.pack(side="left", padx=5) 
bonusBtn = tk.Button(frame_bonus, text="Calculate Bonus", command=calculate_bonus_popup)
bonusBtn.pack(side="left", padx=5)


frame_add = tk.Frame(root)
frame_add_visible = False
tk.Label(frame_add, text="New Staff Name:").pack(side=tk.LEFT)
new_entry = tk.Entry(frame_add)
new_entry.pack(side=tk.LEFT, padx=5)
new_entry.bind("<Return>", lambda event: add_staff(new_entry.get()))
tk.Button(frame_add, text="Confirm", command=lambda: add_staff(new_entry.get())).pack(side=tk.LEFT)

# Month selector
month_var = tk.StringVar()
month_choices = [f"{y}-{m:02d}" for y in range(2023, 2026) for m in range(1, 13)]
month_var.set(datetime.now().strftime("%Y-%m"))
month_dropdown = ttk.Combobox(frame_controls, textvariable=month_var, values=month_choices, state="readonly", width=10)
month_dropdown.pack(side=tk.LEFT, padx=5)
month_dropdown.bind("<<ComboboxSelected>>", lambda e: update_table())



frame_tree = tk.Frame(root)
frame_tree.pack(pady=15, fill="both", expand=True)

# Treeview
columns = ("Name", "Bonus", "Chance", "Schedule Hrs", "Attended Hrs", "Total Tardiness", "Total Absence", "Attendance %", "Last Updated")
tree = ttk.Treeview(frame_tree, columns=columns, show="headings", xscrollcommand=lambda *args: h_scroll.set(*args))

# Setup headings and column widths
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER, width=120)

# Horizontal scrollbar
h_scroll = tk.Scrollbar(frame_tree, orient="horizontal", command=tree.xview)
h_scroll.pack(side="bottom", fill="x")

# Vertical scrollbar
v_scroll = tk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
v_scroll.pack(side="right", fill="y")
tree.configure(yscrollcommand=v_scroll.set)

# Pack Treeview last so it fills remaining space
tree.pack(side="left", fill="both", expand=True)

# Bind row selection event
tree.bind("<<TreeviewSelect>>", on_row_select)

# Actions buttons at the buttom
frame_actions = tk.Frame(root)
frame_actions.pack(pady=10)
recordBtn = tk.Button(frame_actions, text="Record Attendance", command=record_attendance, state="disabled")
deleteBtn = tk.Button(frame_actions, text="Delete", command=lambda: delete_staff(current_name), state="disabled")
recordBtn.pack(side=tk.LEFT, padx=10)
deleteBtn.pack(side=tk.LEFT, padx=10)

root.mainloop()
