import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import mysql.connector
from tkinter import messagebox

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456789",
    database="project"
)
db = conn.cursor()

class AdminDashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Admin Dashboard")
        self.geometry("1280x768")
        self.state('zoomed')
        self.configure(bg="#F8F9FA")

        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure('TFrame', background='#F8F9FA')
        self.style.configure('TLabel', background='#F8F9FA', foreground='#343A40', font=('Arial', 10))
        self.style.configure('TButton', background='#007BFF', foreground='white', font=('Arial', 10, 'bold'), borderwidth=0)
        self.style.map('TButton', background=[('active', '#0056b3')])
        self.style.configure('Card.TFrame', background='#FFFFFF', relief="flat", borderwidth=1)
        self.style.configure('Sidebar.TFrame', background='#E9ECEF')
        self.style.configure('Header.TLabel', background='#F8F9FA', foreground='#212529', font=('Arial', 16, 'bold'))

        header_frame = ttk.Frame(self, style='TFrame')
        header_frame.pack(side=tk.TOP, fill=tk.X, pady=10, padx=20)
        ttk.Label(header_frame, text="Product Management Dashboard", style='Header.TLabel').pack(side=tk.LEFT)

        main_content_frame = ttk.Frame(self, style='TFrame')
        main_content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        products_canvas = tk.Canvas(main_content_frame, bg="#F8F9FA", highlightthickness=0)
        products_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        self.products_frame = ttk.Frame(products_canvas, style='TFrame')
        products_canvas.create_window((0, 0), window=self.products_frame, anchor="nw")

        scrollbar = ttk.Scrollbar(products_canvas, orient="vertical", command=products_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        products_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.products_frame.bind("<Configure>", lambda e: products_canvas.configure(scrollregion=products_canvas.bbox("all")))
        self.bind_all("<MouseWheel>", lambda event: products_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        sidebar_frame = ttk.Frame(main_content_frame, width=250, style='Sidebar.TFrame')
        sidebar_frame.pack(side=tk.RIGHT, fill=tk.Y)
        sidebar_frame.pack_propagate(False)
        
        self.placeholder_photo = self.create_placeholder_image(120, 90, '#CCCCCC')

        self.populate_products(self.products_frame)
        self.populate_sidebar(sidebar_frame)

    def create_placeholder_image(self, width, height, color):
        img = Image.new('RGB', (width, height), color=color)
        return ImageTk.PhotoImage(img)

    def populate_products(self, parent_frame):
      try:
          db.execute("SELECT id, productName, category, quantity, price, imagepath FROM stock")
          products = db.fetchall()
      except mysql.connector.Error as err:
          messagebox.showerror("Database Error", f"Error loading products: {err}")
          return
      for i, product in enumerate(products):
          product_id, name, category, quantity, price, image_path = product
          row, col = divmod(i, 4)
          card = ttk.Frame(parent_frame, style='Card.TFrame', padding="15")
          card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
          if image_path:
              try:
                  img = Image.open(image_path)
                  img = img.resize((120, 90))
                  photo = ImageTk.PhotoImage(img)
              except:
                  photo = self.placeholder_photo
          else:
              photo = self.placeholder_photo
          image_label = tk.Label(card, image=photo, bg="#E9ECEF", relief="solid", borderwidth=1)
          image_label.image = photo
          image_label.pack(pady=(0, 10))
          ttk.Label(card, text=name, font=('Arial', 11, 'bold'), anchor="w", background='#FFFFFF').pack(fill='x')
          ttk.Label(card, text=f"Category: {category}", font=('Arial', 9), anchor="w", background='#FFFFFF', foreground='#6C757D').pack(fill='x')
          ttk.Label(card, text=f"Price: ${price:.2f}", font=('Arial', 9), anchor="w", background='#FFFFFF', foreground='#6C757D').pack(fill='x')
          ttk.Label(card, text=f"Quantity: {quantity}", font=('Arial', 9), anchor="w", background='#FFFFFF', foreground='#6C757D').pack(fill='x')
          ttk.Separator(card, orient='horizontal').pack(fill='x', pady=10)
          ttk.Button(card, text="Change Quantity", style='TButton', command=lambda pid=product_id, current_qty=quantity: self.open_change_quantity_window(pid, current_qty)).pack(fill='x', pady=3)
          ttk.Button(card, text="Remove Item", style='TButton', command=lambda item_id=product_id: self.remove_item(item_id)).pack(fill='x', pady=3)

      for i in range(4):
          parent_frame.grid_columnconfigure(i, weight=1)


    def populate_sidebar(self, parent_frame):
        ttk.Label(parent_frame, text="Actions", font=('Arial', 13, 'bold'), background='#E9ECEF', foreground='#343A40').pack(pady=(20, 10), padx=15)
        ttk.Button(parent_frame, text="Create New Item", command=self.open_create_item_window, style='TButton').pack(pady=5, padx=15, fill='x')
        ttk.Button(parent_frame, text="Placed Orders", command=self.open_orders_window, style='TButton').pack(pady=5, padx=15, fill='x')

    def refresh_products(self):
      for widget in self.products_frame.winfo_children():
          widget.destroy()
      self.populate_products(self.products_frame)

    def remove_item(self, item_id):
      confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to remove this item?")
      if confirm:
          try:
              db.execute("DELETE FROM stock WHERE id = %s", (item_id,))
              conn.commit()
              messagebox.showinfo("Success", "Item removed successfully.")
              self.refresh_products()
          except mysql.connector.Error as err:
              messagebox.showerror("Database Error", f"Error removing item: {err}")
    def open_orders_window(self):
      win = tk.Toplevel(self)
      win.title("Placed Orders")
      win.geometry("800x600")
      win.grab_set()
      frame = ttk.Frame(win, padding=10)
      frame.pack(fill=tk.BOTH, expand=True)
      try:
          db.execute("SELECT id, customerId, date, status, address FROM PlacedOrders ORDER BY date DESC")
          orders = db.fetchall()
      except mysql.connector.Error as err:
          messagebox.showerror("Database Error", f"Error fetching orders: {err}")
          return

      for order in orders:
          order_id, cust_id, date, status, address = order
    
          header = ttk.Label(frame, text=f"Order #{order_id} — {date.strftime('%Y-%m-%d %H:%M')} — Status: {status}", font=('Arial', 12, 'bold'))
          header.pack(anchor="w", pady=(10, 5))

          ttk.Label(frame, text=f"Customer ID: {cust_id} | Address: {address}").pack(anchor="w")

          try:
              db.execute("""
                  SELECT s.productName, d.quantity, d.price
                  FROM order_details d
                  JOIN stock s ON d.product_id = s.id
                  WHERE d.order_id = %s
              """, (order_id,))
              items = db.fetchall()
          except mysql.connector.Error as err:
              messagebox.showerror("Database Error", f"Error fetching order items: {err}")
              items = []

          total = 0
          for name, qty, price in items:
              subtotal = qty * price
              total += subtotal
              ttk.Label(frame, text=f"  {name} x {qty} @ ${price:.2f} = ${subtotal:.2f}").pack(anchor="w")

          ttk.Label(frame, text=f"  Total: ${total:.2f}", font=('Arial', 10, 'italic')).pack(anchor="w")

          status_var = tk.StringVar(value=status)
          status_options = ["Pending", "Shipped", "Delivered", "Canceled"]
          status_menu = ttk.OptionMenu(frame, status_var, status, *status_options)
          status_menu.pack(anchor="w", pady=5)

          def update_status(order_id=order_id, stat_var=status_var):
              new_stat = stat_var.get()
              try:
                  db.execute("UPDATE PlacedOrders SET status = %s WHERE id = %s", (new_stat, order_id))
                  conn.commit()
                  messagebox.showinfo("Success", f"Order #{order_id} status updated to {new_stat}")
                  win.destroy()
                  self.open_orders_window()
              except mysql.connector.Error as err:
                  messagebox.showerror("Database Error", f"Could not update status: {err}")

          ttk.Button(frame, text="Update Status", command=update_status).pack(anchor="w", pady=(0, 10))
          ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=5)

    def open_change_quantity_window(self, product_id, current_quantity):
      win = tk.Toplevel(self)
      win.title("Change Quantity")
      win.geometry("300x150")
      win.configure(bg="#F8F9FA")
      win.resizable(False, False)
      win.transient(self)
      win.grab_set()

      ttk.Label(win, text="Enter new quantity:", background="#F8F9FA", font=("Arial", 11)).pack(pady=(20, 10))
      qty_var = tk.StringVar(value=str(current_quantity))
      qty_entry = ttk.Entry(win, textvariable=qty_var)
      qty_entry.pack(pady=5)
      def update_quantity():
          try:
              new_qty = int(qty_var.get())
              if new_qty < 0:
                  raise ValueError("Quantity must be non-negative.")
              db.execute("UPDATE stock SET quantity = %s WHERE id = %s", (new_qty, product_id))
              conn.commit()
              messagebox.showinfo("Success", "Quantity updated successfully.")
              win.destroy()
              self.refresh_products()
          except ValueError:
              messagebox.showerror("Invalid Input", "Please enter a valid integer.")
          except mysql.connector.Error as err:
              messagebox.showerror("Database Error", f"Error: {err}")
      ttk.Button(win, text="Update", command=update_quantity, style='TButton').pack(pady=15)

    def open_create_item_window(self):
        CreateItemWindow(self)



class CreateItemWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.title("Create New Item")
        self.geometry("450x450")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self.configure(bg="#F8F9FA")

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TLabel', background='#F8F9FA', foreground='#343A40', font=('Arial', 10))
        self.style.configure('TEntry', fieldbackground='white', foreground='#343A40', font=('Arial', 10))
        self.style.configure('TRadiobutton', background='#F8F9FA', foreground='#343A40', font=('Arial', 10))
        self.style.configure('Add.TButton', background='#28A745', foreground='white', font=('Arial', 10, 'bold'), borderwidth=0)
        self.style.map('Add.TButton', background=[('active', '#218838')])

        frame = ttk.Frame(self, padding="30", style='TFrame')
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Product Name:", anchor="w").grid(row=0, column=0, sticky="w", pady=8, padx=5)
        self.name_entry = ttk.Entry(frame, width=40, style='TEntry')
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=8, padx=5)

        ttk.Label(frame, text="Price:", anchor="w").grid(row=1, column=0, sticky="w", pady=8, padx=5)
        self.price_entry = ttk.Entry(frame, style='TEntry')
        self.price_entry.grid(row=1, column=1, sticky="ew", pady=8, padx=5)

        ttk.Label(frame, text="Quantity:", anchor="w").grid(row=2, column=0, sticky="w", pady=8, padx=5)
        self.quantity_entry = ttk.Entry(frame, style='TEntry')
        self.quantity_entry.grid(row=2, column=1, sticky="ew", pady=8, padx=5)

        ttk.Label(frame, text="Category:", anchor="w").grid(row=3, column=0, sticky="w", pady=8, padx=5)
        category_frame = ttk.Frame(frame, style='TFrame')
        category_frame.grid(row=3, column=1, sticky="w", pady=8, padx=5)
        
        self.category_var = tk.StringVar(value="men")
        ttk.Radiobutton(category_frame, text="Men", variable=self.category_var, value="men", style='TRadiobutton').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(category_frame, text="Women", variable=self.category_var, value="women", style='TRadiobutton').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(category_frame, text="Children", variable=self.category_var, value="children", style='TRadiobutton').pack(side=tk.LEFT, padx=5)

        self.uploaded_image_path = None
        self.image_status_label = ttk.Label(frame, text="No image selected.", foreground="red", background='#F8F9FA')
        
        ttk.Label(frame, text="Product Image:", anchor="w").grid(row=4, column=0, sticky="w", pady=8, padx=5)
        image_button = ttk.Button(frame, text="Upload Image", command=self.upload_image_action, style='TButton')
        image_button.grid(row=4, column=1, sticky="ew", pady=8, padx=5)

        self.image_status_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=10)

        create_button = ttk.Button(frame, text="Add Item", command=self.create_item, style='Add.TButton')
        create_button.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(30, 0), padx=5)

        frame.columnconfigure(1, weight=1)

    def upload_image_action(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image Files", ".png;.jpg;.jpeg;.gif")])
        if filepath:
            self.uploaded_image_path = filepath
            print(f"Selected image: {filepath}")
            self.image_status_label.config(text="Image selected successfully!", foreground="green")
        else:
            self.image_status_label.config(text="No image selected.", foreground="red")

    def create_item(self):
      product_name = self.name_entry.get().strip()
      price = self.price_entry.get().strip()
      quantity = self.quantity_entry.get().strip()
      category = self.category_var.get()
      image_path = self.uploaded_image_path
      if not product_name or not price or not quantity:
          messagebox.showerror("Error", "Please fill in all required fields.")
          return
      try:
          price = float(price)
          quantity = int(quantity)
      except ValueError:
          messagebox.showerror("Error", "Price must be a number and Quantity must be an integer.")
          return
      try:
          sql = "INSERT INTO stock (productName, category, quantity, price, imagepath) VALUES (%s, %s, %s, %s, %s)"
          values = (product_name, category, quantity, price, image_path)
          db.execute(sql, values)
          conn.commit()
          messagebox.showinfo("Success", "Product added successfully!")
          self.parent.refresh_products()
          self.destroy()
      except mysql.connector.Error as err:
          messagebox.showerror("Database Error", f"Error: {err}")
      print(f"Creating item: {product_name}, Price: {price}, Qty: {quantity}, Cat: {category}, Img: {image_path}")
      self.destroy()

if __name__ == "__main__":
    app = AdminDashboard()
    app.mainloop()