import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
from dashboard import AdminDashboard
from shop import CustomerShop

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456789",
    database="project"
)
db = conn.cursor()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("User System")
root.geometry("500x400")

def signup_window():
    win = ctk.CTkToplevel(root)
    win.title("Sign Up")
    win.geometry("400x400")

    ctk.CTkLabel(win, text="--- Sign Up ---", font=("Arial", 20, "bold")).pack(pady=20)
    name_entry = ctk.CTkEntry(win, placeholder_text="Name", width=300)
    name_entry.pack(pady=10)
    email_entry = ctk.CTkEntry(win, placeholder_text="Email", width=300)
    email_entry.pack(pady=10)
    pass_entry = ctk.CTkEntry(win, placeholder_text="Password", show="*", width=300)
    pass_entry.pack(pady=10)

    def do_signup():
        name = name_entry.get()
        email = email_entry.get()
        password = pass_entry.get()
        db.execute("SELECT * FROM customer WHERE email = %s", (email,))
        existing_user = db.fetchall()
        if existing_user:
            messagebox.showerror("Error", "Email Already Exists!")
        else:
            sql = "INSERT INTO customer (name, email, password) VALUES (%s,%s,%s)"
            values = (name, email, password)
            db.execute(sql, values)
            conn.commit()
            messagebox.showinfo("Success", "Account Created Successfully!")
            win.destroy()

    ctk.CTkButton(win, text="Sign Up", width=200, command=do_signup).pack(pady=20)

def login_window():
    win = ctk.CTkToplevel(root)
    win.title("Login")
    win.geometry("400x300")

    ctk.CTkLabel(win, text="--- Login ---", font=("Arial", 20, "bold")).pack(pady=20)
    email_entry = ctk.CTkEntry(win, placeholder_text="Email", width=300)
    email_entry.pack(pady=10)
    pass_entry = ctk.CTkEntry(win, placeholder_text="Password", show="*", width=300)
    pass_entry.pack(pady=10)

    def do_login():
      email = email_entry.get()
      password = pass_entry.get()
      db.execute("SELECT * FROM customer WHERE email = %s AND password = %s", (email, password))
      user = db.fetchone()
      if user:
          messagebox.showinfo("Success", f"Welcome Back {email}!")
          win.destroy()
          if email == "smz@gmail.com" and password == "123456789smz":
              root.destroy()
              app = AdminDashboard()
              app.mainloop()
          else:
              customer_id = user[0]
              root.destroy()
              app = CustomerShop(customer_id)
              app.mainloop()
      else:
          messagebox.showerror("Error", "Wrong Email or Password!")


    ctk.CTkButton(win, text="Login", width=200, command=do_login).pack(pady=20)

ctk.CTkLabel(root, text="User System", font=("Arial", 26, "bold")).pack(pady=30)
ctk.CTkButton(root, text="Sign Up", width=250, height=40, fg_color="#44bd32", hover_color="#27ae60",
              text_color="white", font=("Arial", 16, "bold"), command=signup_window).pack(pady=15)
ctk.CTkButton(root, text="Login", width=250, height=40, fg_color="#2980b9", hover_color="#1f618d",
              text_color="white", font=("Arial", 16, "bold"), command=login_window).pack(pady=15)
ctk.CTkButton(root, text="Exit", width=250, height=40, fg_color="#e74c3c", hover_color="#c0392b",
              text_color="white", font=("Arial", 16, "bold"), command=root.quit).pack(pady=15)

root.mainloop()