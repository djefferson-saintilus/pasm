# coding:utf-8
# author: djefferson saintilus


import pykeepass, getpass, hashlib, requests, base64, os, pyperclip, string, random, platform, validators
from cryptography.fernet import Fernet
from tabulate import tabulate
import os, sys, time


DB_FILE = ""
MASTER_PASSWORD = ""

# Create the database directory if not exist
db_dir = r"./db/"
if not os.path.exists(db_dir):
    os.mkdir(r"./db/")
    
def clear_screen():
    """Clears the console screen based on the current platform."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


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


def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(random.choice(characters) for _ in range(length))
    return password


def create_database():
    global DB_FILE
    global MASTER_PASSWORD

    database_name = input(
        "\033[1;36mEnter the name for the database (without extension):\033[0m "
    )
    current_directory = os.getcwd()  # Get current directory

    DB_FILE = os.path.join(current_directory, f"db/{database_name}.kdbx")

    if os.path.exists(DB_FILE):
        print(
            f"\033[1;31mA database with the name 'db/{database_name}.kdbx' already exists in {os.path.basename(current_directory)}.\033[0m"
        )
        input("\nPress ENTER to continue")
        return
    
    master_password = getpass.getpass(
        "\033[1;36mEnter the master password (minimum 8 characters):\033[0m "
    )
    confirm_password = getpass.getpass("\033[1;36mConfirm the master password:\033[0m ")

    if master_password != confirm_password:
        print("\033[1;31mPasswords do not match. Database creation aborted.\033[0m")
        input("\nPress ENTER to continue")
        return

    if len(master_password) < 8:
        print(
            "\033[1;31mMaster password should be a minimum of 8 characters long. Database creation aborted.\033[0m"
        )
        input("\nPress ENTER to continue")
        return

    try:
        # Create an empty KeePass database file
        kp = pykeepass.create_database(DB_FILE, master_password)
        kp.save()
        print(
            f"\033[1;32mDatabase 'db/{database_name}.kdbx' created successfully in {os.path.basename(current_directory)}!\033[0m"
        )
        # Save DB_FILE and MASTER_PASSWORD
        with open(".keepass_settings", "w") as settings_file:
            settings_file.write(f"{DB_FILE}\n{master_password}")

        MASTER_PASSWORD = master_password
        input("\nPress ENTER to continue")
    except Exception as e:
        print("\033[1;31mError creating database:", str(e), "\033[0m")
        input("\nPress ENTER to continue")
        

def use_existing_db():
    global DB_FILE
    global MASTER_PASSWORD

    db_name = input(
        "\033[1;36mEnter the name of the existing KeePass database (without extension):\033[0m "
    )
    db_path = os.path.join("db", f"{db_name}.kdbx")
    master_password = getpass.getpass(
        "\033[1;36mEnter the master password for the existing database:\033[0m "
    )

    if not os.path.exists(db_path):
        print("\033[1;31mDatabase file does not exist.\033[0m")
        input("\nPress ENTER to continue")
        return

    try:
        with pykeepass.PyKeePass(db_path, password=master_password):
            DB_FILE = db_path
            MASTER_PASSWORD = master_password

        print("\033[1;32mUsing existing database:\033[0m")
        print("\033[1;32mDatabase Path:\033[0m", DB_FILE)
        print("\033[1;32mMaster Password:\033[0m", "*" * len(MASTER_PASSWORD))
        input("\nPress ENTER to continue")
    except Exception as e:
        print("\033[1;31mError opening existing database:", str(e), "\033[0m")
        input("\nPress ENTER to continue")


def store_password():
    global DB_FILE
    global MASTER_PASSWORD

    if DB_FILE == "" or MASTER_PASSWORD == "":
        print(
            "\033[1;31mPlease create a new database or use an existing database first.\033[0m"
        )
        input("\nPress ENTER to continue")
        return

    while True:
        generate_option = input(
            "\033[1;36mDo you want to generate a password? (y/n):\033[0m "
        )
        
        if generate_option.lower() == "y":
            while True:
                password_length = int(
                    input(
                        "\033[1;36mEnter the desired password length (minimum 8 characters):\033[0m "
                    )
                )
                if password_length >= 8:
                    break
                print(
                    "\033[1;31mPassword length should be a minimum of 8 characters.\033[0m"
                )
                input("\nPress ENTER to continue")
            password = generate_password(password_length)
            break

        elif generate_option.lower() == "n":
            password = getpass.getpass(
                "\033[1;36mEnter the password (minimum 8 characters):\033[0m "
            )

            if len(password) < 8:
                print(
                    "\033[1;31mPassword should be a minimum of 8 characters long.\033[0m"
                )
                input("\nPress ENTER to continue")
            else:
                break

        else:
            print("\033[1;31mInvalid option. Please enter 'y' or 'n'.\033[0m")
            input("\nPress ENTER to continue")

    while True:
        entry_name = input("\033[1;36mEnter the entry name (Title):\033[0m ")
        website_url = input("\033[1;36mEnter the website URL:\033[0m ")

        if not validators.url(website_url):
            print("\033[1;31mInvalid website URL.\033[0m")
            input("\nPress ENTER to continue")
        else:
            break

    while True:
        username = input("\033[1;36mEnter the username (minimum 4 characters):\033[0m ")

        if len(username) < 4:
            print("\033[1;31mUsername should be a minimum of 4 characters long.\033[0m")
            input("\nPress ENTER to continue")
        else:
            break

    try:
        with pykeepass.PyKeePass(DB_FILE, password=MASTER_PASSWORD) as kp:
            entry_group = kp.find_groups(name="Root", first=True)

            # Check if entry name already exists
            if kp.find_entries(title=entry_name, group=entry_group):
                print(
                    "\033[1;31mAn entry with the same name already exists. Password not stored.\033[0m"
                )
                input("\nPress ENTER to continue")
                return

            entry = kp.add_entry(
                entry_group, title=entry_name, username=username, password=password
            )
            entry.url = website_url  # Set the URL field
            kp.save()
        print("\033[1;32mPassword stored successfully!\033[0m")
        input("\nPress ENTER to continue")
    except Exception as e:
        print("\033[1;31mError storing password:", str(e), "\033[0m")
        input("\nPress ENTER to continue")


def retrieve_password():
    global DB_FILE
    global MASTER_PASSWORD

    if DB_FILE == "" or MASTER_PASSWORD == "":
        print(
            "\033[1;31mPlease create a new database or use an existing database first.\033[0m"
        )
        input("\nPress ENTER to continue")
        return

    entry_name = input("\033[1;36mEnter the entry name:\033[0m ")
    username = input("\033[1;36mEnter username:\033[0m ")

    try:
        with pykeepass.PyKeePass(DB_FILE, password=MASTER_PASSWORD) as kp:
            entries = kp.find_entries(title=entry_name, username=username)
            if entries:
                entry = entries[0]
                decrypted_password = (
                    entry.password
                )  # Password is already stored in encrypted form
                print("\033[1;32mRetrieved password:", decrypted_password, "\033[0m")
                pyperclip.copy(decrypted_password)
                print("\033[1;32mPassword copied to clipboard.\033[0m")
                input("\nPress ENTER to continue")
            else:
                print("\033[1;31mNo matching entry found.\033[0m")
                input("\nPress ENTER to continue")
    except Exception as e:
        print("\033[1;31mError retrieving password:", str(e), "\033[0m")
        input("\nPress ENTER to continue")

# Delete entry based on the entry name
def delete_entry_by_title():
    global DB_FILE
    global MASTER_PASSWORD
    while True:
        entry_title = input("\033[1;36mEnter the entry name to delete: \033[0m")
        try:
            kp = pykeepass.PyKeePass(DB_FILE, password=MASTER_PASSWORD)
            # # Find entries maching the title 
            entry = kp.find_entries(title=entry_title, first=True)

            if entry:
                user_confirmation = input("\033[1;31mDo you want to delete the entry ? (y/n):\033[0m ")
                if user_confirmation == "y":
                    kp.delete_entry(entry)
                    kp.save()
                    print("\033[1;32mEntry Deleted successfully!\033[0m")
                elif user_confirmation == "n":
                    print("\033[1;31mNo entry delete in the database\033[0m")
                    input("\nPress ENTER to continue")
                    break
                else:
                    print("\033[1;31mBad answer character. Type (y or n)\033[0m")
                    continue
                input("\nPress ENTER to continue")
                return
            else:
                print("\033[1;31mNo matching entry found.\033[0m")
                input("\nPress ENTER to continue")
                return  
        except Exception as e:
            print(str(e))

def analyze_password():
    while True:
        password = getpass.getpass("\033[1;36mEnter password to analyze:\033[0m ")

        if password.strip() == "":
            print("\033[1;31mPassword cannot be empty. Please try again.\033[0m")
            input("\nPress ENTER to continue")
        else:
            break

    # Generate SHA-1 hash of the password
    sha1_password = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
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
                    count = int(password_hash.split(":")[1])
                    print(
                        f"The password '\033[1;33m{password}\033[0m' has been found in \033[1;31m{count}\033[0m data breaches."
                    )
                    input("\nPress ENTER to continue")
                    found = True
                    break

            if not found:
                print(
                    f"The password '\033[1;33m{password}\033[0m' has not been found in any data breaches."
                )
                print("\033[1;32mTip: This password has not been compromised.")
                print(
                    "However, it is important to use strong and unique passwords for better security.\033[0m"
                )
                input("\nPress ENTER to continue")
            else:
                print(
                    "\033[1;31mTip: This password has been compromised in a data breach."
                )
                print(
                    "It is strongly recommended to choose a different and more secure password.\033[0m"
                )
                input("\nPress ENTER to continue")
        elif response.status_code == 404:
            print(
                f"The password '\033[1;33m{password}\033[0m' has not been found in any data breaches."
            )
            print("\033[1;32mTip: This password has not been compromised.")
            print(
                "However, it is important to use strong and unique passwords for better security.\033[0m"
            )
            input("\nPress ENTER to continue")
        else:
            print("An error occurred while analyzing the password.")
            time.sleep(5)
    except Exception as e:
        print("Error analyzing password:", str(e))
        input("\nPress ENTER to continue")


def show_entries():
    global DB_FILE
    global MASTER_PASSWORD

    if DB_FILE == "" or MASTER_PASSWORD == "":
        print("\033[1;33mPlease create a new database or use an existing database first.\033[0m")
        input("\nPress ENTER to continue")
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
            input("\nPress ENTER to continue")
    except Exception as e:
        print("Error retrieving entries:", str(e))
        input("\nPress ENTER to continue")

# this is an update to delete Menu
# Update made by kerdes
# ===========Update start================ 

# Store menu option as a list for futher use to display current option
menu = [
    "    1. Create KeePass database",
    "    2. Use existing KeePass database",
    "    3. Store password",
    "    4. Retrieve password",
    "    5. Delete database entry",
    "    6. Analyze password",
    "    7. Show database entries",
    "    0. Exit"
]

# Display the menu
def print_menu():
    print("Menu:")
    print(menu[0])
    print(menu[1])
    print(menu[2])
    print(menu[3])
    print(menu[4])
    print(menu[5])
    print(menu[6])
    print(menu[7])
    print()
        
# Top level function to get user choice when program start
def get_user_choice():
    while True:
        choice = input("\nEnter your choice: ")
        if choice == "*":
            clear_screen()
            logo()
            print_menu()
            menu_actions()
        elif choice == "q":
            print("*** Thank you for using \033[1;36mPASM\033[0m as your Password Manager ***")
            print("Bye")
            sys.exit()
        else:
            print("\033[1;31mInvalid choice. Please try again.\033[0m")
            # continue
    return choice

# Logo to display at the top of the terminal
def logo():
    print(
        r"""
   ▄███████▄    ▄████████    ▄████████   ▄▄▄▄███▄▄▄▄   
  ███    ███   ███    ███   ███    ███ ▄██▀▀▀███▀▀▀██▄ 
  ███    ███   ███    ███   ███    █▀  ███   ███   ███ 
  ███    ███   ███    ███   ███        ███   ███   ███ 
▀█████████▀  ▀███████████ ▀███████████ ███   ███   ███ 
  ███          ███    ███          ███ ███   ███   ███ 
  ███          ███    ███    ▄█    ███ ███   ███   ███ 
 ▄████▀        ███    █▀    ▄████████▀  ▀█   ███   █▀                                                             
"""
)

# First banner to display after the logo
def banner2():
    print("--------------------------------")
    print("Author	: Djefferson Saintilus")
    print("Version	: v1.1")
    print("Collaborators : kerdes, xdevcod3")
    print("--------------------------------")

# Second banner to display after the first banner
def banner3():    
    print("\033[1;36mType (*) To display the menu\033[0m]")
    print("\033[1;31mType (q) to quit the program\033[0m]")

# This function help the user to interact with the program and use it's features
def menu_actions():
    # clear_screen()
    global MASTER_PASSWORD
    global menu
    while True:
        clear_screen()
        logo()
        print_menu()

        menu_option_selected = input("Type > ")
        
        if menu_option_selected == "1":
            clear_screen()
            logo()
            banner2()
            print(f"Current Option\n└─({menu[0]}\n")
            try:
                create_database()
            except Exception as e:
                print("\033[1;31mError creating database:", str(e), "\033[0m")
        elif menu_option_selected == "2":
            clear_screen()
            logo()
            banner2()
            print(f"Current Option\n└─({menu[1]}\n")
            try:
                use_existing_db()
            except Exception as e:
                print("\033[1;31mError using existing database:", str(e), "\033[0m")
        elif menu_option_selected == "3":
            clear_screen()
            logo()
            banner2()
            print(f"Current Option\n└─({menu[2]}\n")
            try:
                store_password()
            except Exception as e:
                print("\033[1;31mError storing password:", str(e), "\033[0m")
        elif menu_option_selected == "4":
            clear_screen()
            logo()
            banner2()
            print(f"Current Option\n└─({menu[3]}\n")
            try:
                retrieve_password()
            except Exception as e:
                print("\033[1;31mError retrieving password:", str(e), "\033[0m")
        elif menu_option_selected == "5":
            clear_screen()
            logo()
            banner2()
            print(f"Current Option\n└─({menu[4]}\n")
            try:
                delete_entry_by_title()
            except Exception as e:
                print("\033[1;31mError deleting entry:", str(e), "\033[0m")
        elif menu_option_selected == "6":
            clear_screen()
            logo()
            banner2()
            print(f"Current Option\n└─({menu[5]}\n")
            try:
                analyze_password()
            except Exception as e:
                print(
                    "\033[1;31mAn error occurred while analyzing the password:",
                    str(e),
                    "\033[0m",
                )
        elif menu_option_selected == "7":
            clear_screen()
            logo()
            banner2()
            print(f"Current Option\n└─({menu[6]}\n")
            try:
                show_entries()
            except Exception as e:
                print("\033[1;31mError retrieving entries:", str(e), "\033[0m")
        elif menu_option_selected == "0":
            print("\033[1;32mGoing back to the Top\033[0m")
            time.sleep(1.5)
            clear_screen()
            main()
        else:
            print("\033[1;31mInvalid choice. Please try again.\033[0m")

# This is the main function that launch the program
def main():
    logo()
    banner2()
    banner3()
    get_user_choice()
    
# =============== END update ==============

if __name__ == "__main__":
    main()
