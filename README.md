# Attendance Calculator Application

## Introduction
Attendance Calculator is a Windows-based desktop application (also provided as a Python source file) designed to help organizations track and manage employee attendance more effectively. The tool calculates key attendance metrics and determines monthly bonuses based on attendance performance.

## Feature
* Attendance Tracking: Record weekly attendance hours including scheduled, attended, tardiness, and absence.

* Monthly Bonus Calculation: Automatically calculates bonus progression or resets based on attendance quality, with logic for perfect and imperfect attendance.

* Editable Records: Easily modify existing attendance or bonus data.

* Bonus History: Keep a monthly log of bonuses and "chance" values per employee.

* CSV Import/Export: Import historical data or export current staff data to CSV files for backup or external analysis.

* User-Friendly Interface: Intuitive UI built with Tkinter, including table views and popup dialogs.

## Packaging
This application is distributed as a standalone `.exe` for Windows users. The `.exe` file can be run directly without requiring Python installation. 
 

If building manually, you can generate the executable using:
```
pyinstaller --onefile calculator.py

```
To include a custom icon: 
```
pyinstaller --onefile --icon=your_icon.ico calculator.py
```

## Future Improvement
* Yearly Overview: Add a summary view for yearly attendance and bonus statistics.

* Graphical Reports: Visual charts for attendance trends and bonus progress.

* User Roles: Support for admin/viewer roles or multi-user environments.

## File Structure
```
Attendance_Calculator/
|-- calculator.py       # Main application script
|-- README.md 
|-- staff.json          # Local data file
|-- dist/               # Output folder after building .exe
|-- attendance.ico      # Optional app icon

```