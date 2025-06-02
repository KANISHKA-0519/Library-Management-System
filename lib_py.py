import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import hashlib

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["LibraryDB"]
books_col = db["Books"]
users_col = db["Users"]  # This stores borrowing records
history_col = db["History"]
accounts_col = db["Accounts"]  # For login accounts

# Password hashing helper
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Library Management System")
        self.root.geometry("400x350")
        self.root.configure(bg="#00ced1")  # dark turquoise bg

        self.current_user = None
        self.current_role = None

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Segoe UI", 11), padding=6, background="#00b4d8", foreground="#000")
        self.style.configure("Hover.TButton", font=("Segoe UI", 11, "bold"), foreground="#ffb703", background="#023e8a")
        self.style.configure("TLabel", font=("Segoe UI", 11), background="#00ced1")

        self.login_ui()

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login_ui(self):
        self.clear_root()

        ttk.Label(self.root, text="Login", font=("Segoe UI", 24, "bold"), foreground="#0077b6", background="#00ced1").pack(pady=20)

        self.login_username_var = tk.StringVar()
        self.login_password_var = tk.StringVar()

        ttk.Label(self.root, text="Username:").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.login_username_var).pack()

        ttk.Label(self.root, text="Password:").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.login_password_var, show="*").pack()

        login_btn = ttk.Button(self.root, text="Login", command=self.handle_login)
        login_btn.pack(pady=15)

        ttk.Label(self.root, text="Don't have an account?", background="#00ced1").pack(pady=10)
        register_btn = ttk.Button(self.root, text="Register", command=self.register_ui)
        register_btn.pack()

        # Hover effect
        login_btn.bind("<Enter>", lambda e: login_btn.configure(style="Hover.TButton"))
        login_btn.bind("<Leave>", lambda e: login_btn.configure(style="TButton"))
        register_btn.bind("<Enter>", lambda e: register_btn.configure(style="Hover.TButton"))
        register_btn.bind("<Leave>", lambda e: register_btn.configure(style="TButton"))

    def register_ui(self):
        self.clear_root()

        ttk.Label(self.root, text="Register", font=("Segoe UI", 24, "bold"), foreground="#0077b6", background="#00ced1").pack(pady=20)

        self.reg_username_var = tk.StringVar()
        self.reg_password_var = tk.StringVar()
        self.reg_role_var = tk.StringVar(value="User")

        ttk.Label(self.root, text="Username:").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.reg_username_var).pack()

        ttk.Label(self.root, text="Password:").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.reg_password_var, show="*").pack()

        ttk.Label(self.root, text="Role:").pack(pady=5)
        role_combo = ttk.Combobox(self.root, textvariable=self.reg_role_var, values=["User", "Admin"], state="readonly")
        role_combo.pack()

        register_btn = ttk.Button(self.root, text="Register", command=self.handle_register)
        register_btn.pack(pady=15)

        back_btn = ttk.Button(self.root, text="Back to Login", command=self.login_ui)
        back_btn.pack()

        register_btn.bind("<Enter>", lambda e: register_btn.configure(style="Hover.TButton"))
        register_btn.bind("<Leave>", lambda e: register_btn.configure(style="TButton"))
        back_btn.bind("<Enter>", lambda e: back_btn.configure(style="Hover.TButton"))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(style="TButton"))

    def handle_register(self):
        username = self.reg_username_var.get().strip()
        password = self.reg_password_var.get().strip()
        role = self.reg_role_var.get()

        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

        # Check if user exists
        if accounts_col.find_one({"username": username}):
            messagebox.showerror("Error", "Username already exists.")
            return

        accounts_col.insert_one({
            "username": username,
            "password": hash_password(password),
            "role": role
        })
        messagebox.showinfo("Success", f"Account created successfully as {role}!")
        self.login_ui()

    def handle_login(self):
        username = self.login_username_var.get().strip()
        password = self.login_password_var.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password.")
            return

        account = accounts_col.find_one({"username": username})
        if not account or account["password"] != hash_password(password):
            messagebox.showerror("Error", "Invalid username or password.")
            return

        self.current_user = username
        self.current_role = account["role"]
        messagebox.showinfo("Welcome", f"Welcome {self.current_user}! Role: {self.current_role}")
        self.main_ui()

    def main_ui(self):
        self.clear_root()
        self.root.title(f"Library Management System - {self.current_user} ({self.current_role})")
        self.root.geometry("1000x650")
        self.root.configure(bg="#00ced1")

        # Title
        header = ttk.Frame(self.root)
        header.pack(pady=20)
        title_label = ttk.Label(header, text="📚 Library Management System", font=("Segoe UI", 26, "bold"), foreground="#0077b6")
        title_label.pack()

        # Navigation Bar
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(pady=15)

        buttons = [
            ("Add Book", self.add_book_ui),
            ("Borrow Book", self.borrow_book_ui),
            ("Return Book", self.return_book_ui),
            ("View Books", self.view_books_ui),
            ("View History", self.view_history_ui),
            ("Logout", self.logout)
        ]

        for idx, (text, cmd) in enumerate(buttons):
            btn = ttk.Button(nav_frame, text=text, command=cmd, style="TButton")
            btn.grid(row=0, column=idx, padx=10, pady=6)

            # Disable Add Book button if not admin
            if text == "Add Book" and self.current_role != "Admin":
                btn.state(["disabled"])

            # Hover effect
            def on_enter(e, b=btn): b.configure(style="Hover.TButton")
            def on_leave(e, b=btn): b.configure(style="TButton")
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

        # Footer
        footer = ttk.Label(self.root, text="🌊 Dark Turquoise & Yellow Theme | Built with Tkinter + MongoDB",
                           font=("Segoe UI", 10), foreground="#0077b6")
        footer.pack(side=tk.BOTTOM, pady=15)

    def logout(self):
        self.current_user = None
        self.current_role = None
        self.root.title("Login - Library Management System")
        self.root.geometry("400x350")
        self.login_ui()

    # The following methods remain mostly same, only add minor tweaks to check current_user and current_role if needed.

    def add_book_ui(self):
        if self.current_role != "Admin":
            messagebox.showerror("Unauthorized", "Only Admin can add books.")
            return

        def add_book():
            book = {
                "title": title_var.get(),
                "author": author_var.get(),
                "year": year_var.get(),
                "genre": genre_var.get(),
                "available": True
            }
            books_col.insert_one(book)
            messagebox.showinfo("Success", "Book added successfully!")
            top.destroy()

        top = tk.Toplevel(self.root)
        top.title("Add Book")
        top.geometry("300x300")
        top.configure(bg="#fefae0")

        title_var = tk.StringVar()
        author_var = tk.StringVar()
        year_var = tk.StringVar()
        genre_var = tk.StringVar()

        for label, var in zip(["Title", "Author", "Year", "Genre"], [title_var, author_var, year_var, genre_var]):
            ttk.Label(top, text=label).pack(pady=2)
            ttk.Entry(top, textvariable=var).pack(pady=2)

        ttk.Button(top, text="Add", command=add_book).pack(pady=10)

    def borrow_book_ui(self):
        def borrow():
            title = title_var.get().strip()
            username = self.current_user
            book = books_col.find_one({"title": {"$regex": f"^{title}$", "$options": "i"}, "available": True})

            if book:
                books_col.update_one({"_id": book["_id"]}, {"$set": {"available": False}})
                record = {
                    "username": username,
                    "book_id": str(book["_id"]),
                    "book_title": book["title"],
                    "borrowed_on": datetime.datetime.now()
                }
                users_col.insert_one(record)
                history_col.insert_one({**record, "action": "borrowed"})
                messagebox.showinfo("Success", "Book borrowed!")
                top.destroy()
            else:
                messagebox.showerror("Error", "Book not available")

        top = tk.Toplevel(self.root)
        top.title("Borrow Book")
        top.geometry("300x200")
        top.configure(bg="#fefae0")

        title_var = tk.StringVar()

        ttk.Label(top, text="Book Title").pack(pady=2)
        ttk.Entry(top, textvariable=title_var).pack(pady=2)
        ttk.Label(top, text=f"Borrower: {self.current_user}").pack(pady=5)

        ttk.Button(top, text="Borrow", command=borrow).pack(pady=10)

    def return_book_ui(self):
        def return_book():
            username = self.current_user
            title = title_var.get().strip()

            user_record = users_col.find_one({
                "username": {"$regex": f"^{username}$", "$options": "i"},
                "book_title": {"$regex": f"^{title}$", "$options": "i"}
            })

            if user_record:
                book_id = ObjectId(user_record["book_id"])
                books_col.update_one({"_id": book_id}, {"$set": {"available": True}})
                users_col.delete_one({"_id": user_record["_id"]})
                history_col.insert_one({
                    "username": user_record["username"],
                    "book_id": user_record["book_id"],
                    "book_title": user_record["book_title"],
                    "action": "returned",
                    "returned_on": datetime.datetime.now()
                })
                messagebox.showinfo("Success", "Book returned successfully!")
                top.destroy()
            else:
                user_books = list(users_col.find({
                    "username": {"$regex": f"^{username}$", "$options": "i"}
                }))
                if user_books:
                    books_list = "\n".join([f"- {book['book_title']}" for book in user_books])
                    messagebox.showerror(
                        "Error",
                        f"No matching book found. Books borrowed by '{username}':\n{books_list}"
                    )
                else:
                    messagebox.showerror(
                        "Error",
                        "No record found. Ensure the book title is correct."
                    )

        top = tk.Toplevel(self.root)
        top.title("Return Book")
        top.geometry("300x200")
        top.configure(bg="#fefae0")

        title_var = tk.StringVar()

        ttk.Label(top, text="Book Title").pack(pady=2)
        ttk.Entry(top, textvariable=title_var).pack(pady=2)
        ttk.Label(top, text=f"User: {self.current_user}").pack(pady=5)
        ttk.Button(top, text="Return", command=return_book).pack(pady=10)

    def view_books_ui(self):
        top = tk.Toplevel(self.root)
        top.title("Available Books")
        top.geometry("700x400")
        top.configure(bg="#f0f0f0")

        tree = ttk.Treeview(top, columns=("Title", "Author", "Year", "Genre", "Available"), show="headings")
        for col in ("Title", "Author", "Year", "Genre", "Available"):
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER)

        tree.pack(fill=tk.BOTH, expand=True)

        for book in books_col.find():
            tree.insert("", tk.END, values=(
                book.get("title"),
                book.get("author"),
                book.get("year"),
                book.get("genre", "-"),
                "Yes" if book["available"] else "No"
            ))

    def view_history_ui(self):
        top = tk.Toplevel(self.root)
        top.title("Borrowing History")
        top.geometry("800x400")
        top.configure(bg="#f0f0f0")

        tree = ttk.Treeview(top, columns=("Username", "Book Title", "Action", "Date"), show="headings")
        for col in ("Username", "Book Title", "Action", "Date"):
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER)

        tree.pack(fill=tk.BOTH, expand=True)

        for entry in history_col.find():
            date = entry.get("borrowed_on") or entry.get("returned_on")
            date_str = date.strftime("%Y-%m-%d %H:%M") if date else "-"
            tree.insert("", tk.END, values=(
                entry.get("username"),
                entry.get("book_title"),
                entry.get("action"),
                date_str
            ))

if __name__ == '__main__':
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()
