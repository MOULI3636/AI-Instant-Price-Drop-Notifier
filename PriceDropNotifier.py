import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import json
import os
from datetime import datetime, timedelta
import random
import webbrowser

class AmazonPriceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("🛒 Amazon Price Tracker Pro")
        self.root.geometry("1100x750")
        self.root.configure(bg="#f5f5f5")
        
        # Set colors first
        self.primary_color = "#FF9900"
        self.secondary_color = "#232F3E"
        self.success_color = "#2E8B57"
        self.danger_color = "#DC3545"
        
        # Initialize style
        self.set_style()
        
        # Product tracking list
        self.tracked_products = []
        self.load_data()
        
        # Create GUI elements
        self.create_widgets()
        
        # Start background monitoring thread
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self.monitor_prices, daemon=True)
        self.monitor_thread.start()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Add some animations
        self.flashing_alert = False
    
    def set_style(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('TFrame', background="#f5f5f5")
        self.style.configure('TLabel', background="#f5f5f5", font=('Segoe UI', 10))
        self.style.configure('TLabelFrame', background="#f5f5f5", font=('Segoe UI', 11, 'bold'), 
                           borderwidth=2, relief="groove")
        self.style.configure('TButton', font=('Segoe UI', 10), padding=8)
        self.style.configure('Treeview', font=('Segoe UI', 10), rowheight=28, 
                           background="#ffffff", fieldbackground="#ffffff")
        self.style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), 
                           background=self.secondary_color, foreground="white")
        self.style.map('TButton', 
                      background=[('active', '#e0e0e0')],
                      foreground=[('active', 'black')])
        
        # Custom button styles
        self.style.configure('Primary.TButton', foreground='white', background=self.primary_color)
        self.style.map('Primary.TButton',
                      background=[('active', '#E88B00')])
        
        self.style.configure('Success.TButton', foreground='white', background=self.success_color)
        self.style.map('Success.TButton',
                      background=[('active', '#26854A')])
        
        self.style.configure('Danger.TButton', foreground='white', background=self.danger_color)
        self.style.map('Danger.TButton',
                      background=[('active', '#C82333')])
    
    def create_widgets(self):
        # Main frame with gradient background
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with logo and title
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Logo and title
        logo_frame = ttk.Frame(header_frame)
        logo_frame.pack(side=tk.LEFT, padx=10)
        
        # Use emoji as logo or you can replace with actual image
        logo_label = ttk.Label(logo_frame, text="🛒", font=('Segoe UI', 24), 
                              foreground=self.primary_color, background="#f5f5f5")
        logo_label.pack(side=tk.LEFT)
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, padx=10)
        
        title_label = ttk.Label(title_frame, text="Amazon Price Tracker Pro", 
                               font=('Segoe UI', 18, 'bold'), foreground=self.secondary_color)
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Never miss a price drop again!", 
                                 font=('Segoe UI', 10), foreground="#666666")
        subtitle_label.pack(anchor=tk.W)
        
        # Add product section with modern card look
        add_frame = ttk.LabelFrame(main_frame, text="➕ Add New Product", padding=(15, 10, 15, 15))
        add_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Form fields
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(fill=tk.X)
        
        ttk.Label(form_frame, text="Product URL:", font=('Segoe UI', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.url_entry = ttk.Entry(form_frame, width=60, font=('Segoe UI', 10))
        self.url_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Product Name:", font=('Segoe UI', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.name_entry = ttk.Entry(form_frame, width=60, font=('Segoe UI', 10))
        self.name_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Target Price ($):", font=('Segoe UI', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.target_price_entry = ttk.Entry(form_frame, width=15, font=('Segoe UI', 10))
        self.target_price_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Add button with icon
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=1, pady=10, sticky=tk.E)
        
        add_button = ttk.Button(button_frame, text="Add Product", command=self.add_product, 
                               style='Primary.TButton')
        add_button.pack(side=tk.LEFT, ipadx=10)
        
        # Tracked products section
        products_frame = ttk.LabelFrame(main_frame, text="📊 Your Tracked Products", padding=(15, 10, 15, 15))
        products_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview with scrollbars
        tree_frame = ttk.Frame(products_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for products
        columns = ("name", "current_price", "lowest_price", "target_price", "last_drop_date", "status", "url")
        self.products_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="extended")
        
        # Configure columns
        self.products_tree.heading("name", text="Product Name", anchor=tk.W)
        self.products_tree.heading("current_price", text="Current Price", anchor=tk.CENTER)
        self.products_tree.heading("lowest_price", text="Lowest Price", anchor=tk.CENTER)
        self.products_tree.heading("target_price", text="Target Price", anchor=tk.CENTER)
        self.products_tree.heading("last_drop_date", text="Last Price Drop", anchor=tk.CENTER)
        self.products_tree.heading("status", text="Status", anchor=tk.CENTER)
        self.products_tree.heading("url", text="URL", anchor=tk.W)
        
        self.products_tree.column("name", width=250, stretch=tk.YES)
        self.products_tree.column("current_price", width=120, stretch=tk.NO, anchor=tk.CENTER)
        self.products_tree.column("lowest_price", width=120, stretch=tk.NO, anchor=tk.CENTER)
        self.products_tree.column("target_price", width=120, stretch=tk.NO, anchor=tk.CENTER)
        self.products_tree.column("last_drop_date", width=150, stretch=tk.NO, anchor=tk.CENTER)
        self.products_tree.column("status", width=150, stretch=tk.NO, anchor=tk.CENTER)
        self.products_tree.column("url", width=250, stretch=tk.YES, anchor=tk.W)
        
        # Add scrollbars
        y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.products_tree.xview)
        self.products_tree.configure(yscroll=y_scroll.set, xscroll=x_scroll.set)
        
        # Grid layout for tree and scrollbars
        self.products_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Action buttons
        buttons_frame = ttk.Frame(products_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        refresh_button = ttk.Button(buttons_frame, text="🔄 Refresh Prices", command=self.refresh_prices,
                                  style='Success.TButton')
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        remove_button = ttk.Button(buttons_frame, text="❌ Remove Selected", command=self.remove_product,
                                  style='Danger.TButton')
        remove_button.pack(side=tk.LEFT, padx=5)
        
        open_button = ttk.Button(buttons_frame, text="🌐 Open in Browser", command=self.open_in_browser)
        open_button.pack(side=tk.LEFT, padx=5)
        
        # Stats frame
        stats_frame = ttk.Frame(buttons_frame)
        stats_frame.pack(side=tk.RIGHT, padx=5)
        
        self.tracking_count = tk.StringVar()
        self.tracking_count.set(f"Tracking: {len(self.tracked_products)} products")
        stats_label = ttk.Label(stats_frame, textvariable=self.tracking_count, 
                               font=('Segoe UI', 9), foreground="#666666")
        stats_label.pack(side=tk.RIGHT)
        
        # Status bar with time
        status_bar = ttk.Frame(main_frame, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready | " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        status_label = ttk.Label(status_bar, textvariable=self.status_var, 
                               font=('Segoe UI', 9), anchor=tk.W)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Configure grid weights
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Populate tree with existing products
        self.update_products_tree()
        
        # Bind double click to open product
        self.products_tree.bind("<Double-1>", lambda e: self.open_in_browser())
    
    def add_product(self):
        url = self.url_entry.get().strip()
        name = self.name_entry.get().strip()
        target_price = self.target_price_entry.get().strip()
        
        if not url or not name or not target_price:
            messagebox.showerror("Error", "Please fill in all fields", parent=self.root)
            return
        
        try:
            target_price = float(target_price)
            if target_price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Target price must be a positive number", parent=self.root)
            return
        
        # Check if URL already exists
        for product in self.tracked_products:
            if product['url'] == url:
                messagebox.showerror("Error", "This product is already being tracked", parent=self.root)
                return
        
        # Generate random current price between 10000 and 18000
        current_price = random.uniform(10000, 25000)
        
        # Generate random last price drop date (within last 6 months)
        days_ago = random.randint(1, 180)
        last_drop_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        product = {
            'name': name,
            'url': url,
            'current_price': current_price,
            'lowest_price': current_price * random.uniform(0.7, 0.95),  # Random lower price
            'target_price': target_price,
            'last_drop_date': last_drop_date,
            'status': "Tracking" if current_price > target_price else "Target Reached!",
            'last_checked': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.tracked_products.append(product)
        self.save_data()
        self.update_products_tree()
        
        # Clear form
        self.url_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.target_price_entry.delete(0, tk.END)
        
        # Update status
        self.status_var.set(f"Added product: {name} | " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.tracking_count.set(f"Tracking: {len(self.tracked_products)} products")
        
        # Show alert if target reached
        if product['status'] == "Target Reached!":
            self.show_alert(product)
    
    def remove_product(self):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a product to remove", parent=self.root)
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm", "Are you sure you want to remove the selected products?", 
                                 parent=self.root):
            return
        
        products_to_remove = [self.products_tree.item(item)['values'][0] for item in selected]
        self.tracked_products = [p for p in self.tracked_products if p['name'] not in products_to_remove]
        self.save_data()
        self.update_products_tree()
        
        # Update status
        if len(products_to_remove) == 1:
            self.status_var.set(f"Removed product: {products_to_remove[0]} | " + 
                              datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            self.status_var.set(f"Removed {len(products_to_remove)} products | " + 
                              datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        self.tracking_count.set(f"Tracking: {len(self.tracked_products)} products")
    
    def open_in_browser(self, event=None):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a product to open", parent=self.root)
            return
        
        item = self.products_tree.item(selected[0])
        url = item['values'][6]  # URL is the 7th column (0-indexed)
        
        try:
            webbrowser.open_new_tab(url)
            self.status_var.set(f"Opened product in browser | " + 
                              datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        except Exception as e:
            messagebox.showerror("Error", f"Could not open browser: {str(e)}", parent=self.root)
    
    def refresh_prices(self):
        if not self.tracked_products:
            messagebox.showinfo("Info", "No products to refresh", parent=self.root)
            return
        
        self.status_var.set("Refreshing prices... | " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.root.update()
        
        for product in self.tracked_products:
            self.check_price(product)
        
        self.update_products_tree()
        self.status_var.set("Prices refreshed | " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def check_price(self, product):
        try:
            # Generate random fluctuation in price (between -5% and +5%)
            fluctuation = random.uniform(-0.05, 0.05)
            new_price = product['current_price'] * (1 + fluctuation)
            
            # Occasionally simulate a price drop (10% chance)
            if random.random() < 0.1:
                drop_percent = random.uniform(0.1, 0.3)  # 10-30% drop
                new_price = product['current_price'] * (1 - drop_percent)
                product['last_drop_date'] = datetime.now().strftime("%Y-%m-%d")
            
            product['current_price'] = new_price
            
            # Update lowest price if needed
            if new_price < product['lowest_price']:
                product['lowest_price'] = new_price
            
            # Check if price dropped below target
            if new_price <= product['target_price']:
                product['status'] = "Target Reached!"
                self.show_alert(product)
            else:
                product['status'] = "Tracking"
            
            product['last_checked'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        except Exception as e:
            product['status'] = f"Error: {str(e)}"
            product['last_checked'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def show_alert(self, product):
        message = f"🎉 Price alert for {product['name']}!\n\n" \
                 f"💰 Current Price: ${product['current_price']:,.2f}\n" \
                 f"🎯 Target Price: ${product['target_price']:,.2f}\n" \
                 f"📉 Last Price Drop: {product.get('last_drop_date', 'N/A')}"
        
        # Show in GUI with flashing effect
        self.flashing_alert = True
        self.flash_alert_window(message)
    
    def flash_alert_window(self, message):
        if not self.flashing_alert:
            return
            
        alert = tk.Toplevel(self.root)
        alert.title("Price Drop Alert!")
        alert.geometry("400x250")
        alert.resizable(False, False)
        
        # Center the alert window
        window_width = 400
        window_height = 250
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        
        alert.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Add content
        frame = ttk.Frame(alert, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        icon = ttk.Label(frame, text="⚠️", font=('Segoe UI', 24))
        icon.pack(pady=(0, 10))
        
        message_label = ttk.Label(frame, text=message, font=('Segoe UI', 10), 
                                justify=tk.CENTER, wraplength=350)
        message_label.pack(fill=tk.X, pady=5)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=(15, 0))
        
        ok_button = ttk.Button(button_frame, text="OK", command=lambda: self.close_alert(alert), 
                              style='Primary.TButton')
        ok_button.pack(pady=5, ipadx=20)
        
        # Flash the window
        self.flash_window(alert)
    
    def flash_window(self, window):
        if not self.flashing_alert:
            return
            
        colors = ['#FF9900', '#FFD700', '#FF6347', '#FFA500']
        for color in colors:
            window.configure(background=color)
            window.update()
            time.sleep(0.1)
        
        window.configure(background='SystemButtonFace')
    
    def close_alert(self, window):
        self.flashing_alert = False
        window.destroy()
    
    def monitor_prices(self):
        while self.monitoring_active:
            for product in self.tracked_products:
                self.check_price(product)
            
            # Update GUI
            self.root.after(0, self.update_products_tree)
            
            # Update status with current time
            self.root.after(0, lambda: self.status_var.set(
                "Monitoring prices... | " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # Wait before next check (e.g., every 30 minutes)
            time.sleep(1800)
    
    def update_products_tree(self):
        self.products_tree.delete(*self.products_tree.get_children())
        
        for product in self.tracked_products:
            # Format prices with commas for thousands
            current_price = f"${product.get('current_price', 0):,.2f}"
            lowest_price = f"${product.get('lowest_price', 0):,.2f}"
            target_price = f"${product.get('target_price', 0):,.2f}"
            
            values = (
                product.get('name', 'Unknown'),
                current_price,
                lowest_price,
                target_price,
                product.get('last_drop_date', 'N/A'),
                product.get('status', 'Pending'),
                product.get('url', '')
            )
            
            item = self.products_tree.insert("", tk.END, values=values)
            
            # Highlight rows where target price is reached
            if product.get('status') == "Target Reached!":
                self.products_tree.tag_configure('target_reached', background='#d4edda')
                self.products_tree.item(item, tags=('target_reached',))
            
            # Highlight rows with recent price drops
            if product.get('last_drop_date') == datetime.now().strftime("%Y-%m-%d"):
                self.products_tree.tag_configure('price_drop', background='#fff3cd')
                self.products_tree.item(item, tags=('price_drop',))
    
    def load_data(self):
        if os.path.exists('tracked_products.json'):
            try:
                with open('tracked_products.json', 'r') as f:
                    self.tracked_products = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Could not load data: {str(e)}", parent=self.root)
                self.tracked_products = []
    
    def save_data(self):
        try:
            with open('tracked_products.json', 'w') as f:
                json.dump(self.tracked_products, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save data: {str(e)}", parent=self.root)
    
    def on_close(self):
        self.monitoring_active = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set window icon (replace with actual icon file if available)
    try:
        root.iconbitmap('amazon_icon.ico')
    except:
        pass
    
    # Set window position to center
    window_width = 1100
    window_height = 750
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    app = AmazonPriceTracker(root)
    root.mainloop()