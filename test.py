# This code is for storing the staff information under the "staff.json"
import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


# === Load and Save Functions ===
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def load_staff(): 
    path = resource_path("staff.json")
    with open(path , "r") as file: 
        return json.load(file)

def save_staff(): 
    path = resource_path("staff.json")
    with open(path , "w") as file: 
        json.dump(staffList, file, indent=4)

# # Default data (in case staff.json doesn't exist yet)
# DEFAULT_STAFF = {}

# # Path to store staff.json in the user's AppData or current dir
# def get_data_path():
#     appdata = os.getenv('APPDATA') or os.getcwd()
#     return os.path.join(appdata, "staff.json")

# def load_staff():
#     path = get_data_path()
#     if not os.path.exists(path):
#         with open(path, "w") as f:
#             json.dump(DEFAULT_STAFF, f, indent=4)
#     with open(path, "r") as f:
#         return json.load(f)

# def save_staff():
#     path = get_data_path()
#     with open(path, "w") as f:
#         json.dump(staffList, f, indent=4)

staffList = load_staff()
bonus = [20, 40, 50]
current_name = None

# === GUI Functional Logic ===
def find_staff(): 
    global current_name
    name = entry.get().strip()
    if name in staffList: 
        current_name = name
        show_staff(name)
        update_btn("normal")
    else: 
        messagebox.showerror("Error", "Staff not found")
        update_btn("disabled")

def record_attended(): 
    staff = staffList[current_name]
    bonusIdx = staff["currBonus"]
    chance = staff["currChance"]
    if bonusIdx < len(bonus) - 1: 
        bonusIdx += 1
    else: 
        bonusIdx = 0
        chance += 1
    staff["currBonus"] = bonusIdx
    staff["currChance"] = chance
    staff["lastUpdate"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_staff()
    show_staff(current_name)
    messagebox.showinfo("Success", f"{current_name}'s bonus increased!")

def record_absent():
    staff = staffList[current_name]
    bonusIdx = staff["currBonus"]
    chance = staff["currChance"]
    if chance > 0: 
        chance -= 1
        msg = f"{current_name} used a chance. Remaining: {chance}"
    else: 
        bonusIdx = 0
        msg = f"{current_name}'s bonus reset to 20"
    staff["currBonus"] = bonusIdx
    staff["currChance"] = chance
    staff["lastUpdate"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_staff()
    show_staff(current_name)
    messagebox.showinfo("Updated", msg)

def delete_staff(name): 
    if name in staffList: 
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete {name}?")
        if confirm: 
            del staffList[name]
            save_staff()
            clear_table()
            update_btn("disabled")
            messagebox.showinfo("Deleted", f"{name} removed.")

def edit_staff():
    if not current_name:
        return
    edit_win = tk.Toplevel(root)
    edit_win.title(f"Edit {current_name}")

    tk.Label(edit_win, text="Bonus Index (0-2):").pack()
    bonus_entry = tk.Entry(edit_win)
    bonus_entry.insert(0, staffList[current_name]["currBonus"])
    bonus_entry.pack()

    tk.Label(edit_win, text="Chance:").pack()
    chance_entry = tk.Entry(edit_win)
    chance_entry.insert(0, staffList[current_name]["currChance"])
    chance_entry.pack()

    def save_edits():
        try:
            new_bonus = int(bonus_entry.get())
            new_chance = int(chance_entry.get())
            if new_bonus < 0 or new_bonus > 2 or new_chance < 0:
                raise ValueError
            staffList[current_name]["currBonus"] = new_bonus
            staffList[current_name]["currChance"] = new_chance
            staffList[current_name]["lastUpdate"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_staff()
            show_staff(current_name)
            edit_win.destroy()
        except:
            messagebox.showerror("Invalid input", "Please enter valid numbers.")

    tk.Button(edit_win, text="Save", command=save_edits).pack(pady=5)

def add_staff(name):
    name = name.strip()
    if not name:
        messagebox.showerror("Error", "Name cannot be empty.")
        return
    if name in staffList:
        messagebox.showerror("Error", "Staff already exists.")
        return
    staffList[name] = {
        "currBonus": 0,
        "currChance": 1, 
        "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    save_staff()
    messagebox.showinfo("Added", f"{name} has been added.")
    new_entry.delete(0, tk.END)
    toggle_add_frame()
    show_staff(name)

def list_all_staff():
    clear_table()
    for name in staffList:
        show_staff(name, single=False)
    update_btn("disabled")

def update_btn(state): 
    yesBtn.config(state=state)
    noBtn.config(state=state)
    delBtn.config(state=state)
    editBtn.config(state=state)

def clear_table():
    for item in tree.get_children():
        tree.delete(item)

def show_staff(name, single=True):
    if single:
        clear_table()
    staff = staffList[name]
    bonusVal = bonus[staff["currBonus"]]
    last_update = staff.get("lastUpdate", "N/A")
    tree.insert("", "end", values=(name, bonusVal, staff["currChance"], last_update))
    global current_name
    current_name = name

def toggle_add_frame():
    global frame_add_visible
    if frame_add_visible:
        frame_add.pack_forget()
        frame_add_visible = False
    else:
        frame_add.pack(pady=5)
        frame_add_visible = True

# === GUI Layout ===
root = tk.Tk()
root.title("Staff Attendance Record")
root.geometry("650x500")

# --- Search Frame ---
frame_search = tk.Frame(root)
frame_search.pack(pady=10)
tk.Label(frame_search, text="Enter Staff Name:").pack(side=tk.LEFT)
entry = tk.Entry(frame_search)
entry.pack(side=tk.LEFT, padx=5)
tk.Button(frame_search, text="Find", command=find_staff).pack(side=tk.LEFT)

# --- Control Buttons Frame ---
frame_controls = tk.Frame(root)
frame_controls.pack(pady=5)
tk.Button(frame_controls, text="List All Staff", command=list_all_staff).pack(side=tk.LEFT, padx=5)
tk.Button(frame_controls, text="Add Staff", command=toggle_add_frame).pack(side=tk.LEFT, padx=5)

# --- Add Staff Frame (Hidden Initially) ---
frame_add = tk.Frame(root)
frame_add_visible = False
tk.Label(frame_add, text="New Staff Name:").pack(side=tk.LEFT)
new_entry = tk.Entry(frame_add)
new_entry.pack(side=tk.LEFT, padx=5)
tk.Button(frame_add, text="Confirm Add", command=lambda: add_staff(new_entry.get())).pack(side=tk.LEFT)

# --- Staff Table View ---
columns = ("Name", "Current Bonus", "Current Chance", "Last Updated")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER, width=150)
tree.pack(pady=15)

# --- Action Buttons ---
frame_actions = tk.Frame(root)
frame_actions.pack(pady=10)
yesBtn = tk.Button(frame_actions, text="Yes (Attended)", command=record_attended, state="disabled")
noBtn = tk.Button(frame_actions, text="No (Absent)", command=record_absent, state="disabled")
editBtn = tk.Button(frame_actions, text="Edit", command=edit_staff, state="disabled")
delBtn = tk.Button(frame_actions, text="Delete", command=lambda: delete_staff(current_name), state="disabled")
yesBtn.pack(side=tk.LEFT, padx=10)
noBtn.pack(side=tk.LEFT, padx=10)
editBtn.pack(side=tk.LEFT, padx=10)
delBtn.pack(side=tk.LEFT, padx=10)

root.mainloop()
