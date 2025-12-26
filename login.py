import tkinter as tk
from tkinter import messagebox
import sys
import os

# --- IMPORT DASHBOARD ---
# Ye zaroori hai taaki hum dashboard class ko use kar sakein
import dashboard 

def verify():
    u = user_entry.get()
    p = pass_entry.get()
    
    if u == "admin" and p == "admin123":
        root.destroy() # Login window band karo
        
        # --- OPEN DASHBOARD DIRECTLY ---
        # Ye line dashboard.py ke class ko call karegi
        app = dashboard.AdminDashboard()
        app.root.mainloop()
        
    else:
        messagebox.showerror("Error", "Invalid Credentials")

# --- UI SETUP ---
root = tk.Tk()
root.title("Login - Traffic Admin")
root.geometry("350x450")
root.configure(bg="#2f3640")

tk.Label(root, text="🔐", font=("Arial", 60), bg="#2f3640", fg="#00cec9").pack(pady=40)
tk.Label(root, text="ADMIN LOGIN", font=("Arial", 14, "bold"), bg="#2f3640", fg="white").pack()

# Username
tk.Entry(root, font=("Arial", 12), width=25, bg="white", bd=0, textvariable=tk.StringVar()).pack(pady=10)
user_entry = root.winfo_children()[-1]
user_entry.insert(0, "admin") # Auto-fill
user_entry.focus() 

# Password
tk.Entry(root, font=("Arial", 12), width=25, bg="white", bd=0, show="*", textvariable=tk.StringVar()).pack(pady=10)
pass_entry = root.winfo_children()[-1]

# Enter Key Support
root.bind('<Return>', lambda event: verify())

tk.Button(root, text="LOGIN", bg="#00cec9", fg="white", font=("Arial", 12, "bold"), width=20, height=2, bd=0, command=verify).pack(pady=30)

root.mainloop()