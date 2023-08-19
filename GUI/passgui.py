import pykeepass
import getpass
import hashlib
import requests
from cryptography.fernet import Fernet
import base64
import os
import pyperclip
from tabulate import tabulate
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from PIL import Image, ImageTk


DB_FILE = ""
MASTER_PASSWORD = ""

def encrypt_password(password):
    key = hashlib.sha256(MASTER_PASSWORD.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key)
    fernet = Fernet(fernet_key)
    encrypted_password = fernet.encrypt(password.encode())
    return encrypted_password

def decrypt_password(encrypted_password):
    key = hashlib.sha256(MASTER_PASSWORD.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key)
    fernet = Fernet(fernet_key)
    decrypted_password = fernet.decrypt(encrypted_password).decode()
    return decrypted_password

def create_database():
    def create_db():
        global DB_FILE
        global MASTER_PASSWORD

        database_name = db_name_entry.get()
        master_password = master_pass_entry.get()
        confirm_password = confirm_pass_entry.get()

        if master_password == confirm_password:
            try:
                # Create an empty KeePass database file
                DB_FILE = f"{database_name}.kdbx"
                kp = pykeepass.create_database(DB_FILE, master_password)
                kp.save()
                MASTER_PASSWORD = master_password
                messagebox.showinfo("Success", f"Database '{database_name}.kdbx' created successfully!")
                create_db_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error creating database: {str(e)}")
        else:
            messagebox.showerror("Error", "Passwords do not match. Database creation aborted.")

    create_db_window = tk.Toplevel()
    create_db_window.title("Create KeePass Database")

    db_name_label = tk.Label(create_db_window, text="Database Name:")
    db_name_label.grid(row=0, column=0, padx=10, pady=5)
    db_name_entry = tk.Entry(create_db_window)
    db_name_entry.grid(row=0, column=1, padx=10, pady=5)

    master_pass_label = tk.Label(create_db_window, text="Master Password:")
    master_pass_label.grid(row=1, column=0, padx=10, pady=5)
    master_pass_entry = tk.Entry(create_db_window, show="*")
    master_pass_entry.grid(row=1, column=1, padx=10, pady=5)

    confirm_pass_label = tk.Label(create_db_window, text="Confirm Password:")
    confirm_pass_label.grid(row=2, column=0, padx=10, pady=5)
    confirm_pass_entry = tk.Entry(create_db_window, show="*")
    confirm_pass_entry.grid(row=2, column=1, padx=10, pady=5)

    create_button = tk.Button(create_db_window, text="Create", command=create_db)
    create_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)


def use_existing_db():
    global DB_FILE
    global MASTER_PASSWORD

    db_path = filedialog.askopenfilename(title="Select KeePass Database File")
    master_password = simpledialog.askstring("Existing Database", "Enter the master password for the existing database:", show='*')

    if not os.path.exists(db_path):
        messagebox.showerror("Error", "Database file does not exist.")
        return

    try:
        with pykeepass.PyKeePass(db_path, password=master_password):
            DB_FILE = db_path
            MASTER_PASSWORD = master_password

        messagebox.showinfo("Success", "Using existing database.")
        messagebox.showinfo("Database Details", f"Database Path: {DB_FILE}\nMaster Password: {'*' * len(MASTER_PASSWORD)}")
    except Exception as e:
        messagebox.showerror("Error", f"Error opening existing database: {str(e)}")


def store_password():
    global DB_FILE
    global MASTER_PASSWORD


    if DB_FILE == "" or MASTER_PASSWORD == "":
        messagebox.showerror("Error", "Please create a new database or use an existing database first.")
        return

    def store():

        entry_name = entry_name_entry.get()
        website_url = website_url_entry.get()
        username = username_entry.get()
        password = password_entry.get()

        try:
            with pykeepass.PyKeePass(DB_FILE, password=MASTER_PASSWORD) as kp:
                entry_group = kp.find_groups(name='Root', first=True)
                entry = kp.add_entry(entry_group, title=entry_name, username=username, password=password)
                entry.url = website_url  # Set the URL field
                kp.save()
            messagebox.showinfo("Success", "Password stored successfully!")
            store_password_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error storing password: {str(e)}")

    store_password_window = tk.Toplevel()
    store_password_window.title("Store Password")

    entry_name_label = tk.Label(store_password_window, text="Title/Entry Name:")
    entry_name_label.grid(row=0, column=0, padx=10, pady=5)
    entry_name_entry = tk.Entry(store_password_window)
    entry_name_entry.grid(row=0, column=1, padx=10, pady=5)

    website_url_label = tk.Label(store_password_window, text="Website URL:")
    website_url_label.grid(row=1, column=0, padx=10, pady=5)
    website_url_entry = tk.Entry(store_password_window)
    website_url_entry.grid(row=1, column=1, padx=10, pady=5)

    username_label = tk.Label(store_password_window, text="Username:")
    username_label.grid(row=2, column=0, padx=10, pady=5)
    username_entry = tk.Entry(store_password_window)
    username_entry.grid(row=2, column=1, padx=10, pady=5)

    password_label = tk.Label(store_password_window, text="Password:")
    password_label.grid(row=3, column=0, padx=10, pady=5)
    password_entry = tk.Entry(store_password_window, show="*")
    password_entry.grid(row=3, column=1, padx=10, pady=5)

    store_button = tk.Button(store_password_window, text="Store", command=store)
    store_button.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

def retrieve_password():
    global DB_FILE
    global MASTER_PASSWORD

    if DB_FILE == "" or MASTER_PASSWORD == "":
        messagebox.showerror("Error", "Please create a new database or use an existing database first.")
        return

    def retrieve():
        entry_name = entry_name_entry.get()
        username = username_entry.get()

        try:
            with pykeepass.PyKeePass(DB_FILE, password=MASTER_PASSWORD) as kp:
                entries = kp.find_entries(title=entry_name, username=username)
                if entries:
                    entry = entries[0]
                    decrypted_password = entry.password  # Password is already stored in encrypted form
                    messagebox.showinfo("Password Retrieved", f"Retrieved password: {decrypted_password}\nPassword copied to clipboard.")
                    pyperclip.copy(decrypted_password)
                    retrieve_password_window.destroy()
                else:
                    messagebox.showinfo("No Entry Found", "No matching entry found.")
        except Exception as e:
            messagebox.showerror("Error", f"Error retrieving password: {str(e)}")

    retrieve_password_window = tk.Toplevel()
    retrieve_password_window.title("Retrieve Password")

    entry_name_label = tk.Label(retrieve_password_window, text="Title/Entry Name:")
    entry_name_label.grid(row=0, column=0, padx=10, pady=5)
    entry_name_entry = tk.Entry(retrieve_password_window)
    entry_name_entry.grid(row=0, column=1, padx=10, pady=5)

    username_label = tk.Label(retrieve_password_window, text="Username:")
    username_label.grid(row=1, column=0, padx=10, pady=5)
    username_entry = tk.Entry(retrieve_password_window)
    username_entry.grid(row=1, column=1, padx=10, pady=5)

    retrieve_button = tk.Button(retrieve_password_window, text="Retrieve", command=retrieve)
    retrieve_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5)


def analyze_password():
    password = simpledialog.askstring("Analyze Password", "Enter password to analyze:", show='*')

    # Generate SHA-1 hash of the password
    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    sha1_prefix = sha1_password[:5]
    sha1_suffix = sha1_password[5:]

    try:
        response = requests.get(f"https://api.pwnedpasswords.com/range/{sha1_prefix}")
        if response.status_code == 200:
            password_hashes = response.text.splitlines()
            found = False

            # Check if the password hash suffix exists in the response
            for password_hash in password_hashes:
                if sha1_suffix in password_hash:
                    count = int(password_hash.split(':')[1])
                    messagebox.showwarning("Password Breached", f"The password '{password}' has been found in {count} data breaches.")
                    found = True
                    break

            if not found:
                messagebox.showinfo("Password Not Breached", f"The password '{password}' has not been found in any data breaches.")
        else:
            messagebox.showerror("Error", "Failed to check password breach status.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to check password breach status: {str(e)}")

def show_entries():
    global DB_FILE
    global MASTER_PASSWORD

    if DB_FILE == "" or MASTER_PASSWORD == "":
        messagebox.showerror("Error", "Please create a new database or use an existing database first.")
        return

    try:
        with pykeepass.PyKeePass(DB_FILE, password=MASTER_PASSWORD) as kp:
            entries = kp.entries
            entry_data = []
            for entry in entries:
                # Add the entry data to the list without including the password
                entry_data.append([entry.title, entry.username, entry.url])

            # Create a new window to display the entries table
            entries_window = tk.Toplevel()
            entries_window.title("Entries")

            # Create a table widget to display the entries
            table = tk.Text(entries_window, height=len(entry_data)+1, width=80)
            table.pack()

            # Insert the table headers
            headers = ["Title/Entry", "Username", "URL"]
            table.insert(tk.END, tabulate([headers] + entry_data, tablefmt="plain"))

            # Disable editing of the table
            table.configure(state="disabled")

    except Exception as e:
        messagebox.showerror("Error", f"Error retrieving entries: {str(e)}")



def main():
    root = tk.Tk()
    root.title("Password Manager Security Analyzer")

    # Load the image
    image = Image.open("banner.png")  # Replace "banner.png" with your image file

    # Resize the image if needed
    image = image.resize((300, 100))  # Adjust the size as needed

    # Create a PhotoImage object from the image
    photo = ImageTk.PhotoImage(image)

    # Create a label with the image
    banner_label = tk.Label(root, image=photo)
    banner_label.image = photo  # Store a reference to the image to prevent garbage collection
    banner_label.pack(pady=10)  # Add padding at the top

    # Create a frame to hold the menu buttons
    menu_frame = tk.Frame(root)
    menu_frame.pack(pady=10)  # Add padding below the image

    # Create the first grid of buttons (3 buttons)
    create_db_button = tk.Button(menu_frame, text="Create New Database", command=create_database)
    create_db_button.grid(row=0, column=0, padx=10, pady=5)

    use_db_button = tk.Button(menu_frame, text="Use Existing Database", command=use_existing_db)
    use_db_button.grid(row=0, column=1, padx=10, pady=5)

    store_password_button = tk.Button(menu_frame, text="Store Password", command=store_password)
    store_password_button.grid(row=0, column=2, padx=10, pady=5)

    # Create the second grid of buttons (3 buttons)
    retrieve_password_button = tk.Button(menu_frame, text="Retrieve Password", command=retrieve_password)
    retrieve_password_button.grid(row=1, column=0, padx=10, pady=5)

    analyze_password_button = tk.Button(menu_frame, text="Analyze Password", command=analyze_password)
    analyze_password_button.grid(row=1, column=1, padx=10, pady=5)

    show_entries_button = tk.Button(menu_frame, text="Show Entries", command=show_entries)
    show_entries_button.grid(row=1, column=2, padx=10, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
