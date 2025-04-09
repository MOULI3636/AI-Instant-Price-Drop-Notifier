import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import threading
import json
import os
from datetime import datetime, timedelta
import random
import webbrowser
from collections import deque

class AmazonPriceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("🛒 Amazon Price Tracker Pro")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f5f5")
        
        # Set colors first
        self.primary_color = "#FF9900"
        self.secondary_color = "#232F3E"
        self.success_color = "#2E8B57"
        self.danger_color = "#DC3545"
        self.info_color = "#17A2B8"
        
        # Initialize style
        self.set_style()
        
        # Product tracking list with price history
        self.tracked_products = []
        self.user_info = {'email': '', 'phone': ''}
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
        self.success_popup = None
    
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
        
        self.style.configure('Info.TButton', foreground='white', background=self.info_color)
        self.style.map('Info.TButton',
                      background=[('active', '#138496')])
    
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
        
        # User info button
        user_button = ttk.Button(header_frame, text="✉️ Set Notifications", 
                               command=self.set_user_info, style='Info.TButton')
        user_button.pack(side=tk.RIGHT, padx=10)
        
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
        
        history_button = ttk.Button(buttons_frame, text="📜 View Price History", command=self.show_price_history,
                                  style='Info.TButton')
        history_button.pack(side=tk.LEFT, padx=5)
        
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
    
    def set_user_info(self):
        # Create a popup window
        popup = tk.Toplevel(self.root)
        popup.title("Notification Settings")
        popup.geometry("400x250")
        popup.resizable(False, False)
        
        # Center the popup window
        window_width = 400
        window_height = 250
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        
        popup.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Add content
        frame = ttk.Frame(popup, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Notification Settings", font=('Segoe UI', 12, 'bold')).pack(pady=(0, 15))
        
        # Email field
        email_frame = ttk.Frame(frame)
        email_frame.pack(fill=tk.X, pady=5)
        ttk.Label(email_frame, text="Email:").pack(side=tk.LEFT, padx=5)
        self.email_entry = ttk.Entry(email_frame)
        self.email_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.email_entry.insert(0, self.user_info.get('email', ''))
        
        # Phone field
        phone_frame = ttk.Frame(frame)
        phone_frame.pack(fill=tk.X, pady=5)
        ttk.Label(phone_frame, text="Phone:").pack(side=tk.LEFT, padx=5)
        self.phone_entry = ttk.Entry(phone_frame)
        self.phone_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.phone_entry.insert(0, self.user_info.get('phone', ''))
        
        # Save button
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=(15, 0))
        
        save_button = ttk.Button(button_frame, text="Save", command=lambda: self.save_user_info(popup), 
                               style='Primary.TButton')
        save_button.pack(pady=5, ipadx=20)
    
    def save_user_info(self, popup):
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if not email and not phone:
            messagebox.showerror("Error", "Please provide at least one contact method", parent=popup)
            return
        
        self.user_info = {
            'email': email,
            'phone': phone
        }
        
        # Save to file
        try:
            with open('user_info.json', 'w') as f:
                json.dump(self.user_info, f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save user info: {str(e)}", parent=popup)
            return
        
        popup.destroy()
        self.show_success_message("Notification settings saved successfully!")
    
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
        
        # Create price history with 3-5 entries
        price_history = deque(maxlen=5)
        for i in range(random.randint(3, 5)):
            days_back = random.randint(1, 365)
            hist_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            hist_price = current_price * random.uniform(0.7, 1.3)  # Random historical price
            price_history.append({
                'date': hist_date,
                'price': hist_price,
                'was_drop': random.random() > 0.7  # 30% chance it was a drop
            })
        
        product = {
            'name': name,
            'url': url,
            'current_price': current_price,
            'lowest_price': current_price * random.uniform(0.7, 0.95),  # Random lower price
            'target_price': target_price,
            'last_drop_date': last_drop_date,
            'status': "Tracking" if current_price > target_price else "Target Reached!",
            'last_checked': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'price_history': list(price_history)
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
        
        # Show success message
        self.show_success_message(f"Product '{name}' added successfully!")
        
        # Show alert if target reached
        if product['status'] == "Target Reached!":
            self.show_alert(product)
    
    def show_success_message(self, message):
        # Close any existing success popup
        if self.success_popup and self.success_popup.winfo_exists():
            self.success_popup.destroy()
        
        # Create a semi-transparent overlay
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-alpha', 0.7)
        overlay.attributes('-fullscreen', True)
        overlay.configure(background='black')
        overlay.attributes('-topmost', True)
        
        # Create the success popup
        self.success_popup = tk.Toplevel(self.root)
        self.success_popup.title("Success")
        self.success_popup.attributes('-topmost', True)
        
        # Center the popup
        window_width = 400
        window_height = 200
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        
        self.success_popup.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.success_popup.resizable(False, False)
        
        # Add content
        frame = ttk.Frame(self.success_popup, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Success icon
        icon = ttk.Label(frame, text="✓", font=('Segoe UI', 36, 'bold'), foreground=self.success_color)
        icon.pack(pady=(0, 15))
        
        # Message
        msg = ttk.Label(frame, text=message, font=('Segoe UI', 12), justify=tk.CENTER)
        msg.pack(fill=tk.X)
        
        # Close button
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=(20, 0))
        
        close_button = ttk.Button(button_frame, text="OK", command=lambda: self.close_success(overlay), 
                                style='Success.TButton')
        close_button.pack(ipadx=20)
        
        # Auto-close after 3 seconds
        self.root.after(3000, lambda: self.close_success(overlay))
    
    def close_success(self, overlay):
        if self.success_popup and self.success_popup.winfo_exists():
            self.success_popup.destroy()
        if overlay and overlay.winfo_exists():
            overlay.destroy()
    
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
    
    def show_price_history(self):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a product to view history", parent=self.root)
            return
        
        item = self.products_tree.item(selected[0])
        product_name = item['values'][0]
        
        # Find the product in our list
        product = next((p for p in self.tracked_products if p['name'] == product_name), None)
        if not product or 'price_history' not in product:
            messagebox.showinfo("Info", "No price history available for this product", parent=self.root)
            return
        
        # Create history window
        history_window = tk.Toplevel(self.root)
        history_window.title(f"Price History: {product_name}")
        history_window.geometry("600x400")
        
        # Create treeview
        tree_frame = ttk.Frame(history_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("date", "price", "change")
        history_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Configure columns
        history_tree.heading("date", text="Date")
        history_tree.heading("price", text="Price ($)")
        history_tree.heading("change", text="Change")
        
        history_tree.column("date", width=150, anchor=tk.CENTER)
        history_tree.column("price", width=150, anchor=tk.CENTER)
        history_tree.column("change", width=150, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=history_tree.yview)
        history_tree.configure(yscroll=scrollbar.set)
        
        history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Sort history by date (newest first)
        sorted_history = sorted(product['price_history'], 
                              key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"), 
                              reverse=True)
        
        # Add data to treeview
        for i, record in enumerate(sorted_history):
            price = f"${record['price']:,.2f}"
            
            # Calculate change if there's a previous record
            if i < len(sorted_history) - 1:
                prev_price = sorted_history[i+1]['price']
                change = record['price'] - prev_price
                change_percent = (change / prev_price) * 100
                change_text = f"{change:+.2f} ({change_percent:+.2f}%)"
                
                if change < 0:
                    change_text = f"↓ {change_text}"
                    tag = 'drop'
                else:
                    change_text = f"↑ {change_text}"
                    tag = 'rise'
            else:
                change_text = "N/A"
                tag = ''
            
            # Insert with appropriate tags
            item = history_tree.insert("", tk.END, values=(record['date'], price, change_text))
            
            # Color rows based on price changes
            if tag == 'drop':
                history_tree.tag_configure('drop', foreground='green')
                history_tree.item(item, tags=('drop',))
            elif tag == 'rise':
                history_tree.tag_configure('rise', foreground='red')
                history_tree.item(item, tags=('rise',))
    
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
                
                # Record this drop in price history
                product['price_history'].append({
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'price': new_price,
                    'was_drop': True
                })
            
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
        
        # Send notifications if user info is set
        if self.user_info.get('email'):
            self.send_email_alert(product)
        
        if self.user_info.get('phone'):
            self.send_sms_alert(product)
    
    def send_email_alert(self, product):
        # In a real app, this would send an actual email
        print(f"Email sent to {self.user_info['email']} about price drop for {product['name']}")
    
    def send_sms_alert(self, product):
        # In a real app, this would send an actual SMS
        print(f"SMS sent to {self.user_info['phone']} about price drop for {product['name']}")
    
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
        # Load tracked products
        if os.path.exists('tracked_products.json'):
            try:
                with open('tracked_products.json', 'r') as f:
                    data = json.load(f)
                    # Convert price_history lists to deques
                    for product in data:
                        if 'price_history' in product:
                            product['price_history'] = deque(product['price_history'], maxlen=5)
                    self.tracked_products = data
            except Exception as e:
                messagebox.showerror("Error", f"Could not load product data: {str(e)}", parent=self.root)
                self.tracked_products = []
        
        # Load user info
        if os.path.exists('user_info.json'):
            try:
                with open('user_info.json', 'r') as f:
                    self.user_info = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Could not load user info: {str(e)}", parent=self.root)
                self.user_info = {'email': '', 'phone': ''}
    
    def save_data(self):
        try:
            with open('tracked_products.json', 'w') as f:
                # Convert deques to lists for JSON serialization
                data_to_save = []
                for product in self.tracked_products:
                    product_copy = product.copy()
                    if 'price_history' in product_copy:
                        product_copy['price_history'] = list(product_copy['price_history'])
                    data_to_save.append(product_copy)
                json.dump(data_to_save, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save product data: {str(e)}", parent=self.root)
    
    def on_close(self):
        self.monitoring_active = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        self.save_data()  # Ensure data is saved before closing
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set window icon (replace with actual icon file if available)
    try:
        root.iconbitmap('amazon_icon.ico')
    except:
        pass
    
    # Set window position to center
    window_width = 1200
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    app = AmazonPriceTracker(root)
    root.mainloop()
