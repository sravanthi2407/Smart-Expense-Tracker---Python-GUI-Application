import json
import os
import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageFilter
import matplotlib.pyplot as plt

# ---------------- THEME ----------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

FILE = "expenses.json"

# ---------------- DATA ----------------
def load_expenses():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def save_expenses(expenses):
    with open(FILE, "w") as f:
        json.dump(expenses, f, indent=4)

# ---------------- ADD ----------------
def add_expense():
    try:
        amount = float(amount_entry.get())
        category = category_entry.get()

        if category == "":
            messagebox.showerror("Error", "Category required")
            return

        expense = {
            "amount": amount,
            "category": category,
            "date": date_entry.get()
        }

        expenses = load_expenses()
        expenses.append(expense)
        save_expenses(expenses)

        update_table()
        clear_fields()

    except ValueError:
        messagebox.showerror("Error", "Enter valid amount")

# ---------------- DELETE ----------------
def delete_expense():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning("Warning", "Select an expense")
        return

    index = int(selected[0])
    expenses = load_expenses()

    expenses.pop(index)
    save_expenses(expenses)

    update_table()

# ---------------- UPDATE TABLE ----------------
def update_table(filter_category=None):
    for row in tree.get_children():
        tree.delete(row)

    expenses = load_expenses()
    total = 0

    for i, exp in enumerate(expenses):
        if filter_category and exp["category"].lower() != filter_category.lower():
            continue

        amount = f"₹ {exp['amount']:.2f}"

        tag = "evenrow" if i % 2 == 0 else "oddrow"

        tree.insert("", "end", iid=i,
                    values=(amount, exp["category"], exp["date"]),
                    tags=(tag,))

        total += exp["amount"]

    # Zebra colors
    tree.tag_configure("evenrow", background="#2a2a2a")
    tree.tag_configure("oddrow", background="#1e1e1e")

    total_label.configure(text=f"Total: ₹ {total:.2f}")

# ---------------- HELPERS ----------------
def clear_fields():
    amount_entry.delete(0, "end")
    category_entry.delete(0, "end")

def filter_expenses():
    update_table(filter_entry.get())

def show_all():
    filter_entry.delete(0, "end")
    update_table()

# ---------------- CHART ----------------
def show_chart():
    expenses = load_expenses()

    if not expenses:
        messagebox.showwarning("No Data", "No expenses to show")
        return

    category_totals = {}

    for exp in expenses:
        cat = exp["category"]
        category_totals[cat] = category_totals.get(cat, 0) + exp["amount"]

    categories = list(category_totals.keys())
    amounts = list(category_totals.values())

    plt.figure(figsize=(8, 5))
    bars = plt.bar(categories, amounts)

    # values on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2,
                 height,
                 f'{int(height)}',
                 ha='center',
                 va='bottom')

    plt.title("Expense Distribution by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount (₹)")
    plt.xticks(rotation=20)
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.show()

# ---------------- UI ----------------
app = ctk.CTk()
app.title("Smart Expense Tracker")
app.geometry("900x650")

# ---------------- BACKGROUND ----------------
try:
    original = Image.open("bg.png").resize((900, 650))
    blurred = original.filter(ImageFilter.GaussianBlur(6))

    bg_image = ctk.CTkImage(light_image=blurred,
                            dark_image=blurred,
                            size=(900, 650))

    bg_label = ctk.CTkLabel(app, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

except Exception as e:
    print("Background error:", e)

# ---------------- TITLE ----------------
title = ctk.CTkLabel(app,
                     text="💰 Smart Expense Tracker",
                     font=("Segoe UI", 32, "bold"),
                     text_color="white")
title.pack(pady=15)

# ---------------- CONTAINER ----------------
container = ctk.CTkFrame(app, fg_color="transparent")
container.pack(padx=20, pady=10, fill="both", expand=True)

# ---------------- INPUT ----------------
input_frame = ctk.CTkFrame(container, fg_color="transparent")
input_frame.pack(pady=10, fill="x")

amount_entry = ctk.CTkEntry(input_frame, placeholder_text="Amount (₹)")
amount_entry.pack(pady=5, fill="x", padx=10)

category_entry = ctk.CTkEntry(input_frame, placeholder_text="Category")
category_entry.pack(pady=5, fill="x", padx=10)

date_entry = DateEntry(input_frame, date_pattern="dd-mm-yyyy")
date_entry.pack(pady=5, fill="x", padx=10)

# ---------------- BUTTONS ----------------
btn_frame = ctk.CTkFrame(container, fg_color="transparent")
btn_frame.pack(pady=10)

ctk.CTkButton(btn_frame, text="Add", command=add_expense).grid(row=0, column=0, padx=10)
ctk.CTkButton(btn_frame, text="Delete", command=delete_expense).grid(row=0, column=1, padx=10)
ctk.CTkButton(btn_frame, text="Chart", command=show_chart).grid(row=0, column=2, padx=10)

# ---------------- FILTER ----------------
filter_frame = ctk.CTkFrame(container, fg_color="transparent")
filter_frame.pack(pady=10)

filter_entry = ctk.CTkEntry(filter_frame, placeholder_text="Filter Category")
filter_entry.grid(row=0, column=0, padx=10)

ctk.CTkButton(filter_frame, text="Filter", command=filter_expenses).grid(row=0, column=1, padx=10)
ctk.CTkButton(filter_frame, text="Show All", command=show_all).grid(row=0, column=2, padx=10)

# ---------------- MODERN TABLE ----------------
style = ttk.Style()
style.theme_use("default")

style.configure("Treeview.Heading",
                font=("Segoe UI", 13, "bold"),
                background="#2b2b2b",
                foreground="white",
                padding=10)

style.configure("Treeview",
                font=("Segoe UI", 12),
                rowheight=35,
                background="#1e1e1e",
                foreground="white",
                fieldbackground="#1e1e1e",
                borderwidth=0)

style.map("Treeview",
          background=[("selected", "#4a90e2")])

tree = ttk.Treeview(container,
                    columns=("Amount", "Category", "Date"),
                    show="headings",
                    height=10)

tree.heading("Amount", text="Amount (₹)")
tree.heading("Category", text="Category")
tree.heading("Date", text="Date")

tree.column("Amount", anchor="center", width=120)
tree.column("Category", anchor="center", width=150)
tree.column("Date", anchor="center", width=120)

tree.pack(pady=15, fill="x")

# ---------------- TOTAL ----------------
total_label = ctk.CTkLabel(container,
                           text="Total: ₹ 0.00",
                           font=("Segoe UI", 18, "bold"))
total_label.pack(pady=10)

# ---------------- START ----------------
update_table()

try:
    app.mainloop()
except KeyboardInterrupt:
    print("App closed safely")