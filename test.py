import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Load staff data
def load_staff(): 
    with open("staff.json", "r") as file: 
        return json.load(file)

# Store staff data
def save_staff(): 
    with open("staff.json", "w") as file: 
        json.dump(staffList, file, indent=4)

staffList = load_staff()
bonus = [20, 40, 50]


def find_staff(): 
    global current_name
    name = entry.get()
    if name in staffList: 
        current_name = name
        staff = staffList[name]

        # Clear table and Insert info
        for item in tree.get_children(): 
            tree.delete(item)
        bonusVal = bonus[staff["currBonus"]]
        last_update = staff.get("lastUpdate", "N/A")
        tree.insert("", "end", values=(name, bonusVal, staff["currChance"], last_update))
        update_btn(state="normal")
    
    else: 
        messagebox.showerror("Error", "Staff not found")
        update_btn(state="disabled")


# Button State Management
def update_btn(state): 
    yesBtn.config(state=state)
    noBtn.config(state=state)
    delBtn.config(state=state)
    editBtn.config(state=state)


# UPDATING FUNCTIONS HERE
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
    refresh()
    messagebox.showinfo("Success", f"{current_name}'s bonus increased!")

def record_absent():
    staff = staffList[current_name]
    bonusIdx = staff["currBonus"]
    chance = staff["currChance"]
    if chance > 0: 
        chance -= 1
        msg = f"{current_name} used a chance. Remaining: {staff['currChance']}"
    else: 
        bonusIdx = 0
        msg = f"{current_name}'s bonus reset to 20"
    staff["currBonus"] = bonusIdx
    staff["currChance"] = chance
    staff["lastUpdate"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_staff()
    refresh()
    messagebox.showinfo("Updated", msg)


def refresh(): 
    staff = staffList[current_name]
    for item in tree.get_children():
        tree.delete(item)
    bonusVal = bonus[staff["currBonus"]]
    last_update = staff.get("lastUpdate", "N/A")
    tree.insert("", "end", values=(current_name, bonusVal, staff["currChance"], last_update))

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
    toggle_add_frame() # hide form after adding
    refresh_table_with(name)

def refresh_table_with(name):
    for item in tree.get_children():
        tree.delete(item)
    staff = staffList[name]
    bonusVal = bonus[staff["currBonus"]]
    last_update = staff.get("lastUpdate", "N/A")
    tree.insert("", "end", values=(name, bonusVal, staff["currChance"], last_update))
    global current_name
    current_name = name
    update_btn("normal")


def delete_staff(name): 
    if name in staffList: 
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete {name}?")
        if confirm: 
            del staffList[name]
            save_staff()
            refresh()
            update_btn(state="disabled")
            messagebox.showinfo("Deleted", f"{name} removed.")
            refresh()
        else: 
            messagebox.showerror("Error", "No staff selected.")


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
            refresh()
            edit_win.destroy()
        except:
            messagebox.showerror("Invalid input", "Please enter valid numbers.")

    tk.Button(edit_win, text="Save", command=save_edits).pack(pady=5)

def toggle_add_frame():
    global frame_add_visible
    if frame_add_visible:
        frame_add.pack_forget()
        frame_add_visible = False
    else:
        frame_add.pack(pady=10)
        frame_add_visible = True

def list_all_staff():
    for item in tree.get_children():
        tree.delete(item)
    for name, staff in staffList.items():
        bonusVal = bonus[staff["currBonus"]]
        last_update = staff.get("lastUpdate", "N/A")
        tree.insert("", "end", values=(name, bonusVal, staff["currChance"], last_update))
    update_btn("disabled")


# Build GUI
root = tk.Tk()
root.title("Staff Attendance Record")
root.geometry("600x400")


# Top frame (input + search)
frame_top = tk.Frame(root)
frame_top.pack(pady=10)

tk.Label(frame_top, text="Enter the Staff Name: ").pack(side=tk.LEFT)
entry = tk.Entry(frame_top)
entry.pack(side=tk.LEFT, padx=5)
tk.Button(frame_top, text="Find Staff", command=find_staff).pack(side=tk.LEFT)


# Treeview (information display)
columns = ("Name", "Current Bonus", "Current Chance", "Last Updated")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns: 
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER, width=150)
tree.pack(pady=20)

# Actions buttons
frame_bottom = tk.Frame(root)
frame_bottom.pack(pady=10)

yesBtn = tk.Button(frame_bottom, text="Yes", command=record_attended, state="disabled")
yesBtn.pack(side=tk.LEFT, padx=10)
noBtn = tk.Button(frame_bottom, text="No", command=record_absent, state="disabled")
noBtn.pack(side=tk.LEFT, padx=10)

delBtn = tk.Button(frame_bottom, text="Delete Staff", command=lambda: delete_staff(current_name), state="disabled")
delBtn.pack(side=tk.LEFT, padx=10)
editBtn = tk.Button(frame_bottom, text="Edit", command=edit_staff, state="disabled")
editBtn .pack(side=tk.LEFT, padx=10)

tk.Button(root, text="List All Staff", command=list_all_staff).pack(pady=5)

# Hidden add frame
frame_add = tk.Frame(root)
frame_add_visible = False
# Button to show/hide add form
tk.Button(root, text="Add Staff", command=toggle_add_frame).pack(pady=5)

tk.Label(frame_add, text="New Staff Name: ").pack(side=tk.LEFT)
new_entry = tk.Entry(frame_add)
new_entry.pack(side=tk.LEFT, padx=5)
tk.Button(frame_add, text="Confirm Add", command=lambda: add_staff(new_entry.get())).pack(side=tk.LEFT)

root.mainloop()