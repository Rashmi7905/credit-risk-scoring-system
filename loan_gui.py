import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# ---------- DATABASE CONNECTION ----------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Igdtuw@123",
        database="credit_risk_db"
    )

# ---------- FETCH DATA FUNCTIONS ----------
def fetch_loans(search_term=""):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT l.loan_id, a.age, a.monthly_income, l.loan_purpose,
               l.credit_score, l.status, r.final_risk_score, r.recommendation
        FROM loans l
        JOIN applicants a ON l.applicant_id = a.applicant_id
        JOIN risk_assessments r ON l.loan_id = r.loan_id
        WHERE l.loan_purpose LIKE %s OR l.status LIKE %s
        LIMIT 100
    """
    cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM loans")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM loans WHERE status='Approved'")
    approved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM loans WHERE status='Rejected'")
    rejected = cursor.fetchone()[0]

    cursor.execute("SELECT ROUND(AVG(final_risk_score),2) FROM risk_assessments")
    avg_score = cursor.fetchone()[0]

    conn.close()
    return total, approved, rejected, avg_score

def calculate_risk(income, credit_score, dti):
    income_score = min(100, (income / 250000) * 100)
    credit_factor = (credit_score - 300) / 6.0
    dti_score = max(0, 100 - (dti * 133))
    final = round(income_score * 0.25 + credit_factor * 0.35 + dti_score * 0.40, 2)
    if final >= 65:
        return final, "APPROVE", "green"
    elif final >= 45:
        return final, "REVIEW", "orange"
    else:
        return final, "REJECT", "red"

# ---------- MAIN WINDOW ----------
root = tk.Tk()
root.title("Credit Risk Scoring & Loan Approval System")
root.geometry("1000x650")
root.configure(bg="#f0f4f8")

# ---------- TITLE BAR ----------
title_frame = tk.Frame(root, bg="#0f2744", pady=12)
title_frame.pack(fill="x")
tk.Label(title_frame, text="Credit Risk Scoring & Loan Approval System",
         font=("Arial", 16, "bold"), fg="white", bg="#0f2744").pack()
tk.Label(title_frame, text="Real-time analysis on 32,581 loan records",
         font=("Arial", 9), fg="#aac4e0", bg="#0f2744").pack()

# ---------- TABS ----------
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

style = ttk.Style()
style.configure("TNotebook.Tab", font=("Arial", 10), padding=[12, 5])

# ============================
# TAB 1 — DASHBOARD
# ============================
tab1 = tk.Frame(notebook, bg="#f0f4f8")
notebook.add(tab1, text="  Dashboard  ")

def load_dashboard():
    total, approved, rejected, avg_score = fetch_stats()
    approval_rate = round((approved / total) * 100, 1)

    stats = [
        ("Total Applications", str(total), "#1a6ab1"),
        ("Approved", str(approved), "#1d7a4f"),
        ("Rejected", str(rejected), "#b83232"),
        ("Avg Risk Score", str(avg_score), "#b87a00"),
    ]

    for widget in stats_frame.winfo_children():
        widget.destroy()

    for label, value, color in stats:
        card = tk.Frame(stats_frame, bg="white", relief="flat",
                        highlightbackground="#ddd", highlightthickness=1)
        card.pack(side="left", expand=True, fill="both", padx=8, pady=8)
        tk.Label(card, text=label, font=("Arial", 9), fg="#666",
                 bg="white").pack(pady=(12,2))
        tk.Label(card, text=value, font=("Arial", 22, "bold"),
                 fg=color, bg="white").pack()
        tk.Label(card, text=" ", bg="white").pack(pady=4)

    approval_label.config(text=f"Overall Approval Rate: {approval_rate}%")

stats_frame = tk.Frame(tab1, bg="#f0f4f8")
stats_frame.pack(fill="x", padx=10, pady=10)

approval_label = tk.Label(tab1, text="", font=("Arial", 12, "bold"),
                           fg="#0f2744", bg="#f0f4f8")
approval_label.pack(pady=5)

tk.Button(tab1, text="Refresh Stats", command=load_dashboard,
          font=("Arial", 10), bg="#0f2744", fg="white",
          relief="flat", padx=15, pady=6).pack(pady=5)

load_dashboard()

# ============================
# TAB 2 — VIEW LOANS
# ============================
tab2 = tk.Frame(notebook, bg="#f0f4f8")
notebook.add(tab2, text="  Loan Applications  ")

search_frame = tk.Frame(tab2, bg="#f0f4f8")
search_frame.pack(fill="x", padx=10, pady=8)
tk.Label(search_frame, text="Search:", font=("Arial", 10),
         bg="#f0f4f8").pack(side="left")
search_var = tk.StringVar()
search_entry = tk.Entry(search_frame, textvariable=search_var,
                        font=("Arial", 10), width=30)
search_entry.pack(side="left", padx=8)

def load_table(search=""):
    for row in tree.get_children():
        tree.delete(row)
    rows = fetch_loans(search)
    for i, row in enumerate(rows):
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        tree.insert("", "end", values=row, tags=(tag,))

tk.Button(search_frame, text="Search", font=("Arial", 10),
          bg="#1a6ab1", fg="white", relief="flat", padx=10,
          command=lambda: load_table(search_var.get())).pack(side="left")
tk.Button(search_frame, text="Show All", font=("Arial", 10),
          bg="#666", fg="white", relief="flat", padx=10,
          command=lambda: load_table()).pack(side="left", padx=5)

columns = ("ID", "Age", "Income", "Purpose", "Credit Score", "Status", "Risk Score", "Decision")
tree = ttk.Treeview(tab2, columns=columns, show="headings", height=20)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=110, anchor="center")

tree.tag_configure("evenrow", background="#f8f9fa")
tree.tag_configure("oddrow", background="white")

scrollbar = ttk.Scrollbar(tab2, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side="left", fill="both", expand=True, padx=(10,0), pady=5)
scrollbar.pack(side="right", fill="y", pady=5)

load_table()

# ============================
# TAB 3 — RISK CALCULATOR
# ============================
tab3 = tk.Frame(notebook, bg="#f0f4f8")
notebook.add(tab3, text="  Risk Calculator  ")

form_frame = tk.Frame(tab3, bg="white", relief="flat",
                      highlightbackground="#ddd", highlightthickness=1)
form_frame.pack(pady=20, padx=40, fill="x")

tk.Label(form_frame, text="New Applicant Risk Assessment",
         font=("Arial", 13, "bold"), fg="#0f2744",
         bg="white").grid(row=0, column=0, columnspan=2, pady=(15,10))

fields = [
    ("Monthly Income (₹)", "income_entry"),
    ("Credit Score (300-900)", "credit_entry"),
    ("Debt-to-Income Ratio (0.0-1.0)", "dti_entry"),
]

entries = {}
for i, (label, key) in enumerate(fields, start=1):
    tk.Label(form_frame, text=label, font=("Arial", 10),
             bg="white", fg="#333").grid(row=i, column=0, padx=20, pady=8, sticky="w")
    entry = tk.Entry(form_frame, font=("Arial", 11), width=20,
                     relief="solid", bd=1)
    entry.grid(row=i, column=1, padx=20, pady=8)
    entries[key] = entry

result_frame = tk.Frame(tab3, bg="white", relief="flat",
                        highlightbackground="#ddd", highlightthickness=1)
result_frame.pack(pady=10, padx=40, fill="x")

score_label = tk.Label(result_frame, text="Risk Score: --",
                       font=("Arial", 20, "bold"), fg="#0f2744", bg="white")
score_label.pack(pady=(15,5))

decision_label = tk.Label(result_frame, text="Decision: --",
                          font=("Arial", 14), fg="#666", bg="white")
decision_label.pack(pady=(0,15))

def run_calculator():
    try:
        income = float(entries["income_entry"].get())
        credit = float(entries["credit_entry"].get())
        dti = float(entries["dti_entry"].get())

        if not (300 <= credit <= 900):
            messagebox.showerror("Error", "Credit score must be between 300 and 900")
            return
        if not (0 <= dti <= 1):
            messagebox.showerror("Error", "DTI ratio must be between 0.0 and 1.0")
            return

        score, decision, color = calculate_risk(income, credit, dti)
        score_label.config(text=f"Risk Score: {score} / 100")
        decision_label.config(text=f"Decision: {decision}", fg=color)

    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers in all fields")

tk.Button(form_frame, text="Calculate Risk Score",
          command=run_calculator,
          font=("Arial", 11, "bold"), bg="#0f2744", fg="white",
          relief="flat", padx=20, pady=8).grid(row=4, column=0,
          columnspan=2, pady=15)

# ---------- RUN ----------
root.mainloop()