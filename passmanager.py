import pykeepass
import getpass
import hashlib
import requests
from cryptography.fernet import Fernet
import base64
import os
import pyperclip
from tabulate import tabulate

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
    global DB_FILE
    database_name = input("Enter the name for the database (without extension): ")
    current_directory = os.getcwd()  # Get current directory

    DB_FILE = os.path.join(current_directory, f"{database_name}.kdbx")
    master_password = getpass.getpass("Enter the master password: ")
    confirm_password = getpass.getpass("Confirm the master password: ")

    if master_password == confirm_password:
        try:
            # Create an empty KeePass database file
            kp = pykeepass.create_database(DB_FILE, master_password)
            kp.save()
            print(f"Database '{database_name}.kdbx' created successfully in {current_directory}!")
        except Exception as e:
            print("Error creating database:", str(e))
            return
    else:
        print("Passwords do not match. Database creation aborted.")



def use_existing_db():
    global DB_FILE
    global MASTER_PASSWORD

    db_path = input("Enter the path to the existing KeePass database file (e.g., 'mydatabase.kdbx'): ")
    master_password = getpass.getpass("Enter the master password for the existing database: ")

    if not os.path.exists(db_path):
        print("Database file does not exist.")
        return

    try:
        with pykeepass.PyKeePass(db_path, password=master_password):
            DB_FILE = db_path
            MASTER_PASSWORD = master_password

        print("Using existing database:")
        print("Database Path:", DB_FILE)
        print("Master Password:", "*" * len(MASTER_PASSWORD))
    except Exception as e:
        print("Error opening existing database:", str(e))


def store_password():
    global DB_FILE
    global MASTER_PASSWORD

    if DB_FILE == "" or MASTER_PASSWORD == "":
        print("Please create a new database or use an existing database first.")
        return

    entry_name = input("Enter the entry name: ")
    website_url = input("Enter the website URL: ")
    username = input("Enter the username: ")
    password = getpass.getpass("Enter the password: ")

    try:
        with pykeepass.PyKeePass(DB_FILE, password=MASTER_PASSWORD) as kp:
            entry_group = kp.find_groups(name='Root', first=True)
            entry = kp.add_entry(entry_group, title=entry_name, username=username, password=password)
            entry.url = website_url  # Set the URL field
            kp.save()
        print("Password stored successfully!")
    except Exception as e:
        print("Error storing password:", str(e))

def retrieve_password():
    global DB_FILE
    global MASTER_PASSWORD

    if DB_FILE == "" or MASTER_PASSWORD == "":
        print("Please create a new database or use an existing database first.")
        return

    entry_name = input("Enter the entry name: ")
    username = input("Enter username: ")

    try:
        with pykeepass.PyKeePass(DB_FILE, password=MASTER_PASSWORD) as kp:
            entries = kp.find_entries(title=entry_name, username=username)
            if entries:
                entry = entries[0]
                decrypted_password = entry.password  # Password is already stored in encrypted form
                print("Retrieved password:", decrypted_password)
                pyperclip.copy(decrypted_password)
                print("Password copied to clipboard.")
            else:
                print("No matching entry found.")
    except Exception as e:
        print("Error retrieving password:", str(e))


def analyze_password():
    password = getpass.getpass("Enter password to analyze: ")

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
                    print(f"The password '{password}' has been found in {count} data breaches.")
                    found = True
                    break

            if not found:
                print(f"The password '{password}' has not been found in any data breaches.")
        elif response.status_code == 404:
            print(f"The password '{password}' has not been found in any data breaches.")
        else:
            print("An error occurred while analyzing the password.")
    except Exception as e:
        print("Error analyzing password:", str(e))

def show_entries():
    global DB_FILE
    global MASTER_PASSWORD

    if DB_FILE == "" or MASTER_PASSWORD == "":
        print("Please create a new database or use an existing database first.")
        return

    try:
        with pykeepass.PyKeePass(DB_FILE, password=MASTER_PASSWORD) as kp:
            entries = kp.entries
            print("Database Entries:")
            table_data = []
            for entry in entries:
                table_data.append([entry.title, entry.username, entry.url])

            headers = ["Title", "Username", "URL"]
            print(tabulate(table_data, headers, tablefmt="grid"))
    except Exception as e:
        print("Error retrieving entries:", str(e))


def main():
    global MASTER_PASSWORD

    print(r"""


   ▄███████▄    ▄████████    ▄████████   ▄▄▄▄███▄▄▄▄   
  ███    ███   ███    ███   ███    ███ ▄██▀▀▀███▀▀▀██▄ 
  ███    ███   ███    ███   ███    █▀  ███   ███   ███ 
  ███    ███   ███    ███   ███        ███   ███   ███ 
▀█████████▀  ▀███████████ ▀███████████ ███   ███   ███ 
  ███          ███    ███          ███ ███   ███   ███ 
  ███          ███    ███    ▄█    ███ ███   ███   ███ 
 ▄████▀        ███    █▀   ▄████████▀   ▀█   ███   █▀  
                                                                        
""")

    print("Author: Djefferson Saintilus")
    print("version: v1.0")
    print("--------------------------------")
    while True:
        print("\nMenu:")
        print("1. Create KeePass database")
        print("2. Use existing KeePass database")
        print("3. Store password")
        print("4. Retrieve password")
        print("5. Analyze password")
        print("6. Show database entries")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            try:
                create_database()
                MASTER_PASSWORD = getpass.getpass("Enter the master password: ")
            except Exception as e:
                print("Error creating database:", str(e))
        elif choice == '2':
            try:
                use_existing_db()
            except Exception as e:
                print("Error using existing database:", str(e))
        elif choice == '3':
            try:
                store_password()
            except Exception as e:
                print("Error storing password:", str(e))
        elif choice == '4':
            try:
                retrieve_password()
            except Exception as e:
                print("Error retrieving password:", str(e))
        elif choice == '5':
            try:
                analyze_password()
            except Exception as e:
                print("An error occurred while analyzing the password:", str(e))
        elif choice == '6':
            try:
                show_entries()
            except Exception as e:
                print("Error retrieving entries:", str(e))
        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
