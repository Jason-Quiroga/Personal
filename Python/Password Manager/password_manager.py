'''
Jason Quiroga | 23 October 2023 | OPSC-540 | Python Final Project
This program is a password manager that allows users to store their passwords in a database. The program uses a
master password to encrypt and decrypt the passwords in the database. The program uses the cryptography module to
encrypt and decrypt the passwords using Fernet. The program uses the sqlite3 module to create and interact with the
database. The program uses the tkinter module to create the GUI. The program uses the pyperclip module to copy the
passwords to the clipboard. The program uses the webbrowser module to open the URL in the browser. The user is first
asked to register a master user. The master user is stored in the database along with the encrypted master password. If
the user already exists, the user is asked to log in. The user is then presented with a menu that displays their
password entries. The user can add new entries, edit existing entries, delete entries, and copy the URL, username, or
password to the clipboard. The user can also open the URL in the browser, and SSH to the client if the
platform is an IP address.
'''

import base64
import hashlib
import os
import pyperclip
import sqlite3
import tkinter as tk
import webbrowser
import re
import subprocess
from tkinter import messagebox, ttk

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class PasswordManagerGUI:  # Class that handles the GUI for the password manager
    def __init__(self, root):
        # Create an instance of PasswordManager
        self.context_menu = None
        self.bg_color = None
        self.logout_button = None
        self.delete_entry_button = None
        self.add_entry_button = None
        self.tree = None
        self.password_manager = PasswordManager()
        self.decrypted_passwords = {}
        self.last_hovered_item = None

        # Initialize the root window that displays the GUI
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("400x400")

        # User authentication frame
        self.login_frame = tk.Frame(self.root)

        # Username entry to log in to the password manager
        self.login_title = tk.Label(self.login_frame, text="Password Manager Login", font=("Helvetica", 16, "bold"))
        self.login_title.grid(row=0, column=0, columnspan=2)
        self.username_label = tk.Label(self.login_frame, text="Username")
        self.username_label.grid(row=1, column=0)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=1, column=1)

        # Password entry to log in to the password manager
        self.password_label = tk.Label(self.login_frame, text="Password")
        self.password_label.grid(row=2, column=0)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=2, column=1)

        # Login button
        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=3, column=0, columnspan=2)

        # Platform entry frame
        self.entry_frame = tk.Frame(self.root)
        # Add Entry Label, make it bold
        self.title_label = tk.Label(self.entry_frame, text="Add an Entry", font=("Helvetica", 16, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2)
        # Platform entry label
        self.platform_label = tk.Label(self.entry_frame, text="Platform")
        self.platform_label.grid(row=1, column=0)
        self.platform_entry = tk.Entry(self.entry_frame)
        self.platform_entry.grid(row=1, column=1)

        # Username entry for the platform
        self.entry_username_label = tk.Label(self.entry_frame, text="Entry Username")
        self.entry_username_label.grid(row=2, column=0)
        self.entry_username_entry = tk.Entry(self.entry_frame)
        self.entry_username_entry.grid(row=2, column=1)

        # Password entry for the platform (hidden)
        self.entry_password_label = tk.Label(self.entry_frame, text="Entry Password")
        self.entry_password_label.grid(row=3, column=0)
        self.entry_password_entry = tk.Entry(self.entry_frame, show="*")
        self.entry_password_entry.grid(row=3, column=1)

        # Notes entry for the platform
        self.entry_notes_label = tk.Label(self.entry_frame, text="Notes")
        self.entry_notes_label.grid(row=4, column=0)
        self.entry_notes_entry = tk.Entry(self.entry_frame)
        self.entry_notes_entry.grid(row=4, column=1)

        # Add entry button to add the entry to the password manager
        self.add_button = tk.Button(self.entry_frame, text="Add Entry", command=self.submit_entry)
        self.add_button.grid(row=5, column=0, columnspan=2)

        # Add a button to go back to the menu frame without adding a new entry
        self.back_button = tk.Button(self.entry_frame, text="Back", command=self.menu)
        self.back_button.grid(row=6, column=0, columnspan=2)
        # Clear the fields when the back button is clicked
        self.back_button.bind("<Button-1>", lambda event: self.clear_fields())

        # Menu frame that shows the user's entries and allows them to add new entries
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(pady=20)

        # Registration frame
        self.register_frame = tk.Frame(self.root)
        self.register_label = tk.Label(self.register_frame, text="Register Master User", font=("Helvetica", 16, "bold"))
        self.register_label.grid(row=0, column=0, columnspan=2)
        self.register_username_label = tk.Label(self.register_frame, text="Username")
        self.register_username_label.grid(row=1, column=0)
        self.register_username_entry = tk.Entry(self.register_frame)
        self.register_username_entry.grid(row=1, column=1)
        self.register_password_label = tk.Label(self.register_frame, text="Master Password")
        self.register_password_label.grid(row=2, column=0)
        self.register_password_entry = tk.Entry(self.register_frame, show="*")
        self.register_password_entry.grid(row=2, column=1)
        self.register_button = tk.Button(self.register_frame, text="Register", command=self.register_master_user)
        self.register_button.grid(row=3, column=0, columnspan=2)

    def register_master_user(self):
        username = self.register_username_entry.get()
        master_password = self.register_password_entry.get()
        if username and master_password:
            hashed_password = self.password_manager.hash_password(master_password)
            self.password_manager.database.add_master_user(username, hashed_password, self.password_manager.salt)
            self.register_frame.pack_forget()
            self.login_frame.pack(pady=20)
        else:
            messagebox.showerror("Error", "Both username and master password are required!")

    def login(self):
        # Take the username and password from the entry fields and check them against the master username and password
        # database. If the credentials are correct, show the menu frame. Otherwise, show an error message.
        username = self.username_entry.get()
        password = self.password_entry.get()
        hashed_input_password = self.password_manager.hash_password(password)

        # Set the encryption key in the PasswordManager instance
        self.password_manager.set_key(password)
        if self.password_manager.login(username, hashed_input_password):
            self.login_frame.pack_forget()
            self.menu()
        else:
            messagebox.showerror("Error", "Invalid credentials!")

    def menu(self):
        # Clear the current frame
        self.entry_frame.pack_forget()
        self.root.geometry("1000x600")
        self.create_context_menu()

        # Treeview Style Sheet
        style = ttk.Style()
        self.bg_color = style.lookup('Treeview', 'background')
        style.configure("Treeview", background="#D3D3D3", foreground="black", rowheight=25, fieldbackground="#D3D3D3")

        # Treeview should have columns for platform, username, password, and notes.
        # Treeview should have a scrollbar
        self.tree = ttk.Treeview(self.menu_frame, columns=("Platform", "Username", "Password", "Notes"),
                                 show='headings')
        self.tree.heading("Platform", text="Platform")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Password", text="Password")
        self.tree.heading("Notes", text="Notes")
        self.tree.grid(row=0, column=0, columnspan=3, sticky='nsew')

        # Add a button to add a new entry
        self.add_entry_button = tk.Button(self.menu_frame, text="Add Entry", command=self.show_add_entry_frame)
        self.add_entry_button.grid(row=1, column=0, padx=10, pady=10)  # Place the button below the treeview

        # Add a button to delete an entry
        # self.delete_entry_button = tk.Button(self.menu_frame, text="Delete Entry", command=self.delete_entry)
        # self.delete_entry_button.grid(row=1, column=1, padx=10, pady=10)  # Place it next to Add Entry

        # Add a button to log out
        self.logout_button = tk.Button(self.menu_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=1, column=2, padx=10, pady=10)  # Place it next to Delete Entry

        # Blur the password by default
        self.tree.column("Password", width=100, stretch=tk.NO, anchor='w')

        # Bind the events to show and hide the password
        self.tree.bind("<Motion>", self.handle_motion)

        # Bind the event of clicking the note column to show the note popup
        self.tree.bind("<Button-1>", self.on_click)

        # Populate the treeview with the user's entries from the database
        self.populate_treeview()

        # Pack the menu_frame to display it
        self.menu_frame.pack(pady=20)

        # Create the right click context menu
        self.tree.bind("<Button-3>", self.show_context_menu)

    def create_context_menu(self):
        # Right click menu to edit, delete, or copy either the URL, username, or password to the clipboard
        # using pyperclip
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_entry)
        self.context_menu.add_command(label="Delete", command=self.delete_entry)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy URL", command=self.copy_url_to_clipboard)
        self.context_menu.add_command(label="Copy Username", command=self.copy_username_to_clipboard)
        self.context_menu.add_command(label="Copy Password", command=self.copy_password_to_clipboard)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Open URL", command=self.open_url)
        self.context_menu.add_command(label="SSH to Client", command=self.ssh_to_client)

    def show_context_menu(self, event):
        # Display the context menu
        self.context_menu.post(event.x_root, event.y_root)

    def edit_entry(self):
        try:
            selected_item = self.tree.selection()[0]
        except Exception as e:
            print(e)
            messagebox.showwarning("Warning", "Please select an entry to edit.")
            return

        platform, username, _, notes = self.tree.item(selected_item, 'values')
        decrypted_password = self.decrypted_passwords[(platform, username)]

        # Use the existing entry frame to edit the values
        self.menu_frame.pack_forget()
        self.entry_frame.pack(pady=20)

        # Populate the entry fields with the current values
        self.platform_entry.insert(0, platform)
        self.entry_username_entry.insert(0, username)
        self.entry_password_entry.insert(0, decrypted_password)
        self.entry_notes_entry.insert(0, notes)

        # Change the Add Entry button command to update the entry instead of adding a new one
        self.add_button.config(text="Update Entry", command=lambda: self.update_entry(selected_item))

    def reset_add_button(self):
        self.add_button.config(text="Add Entry", command=self.submit_entry)

    def update_entry(self, item):
        old_platform = self.tree.item(item, 'values')[0]
        old_username = self.tree.item(item, 'values')[1]
        platform = self.platform_entry.get()
        username = self.entry_username_entry.get()
        password = self.entry_password_entry.get()
        notes = self.entry_notes_entry.get()

        if platform and username and password:
            encrypted_password = self.password_manager.encrypt(password)
            # Update the entry in the database
            self.password_manager.database.conn.execute("""
                UPDATE passwords SET platform_name=?, username=?, encrypted_password=?, notes=? WHERE platform_name=?
                 AND username=?
            """, (platform, username, encrypted_password, notes, old_platform, old_username))
            self.password_manager.database.conn.commit()

            # Update the treeview
            self.tree.item(item, values=(platform, username, '*' * len(password), notes))
            self.decrypted_passwords[(platform, username)] = password

            # Clear the entry fields and return to the menu
            self.clear_fields()
            self.menu()
            self.reset_add_button()
        else:
            messagebox.showerror("Error", "Platform, Username, and Password are Required!")

    def delete_entry(self):
        try:
            selected_item = self.tree.selection()[0]
        except:
            messagebox.showwarning("Warning", "Please select an entry to delete.")
            return

        platform, username, _, _ = self.tree.item(selected_item, 'values')

        # Ask the user for confirmation before deleting
        confirm = messagebox.askyesno("Confirmation", f"Are you sure you want to delete the entry for {platform}?")
        if confirm:
            # Delete the entry from the database
            self.password_manager.database.delete_entry(platform, username)

            # Remove the item from the treeview
            self.tree.delete(selected_item)

        pass

    def copy_url_to_clipboard(self):
        try:
            selected_item = self.tree.selection()[0]
        except:
            messagebox.showwarning("Warning", "Please select an entry to copy the field.")
            return
        platform = self.tree.item(selected_item, "values")[0]
        pyperclip.copy(platform)

    def copy_username_to_clipboard(self):
        try:
            selected_item = self.tree.selection()[0]
        except:
            messagebox.showwarning("Warning", "Please select an entry to copy the field.")
            return
        username = self.tree.item(selected_item, "values")[1]
        pyperclip.copy(username)

    def copy_password_to_clipboard(self):
        try:
            selected_item = self.tree.selection()[0]
        except:
            messagebox.showwarning("Warning", "Please select an entry to copy the field.")
            return
        platform, username, _, _ = self.tree.item(selected_item, 'values')
        decrypted_password = self.decrypted_passwords[(platform, username)]
        pyperclip.copy(decrypted_password)

    def ssh_to_client(self):
        try:
            selected_item = self.tree.selection()[0]
        except:
            messagebox.showwarning("Warning", "Please select an entry to SSH to.")
            return

        platform, username, _, _ = self.tree.item(selected_item, 'values')

        # Check if the platform is an IP address
        if re.match(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", platform):
            # Ask the user for confirmation before SSHing
            confirm = messagebox.askyesno("Confirmation",
                                          f"Do you want to SSH to {platform} with the given credentials?")
            if confirm:
                # Open a new CMD window and SSH to the client
                cmd = f'start cmd /k ssh {username}@{platform}'
                subprocess.run(cmd, shell=True)
        else:
            messagebox.showwarning("Warning", "The selected platform is not an IP address.")
        pass

    def on_click(self, event):
        item = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)

        if item:
            values = self.tree.item(item, 'values')
            if col == "#4" and values[3]:  # Check if the notes column is being clicked
                self.show_note_popup(values[3], values[0])

    def open_url(self):
        url = self.tree.item(self.tree.selection()[0], "values")[0]
        if url.startswith(("https://", "http://", "www.")):
            webbrowser.open(url)

    def show_note_popup(self, note_text, platform_name):
        note_popup = tk.Toplevel(self.root)
        note_popup.title(f"{platform_name} Note")
        note_popup.geometry("300x200")
        note_label = tk.Label(note_popup, text=note_text, wraplength=250, justify=tk.LEFT)
        note_label.pack(pady=20, padx=20)
        close_button = tk.Button(note_popup, text="Close", command=note_popup.destroy)
        close_button.pack(pady=10)

    def handle_motion(self, event):
        item = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        values = self.tree.item(item, 'values')

        if item and col == "#3":  # Check if the password column is being hovered over
            if self.last_hovered_item and self.last_hovered_item != item:
                # Hide the previously hovered password
                self.hide_password_for_item(self.last_hovered_item)
            if len(values) == 4:
                platform, username, _, _ = values
                decrypted_password = self.decrypted_passwords[(platform, username)]
                if decrypted_password:
                    self.tree.set(item, column=col, value=decrypted_password)
                self.last_hovered_item = item
            else:
                self.last_hovered_item = None
        elif self.last_hovered_item:
            # Delay hiding the password to prevent flickering
            self.root.after(500, self.hide_password_for_item, self.last_hovered_item)

    def hide_password_for_item(self, item):
        platform, username, _, _ = self.tree.item(item, 'values')
        decrypted_password = self.decrypted_passwords[(platform, username)]
        if decrypted_password:
            self.tree.set(item, column="#3", value='*' * len(decrypted_password))

    def populate_treeview(self):
        # Fetch the entries from the database
        entries = self.password_manager.database.get_all_entries()
        for entry in entries:
            platform, username, encrypted_password, notes = entry
            decrypted_password = self.password_manager.decrypt(encrypted_password).decode('utf-8')
            self.decrypted_passwords[(platform, username)] = decrypted_password
            # Insert asterisks for the password column
            self.tree.insert("", 'end', values=(platform, username, '*' * len(decrypted_password), notes),
                             tags=('password',))

    def show_add_entry_frame(self):
        # Hide the menu frame and show the add entry frame
        self.menu_frame.pack_forget()
        self.entry_frame.pack(pady=20)

    def logout(self):
        # Clear the current frame and show the login frame
        self.menu_frame.pack_forget()
        self.login_frame.pack(pady=20)

    def submit_entry(self):
        # Take the platform, username, and password from the entry fields and add them to the password manager database.
        platform = self.platform_entry.get()
        username = self.entry_username_entry.get()
        password = self.entry_password_entry.get()
        notes = self.entry_notes_entry.get()

        if platform and username and password:
            self.password_manager.add_password_entry(platform, username, password, notes)
            messagebox.showinfo("Success", f"Added entry for {platform}!")

            # Clear the entry fields
            self.platform_entry.delete(0, tk.END)
            self.entry_username_entry.delete(0, tk.END)
            self.entry_password_entry.delete(0, tk.END)
            self.entry_notes_entry.delete(0, tk.END)

            # Return to the menu
            self.menu()
            self.reset_add_button()
        else:
            messagebox.showerror("Error", "Platform, Username, and Password are Required!")

    def display_entries(self):
        entries = self.password_manager.database.get_all_entries()
        for entry in entries:
            platform, username, encrypted_password, notes = entry
            decrypted_password = self.password_manager.decrypt(encrypted_password)
            print(f"Platform: {platform}\nUsername: {username}\nPassword: {decrypted_password}\nNotes: {notes}\n")

    def clear_fields(self):
        # Clear all the entry fields in the add entry frame
        self.platform_entry.delete(0, tk.END)
        self.entry_username_entry.delete(0, tk.END)
        self.entry_password_entry.delete(0, tk.END)
        self.entry_notes_entry.delete(0, tk.END)


class PasswordManager:
    def __init__(self):
        # Initialize the password manager database and other necessary components
        self.user = None
        self.key = None  # Derive a key from the master password and salt
        self.database = PasswordDatabase()  # Initialize the database
        user_details = self.database.get_master_user()
        if user_details:
            self.user = User(user_details[0], user_details[1])
            self.salt = user_details[2]
            self.key = self.derive_key(self.user.encrypted_master_password, self.salt)
            self.cypher_suite = Fernet(self.key)
        else:
            self.salt = os.urandom(16)  # Generate a random salt
            self.key = None
            self.cypher_suite = None

    def __del__(self):
        # Close the database connection when the PasswordManager instance is deleted
        self.database.close()

    def hash_password(self, password):
        salted_password = password.encode() + self.salt
        hashed = hashlib.sha256(salted_password).hexdigest()
        return hashed

    def register_user(self, username, master_password):
        self.set_key(master_password)
        encrypted_master_password = self.encrypt(master_password)
        # Save user to the database
        self.database.add_master_user(username, encrypted_master_password, self.salt)

    def set_key(self, master_password):
        self.key = self.derive_key(master_password, self.salt)
        self.cypher_suite = Fernet(self.key)

    def derive_key(self, password, salt):
        # Use PBKDF2 to derive a key from the master password and salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        # print(f"Derived Key: {key}")
        return base64.urlsafe_b64encode(key)  # Convert the key to a format that Fernet accepts

    def login(self, username, hashed_input_password):
        user_details = self.database.get_master_user(username)
        if user_details:
            self.user = User(user_details[0], user_details[1])
            self.salt = user_details[2]
            stored_hashed_password = self.user.encrypted_master_password
            return stored_hashed_password == hashed_input_password
        else:
            return False

    def add_password_entry(self, platform_name, username, password, notes=None):
        encrypted_password = self.encrypt(password)
        entry = PasswordEntry(platform_name, username, encrypted_password, notes)
        # Add the entry to the database
        self.database.add_entry(entry)

    def encrypt(self, data):
        encrypted_data = self.cypher_suite.encrypt(data.encode())
        return encrypted_data

    def decrypt(self, encrypted_data):
        decrypted_data = self.cypher_suite.decrypt(encrypted_data)
        return decrypted_data


class User:
    def __init__(self, username, encrypted_master_password):
        self.username = username
        self.encrypted_master_password = encrypted_master_password

    def authenticate(self, input_encrypted_password):
        return self.encrypted_master_password == input_encrypted_password


class PasswordEntry:
    # Instances of "Password Entry" are created to represent individual password entries. Each entry will have a
    # platform name ("Facebook"), username, encrypted password, and notes.
    def __init__(self, platform_name, username, encrypted_password, notes=None):
        self.platform_name = platform_name
        self.username = username
        self.encrypted_password = encrypted_password
        self.notes = notes


class PasswordDatabase:
    def __init__(self, db_name="password_manager.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def delete_entry(self, platform, username):
        self.conn.execute("""
                    DELETE FROM passwords WHERE platform_name=? AND username=?
                """, (platform, username))
        self.conn.commit()

    def master_user_exists(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM master_user")
        count = cursor.fetchone()[0]
        return count > 0

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY,
                    platform_name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    encrypted_password TEXT NOT NULL,
                    notes TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS master_user (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                encrypted_master_password TEXT NOT NULL,
                salt BLOB NOT NULL
                )
            """)

    def add_master_user(self, username, encrypted_master_password, salt):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO master_user (username, encrypted_master_password, salt)
                VALUES (?, ?, ?)
            """, (username, encrypted_master_password, salt))
            self.conn.commit()
            print("Master user added successfully!")
        except Exception as e:
            print(f"Error adding master user: {e}")

    def get_master_user(self, username=None):
        # Pull the master user from the database, which includes the username, encrypted master password, and salt.
        # This will be used to compare the user's input password against the stored password for login.
        try:
            cursor = self.conn.cursor()
            if username:
                cursor.execute("SELECT username, encrypted_master_password, salt FROM master_user WHERE username=?",
                               (username,))
            else:
                cursor.execute("SELECT username, encrypted_master_password, salt FROM master_user LIMIT 1")
            result = cursor.fetchone()
            return result
        except Exception as e:
            print(f"Error retrieving master user: {e}")

    def add_entry(self, entry):
        with self.conn:
            self.conn.execute("""
                INSERT INTO passwords (platform_name, username, encrypted_password, notes)
                VALUES (?, ?, ?, ?)
            """, (entry.platform_name, entry.username, entry.encrypted_password, entry.notes))

    def get_all_entries(self):
        with self.conn:
            cursor = self.conn.execute("SELECT platform_name, username, encrypted_password, notes FROM passwords")
            return cursor.fetchall()

    def close(self):
        self.conn.close()


def on_closing():
    # Close (and save) the database connection and destroy the root window
    gui.password_manager.database.close()
    root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    gui = PasswordManagerGUI(root)

    # Check if the master user exists
    if gui.password_manager.database.master_user_exists():
        gui.login_frame.pack(pady=20)
    else:
        gui.register_frame.pack(pady=20)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
