import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import mysql.connector
from datetime import datetime

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456789",
    database="project"
)
db = conn.cursor()

class CustomerShop(tk.Tk):
    def __init__(self, customer_id):
        super().__init__()
        self.customer_id = customer_id
        self.cart = []  # Format: [{'id':..., 'name':..., 'qty':..., 'price':...}]
        
        self.title("Customer Shop")
        self.geometry("1280x768")
        self.configure(bg="#F8F9FA")
        self.state('zoomed')

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#F8F9FA')
        self.style.configure('TLabel', background='#F8F9FA', foreground='#343A40', font=('Arial', 10))
        self.style.configure('Card.TFrame', background='#FFFFFF', relief="flat", borderwidth=1)

        self.placeholder_photo = self.create_placeholder_image(120, 90, '#CCCCCC')

        ttk.Label(self, text="Welcome to the Shop", font=("Arial", 20, "bold")).pack(pady=20)

        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=20)

        canvas = tk.Canvas(container, bg="#F8F9FA", highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)

        self.products_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.products_frame, anchor="nw")

        self.products_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self.populate_products()

        ttk.Button(self, text="View Cart & Confirm Order", command=self.open_cart_window).pack(pady=10)
        ttk.Button(self, text="My Orders", command=self.view_orders).pack(pady=5)


    def create_placeholder_image(self, width, height, color):
        img = Image.new('RGB', (width, height), color=color)
        return ImageTk.PhotoImage(img)

    def populate_products(self):
        db.execute("SELECT id, productName, category, quantity, price, imagepath FROM stock")
        products = db.fetchall()

        for i, product in enumerate(products):
            pid, name, category, qty, price, image_path = product
            row, col = divmod(i, 4)

            card = ttk.Frame(self.products_frame, style='Card.TFrame', padding=10)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Image
            if image_path:
                try:
                    img = Image.open(image_path).resize((120, 90))
                    photo = ImageTk.PhotoImage(img)
                except:
                    photo = self.placeholder_photo
            else:
                photo = self.placeholder_photo

            img_label = tk.Label(card, image=photo, bg="#E9ECEF")
            img_label.image = photo
            img_label.pack()

            ttk.Label(card, text=name, font=('Arial', 11, 'bold')).pack()
            ttk.Label(card, text=f"Category: {category}").pack()
            ttk.Label(card, text=f"Price: ${price:.2f}").pack()
            ttk.Label(card, text=f"Available: {qty}").pack()

            qty_var = tk.StringVar()
            ttk.Entry(card, textvariable=qty_var, width=10).pack(pady=5)

            def add_to_cart_func(pid=pid, name=name, price=price, available_qty=qty, qv=qty_var):
                self.add_to_cart(pid, name, price, available_qty, qv.get())

            ttk.Button(card, text="Add to Cart", command=add_to_cart_func).pack(pady=5)

        for i in range(4):
            self.products_frame.grid_columnconfigure(i, weight=1)

    def add_to_cart(self, pid, name, price, available_qty, qty_str):
        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError("Quantity must be > 0")
            if qty > available_qty:
                raise ValueError("Not enough stock available.")
        except ValueError as e:
            messagebox.showerror("Invalid Quantity", str(e))
            return

        # Check if already in cart
        for item in self.cart:
            if item['id'] == pid:
                item['qty'] += qty
                messagebox.showinfo("Added", f"Added {qty} more of {name} to cart.")
                return

        self.cart.append({'id': pid, 'name': name, 'qty': qty, 'price': price})
        messagebox.showinfo("Added", f"{name} added to cart.")

    def open_cart_window(self):
        if not self.cart:
            messagebox.showinfo("Cart Empty", "You have no items in your cart.")
            return

        win = tk.Toplevel(self)
        win.title("Your Cart")
        win.geometry("400x400")
        win.configure(bg="#F8F9FA")
        win.grab_set()

        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        total = 0
        for item in self.cart:
            name = item['name']
            qty = item['qty']
            price = item['price']
            subtotal = qty * price
            total += subtotal
            ttk.Label(frame, text=f"{name} x {qty} = ${subtotal:.2f}").pack(anchor="w", pady=2)

        ttk.Label(frame, text=f"Total: ${total:.2f}", font=('Arial', 12, 'bold')).pack(pady=10)

        ttk.Button(frame, text="Confirm Order", command=lambda: self.confirm_order(win)).pack(pady=10)
    def view_orders(self):
      win = tk.Toplevel(self)
      win.title("My Orders")
      win.geometry("600x500")
      win.configure(bg="#F8F9FA")
      win.grab_set()

      frame = ttk.Frame(win, padding=15)
      frame.pack(fill=tk.BOTH, expand=True)

      db.execute("SELECT id, date, status FROM PlacedOrders WHERE customerId = %s ORDER BY date DESC", (self.customer_id,))
      orders = db.fetchall()

      if not orders:
          ttk.Label(frame, text="No orders found.", font=("Arial", 12)).pack()
          return

      for order in orders:
          order_id, date, status = order
          ttk.Label(frame, text=f"Order #{order_id} - {date.strftime('%Y-%m-%d %H:%M')} - Status: {status}",
                    font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))

          # Fetch order details
          db.execute("""
              SELECT s.productName, d.quantity, d.price
              FROM order_details d
              JOIN stock s ON d.product_id = s.id
              WHERE d.order_id = %s
          """, (order_id,))
          items = db.fetchall()

          total = 0
          for name, qty, price in items:
              line = f"  {name} x{qty} = ${qty * price:.2f}"
              ttk.Label(frame, text=line).pack(anchor="w")
              total += qty * price

          ttk.Label(frame, text=f"  Total: ${total:.2f}", font=("Arial", 10, "italic")).pack(anchor="w", pady=(0, 5))
          ttk.Separator(frame, orient="horizontal").pack(fill='x', pady=5)

    def confirm_order(self, cart_window):
      if not self.cart:
          messagebox.showinfo("Cart Empty", "You have no items in your cart.")
          return
      address_win = tk.Toplevel(self)
      address_win.title("Enter Delivery Address")
      address_win.geometry("400x200")
      address_win.configure(bg="#F8F9FA")
      address_win.grab_set()

      ttk.Label(address_win, text="Please enter your delivery address:", font=("Arial", 11), background="#F8F9FA").pack(pady=15)
      address_var = tk.StringVar()
      address_entry = ttk.Entry(address_win, textvariable=address_var, width=50)
      address_entry.pack(pady=10)

      def confirm_with_address():
          address = address_var.get().strip()
          if not address:
              messagebox.showerror("Error", "Address cannot be empty.")
              return
          try:
              db.execute(
                  "INSERT INTO PlacedOrders (customerId, status, address) VALUES (%s, %s, %s)",
                  (self.customer_id, "Pending", address)
              )
              conn.commit()
              order_id = db.lastrowid
              
              for item in self.cart:
                  db.execute(
                      "INSERT INTO order_details (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                      (order_id, item['id'], item['qty'], item['price'])
                  )
                  db.execute("UPDATE stock SET quantity = quantity - %s WHERE id = %s", (item['qty'], item['id']))

              conn.commit()
              messagebox.showinfo("Order Confirmed", "Your order has been placed!")
              self.cart.clear()
              address_win.destroy()
              cart_window.destroy()
              self.refresh_shop()

          except mysql.connector.Error as err:
              messagebox.showerror("Database Error", f"Error: {err}")
              conn.rollback()

      ttk.Button(address_win, text="Confirm Order", command=confirm_with_address).pack(pady=20)


    def refresh_shop(self):
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        self.populate_products()

if __name__ == "__main__":
    app = CustomerShop(customer_id=1)
    app.mainloop()
