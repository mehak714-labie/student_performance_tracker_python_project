# ============================================================
#  main.py  —  Student Performance Tracker
#  BTech CS-II | Python Programming Project
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import database as db
import analytics
import charts

# ── Colors ───────────────────────────────────────────────────
BG       = "#1e1e2e"
PANEL    = "#181825"
ACCENT   = "#89b4fa"
FG       = "#cdd6f4"
RED      = "#f38ba8"
GREEN    = "#a6e3a1"
YELLOW   = "#f9e2af"
ENTRY_BG = "#313244"


# ════════════════════════════════════════════════════════════
#  TAB 1 — STUDENT MANAGEMENT
# ════════════════════════════════════════════════════════════

def build_students_tab(parent):
    frame = tk.Frame(parent, bg=BG)
    frame.pack(fill="both", expand=True)

    # --- Left: input form ---
    left = tk.Frame(frame, bg=PANEL, width=270, padx=20, pady=20)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    tk.Label(left, text="Student Details", bg=PANEL, fg=ACCENT,
             font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 14))

    # Input fields — updated labels
    entries = {}
    for field in ["Full Name", "SAP ID", "Batch No", "Course"]:
        tk.Label(left, text=field, bg=PANEL, fg=FG, font=("Arial", 10)).pack(anchor="w")
        e = tk.Entry(left, bg=ENTRY_BG, fg=FG, insertbackground=FG,
                     relief="flat", font=("Arial", 11), bd=6)
        e.pack(fill="x", pady=(2, 10))
        entries[field] = e

    selected_id = [None]

    def clear_form():
        for e in entries.values():
            e.delete(0, tk.END)
        selected_id[0] = None
        btn_save.config(text="➕  Add Student")

    def save_student():
        name   = entries["Full Name"].get().strip()
        sap_id = entries["SAP ID"].get().strip()
        batch  = entries["Batch No"].get().strip()
        course = entries["Course"].get().strip()

        if not all([name, sap_id, batch, course]):
            messagebox.showwarning("Missing Fields", "Please fill in all fields.")
            return

        if selected_id[0]:
            db.update_student(selected_id[0], name, sap_id, batch, course)
        else:
            db.add_student(name, sap_id, batch, course)

        clear_form()
        load_table()

    def delete_student():
        selection = table.selection()
        if not selection:
            messagebox.showinfo("Select Student", "Click on a student first.")
            return
        sid     = selection[0]
        student = db.get_student(sid)
        if messagebox.askyesno("Confirm Delete",
                               f"Delete {student['name']} and all their marks?"):
            db.delete_student(sid)
            clear_form()
            load_table()

    def on_row_click(event):
        selection = table.selection()
        if not selection:
            return
        sid     = selection[0]
        student = db.get_student(sid)
        if student:
            entries["Full Name"].delete(0, tk.END)
            entries["Full Name"].insert(0, student["name"])
            entries["SAP ID"].delete(0, tk.END)
            entries["SAP ID"].insert(0, student.get("sap_id", ""))
            entries["Batch No"].delete(0, tk.END)
            entries["Batch No"].insert(0, student.get("batch", ""))
            entries["Course"].delete(0, tk.END)
            entries["Course"].insert(0, student.get("course", ""))
            selected_id[0] = sid
            btn_save.config(text="💾  Update Student")

    btn_save = tk.Button(left, text="➕  Add Student", bg=ACCENT, fg="#1e1e2e",
                         font=("Arial", 10, "bold"), relief="flat", cursor="hand2",
                         padx=10, pady=7, command=save_student)
    btn_save.pack(fill="x", pady=(4, 4))

    tk.Button(left, text="🗑  Delete Selected", bg=RED, fg="#1e1e2e",
              font=("Arial", 10, "bold"), relief="flat", cursor="hand2",
              padx=10, pady=7, command=delete_student).pack(fill="x", pady=(0, 4))

    tk.Button(left, text="✖  Clear Form", bg=ENTRY_BG, fg=FG,
              font=("Arial", 10), relief="flat", cursor="hand2",
              padx=10, pady=7, command=clear_form).pack(fill="x")

    # --- Right: table ---
    right = tk.Frame(frame, bg=BG, padx=16, pady=16)
    right.pack(side="left", fill="both", expand=True)

    search_row = tk.Frame(right, bg=BG)
    search_row.pack(fill="x", pady=(0, 10))
    tk.Label(search_row, text="🔍  Search:", bg=BG, fg=FG, font=("Arial", 10)).pack(side="left")
    search_var = tk.StringVar()

    def on_search(*args):
        query = search_var.get().strip()
        load_table(db.search_students(query) if query else None)

    search_var.trace("w", on_search)
    tk.Entry(search_row, textvariable=search_var, bg=ENTRY_BG, fg=FG,
             insertbackground=FG, relief="flat", font=("Arial", 11),
             bd=6, width=30).pack(side="left", padx=8)

    # Table columns — updated headers
    _style_table("Students")
    table = ttk.Treeview(right,
                         columns=("Name", "SAP ID", "Batch No", "Course"),
                         show="headings", style="Students.Treeview")
    for col, width in [("Name", 180), ("SAP ID", 110), ("Batch No", 100), ("Course", 130)]:
        table.heading(col, text=col)
        table.column(col, width=width, anchor="center")
    table.pack(fill="both", expand=True)
    table.bind("<<TreeviewSelect>>", on_row_click)

    def load_table(data=None):
        table.delete(*table.get_children())
        for s in (data if data is not None else db.get_all_students()):
            table.insert("", "end", iid=str(s["_id"]),
                         values=(s["name"],
                                 s.get("sap_id", ""),
                                 s.get("batch", ""),
                                 s.get("course", "")))
    load_table()


# ════════════════════════════════════════════════════════════
#  TAB 2 — MARKS ENTRY
# ════════════════════════════════════════════════════════════

def build_marks_tab(parent):
    frame = tk.Frame(parent, bg=BG)
    frame.pack(fill="both", expand=True)

    left = tk.Frame(frame, bg=PANEL, width=300, padx=20, pady=20)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    tk.Label(left, text="Enter Marks", bg=PANEL, fg=ACCENT,
             font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 12))

    tk.Label(left, text="Select Student", bg=PANEL, fg=FG, font=("Arial", 10)).pack(anchor="w")
    student_var = tk.StringVar()
    student_cb  = ttk.Combobox(left, textvariable=student_var,
                                state="readonly", font=("Arial", 10), width=28)
    student_cb.pack(fill="x", pady=(2, 10))
    student_cb._data = []

    tk.Label(left, text="Exam", bg=PANEL, fg=FG, font=("Arial", 10)).pack(anchor="w")
    exam_var = tk.StringVar(value=db.EXAMS[0])
    exam_cb  = ttk.Combobox(left, textvariable=exam_var, values=db.EXAMS,
                             state="readonly", font=("Arial", 10), width=28)
    exam_cb.pack(fill="x", pady=(2, 14))

    tk.Label(left, text="Marks per Subject (0–100)", bg=PANEL,
             fg=ACCENT, font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 6))

    mark_entries = {}
    for subject in db.SUBJECTS:
        row = tk.Frame(left, bg=PANEL)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=subject, bg=PANEL, fg=FG,
                 font=("Arial", 9), width=12, anchor="w").pack(side="left")
        e = tk.Entry(row, bg=ENTRY_BG, fg=FG, insertbackground=FG,
                     relief="flat", font=("Arial", 11), bd=4, width=6)
        e.pack(side="right")
        mark_entries[subject] = e

    def refresh_students():
        all_students        = db.get_all_students()
        student_cb._data    = all_students
        # Show name + SAP ID in dropdown
        student_cb["values"] = [f"{s['name']} ({s.get('sap_id','')})" for s in all_students]

    def prefill_marks(*args):
        idx = student_cb.current()
        if idx < 0:
            return
        sid      = str(student_cb._data[idx]["_id"])
        exam     = exam_var.get()
        existing = next((r for r in db.get_student_marks(sid) if r["exam"] == exam), None)
        for subject, entry in mark_entries.items():
            entry.delete(0, tk.END)
            if existing and subject in existing["marks"]:
                entry.insert(0, str(int(existing["marks"][subject])))

    student_cb.bind("<<ComboboxSelected>>", prefill_marks)
    exam_cb.bind("<<ComboboxSelected>>",    prefill_marks)

    def save_marks():
        idx = student_cb.current()
        if idx < 0:
            messagebox.showwarning("No Student", "Please select a student first.")
            return
        sid  = str(student_cb._data[idx]["_id"])
        exam = exam_var.get()
        marks_dict = {}
        for subject, entry in mark_entries.items():
            value = entry.get().strip()
            if value == "":
                messagebox.showwarning("Missing", f"Please enter marks for {subject}.")
                return
            try:
                score = float(value)
                if not (0 <= score <= 100):
                    raise ValueError
                marks_dict[subject] = score
            except ValueError:
                messagebox.showerror("Invalid", f"{subject} marks must be between 0 and 100.")
                return
        db.save_marks(sid, exam, marks_dict)
        messagebox.showinfo("Saved ✅", f"Marks for {exam} saved successfully!")
        load_records_table()

    def delete_marks():
        idx = student_cb.current()
        if idx < 0:
            return
        sid  = str(student_cb._data[idx]["_id"])
        exam = exam_var.get()
        if messagebox.askyesno("Delete", f"Delete {exam} marks for this student?"):
            db.marks_col.delete_one({"student_id": sid, "exam": exam})
            for e in mark_entries.values():
                e.delete(0, tk.END)
            load_records_table()

    tk.Button(left, text="💾  Save Marks", bg=ACCENT, fg="#1e1e2e",
              font=("Arial", 10, "bold"), relief="flat", cursor="hand2",
              padx=10, pady=7, command=save_marks).pack(fill="x", pady=(14, 4))

    tk.Button(left, text="🗑  Delete Record", bg=RED, fg="#1e1e2e",
              font=("Arial", 10, "bold"), relief="flat", cursor="hand2",
              padx=10, pady=7, command=delete_marks).pack(fill="x")

    right = tk.Frame(frame, bg=BG, padx=16, pady=16)
    right.pack(side="left", fill="both", expand=True)

    tk.Label(right, text="All Marks Records", bg=BG, fg=ACCENT,
             font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))

    # Updated column: SAP ID instead of Roll
    cols = ["Student", "SAP ID", "Exam"] + db.SUBJECTS + ["Avg", "Grade"]
    _style_table("Marks")
    records_table = ttk.Treeview(right, columns=cols, show="headings",
                                  style="Marks.Treeview")
    widths = {"Student": 110, "SAP ID": 90, "Exam": 60, "Avg": 55, "Grade": 55}
    for col in cols:
        records_table.heading(col, text=col)
        records_table.column(col, width=widths.get(col, 85), anchor="center")

    sb = ttk.Scrollbar(right, orient="horizontal", command=records_table.xview)
    records_table.configure(xscrollcommand=sb.set)
    records_table.pack(fill="both", expand=True)
    sb.pack(fill="x")

    def load_records_table():
        records_table.delete(*records_table.get_children())
        student_map = {str(s["_id"]): s for s in db.get_all_students()}
        for rec in db.get_all_marks():
            student = student_map.get(rec["student_id"], {})
            scores  = [rec["marks"].get(s, 0) for s in db.SUBJECTS]
            avg     = round(sum(scores) / len(scores), 1)
            row     = ([student.get("name", "?"),
                        student.get("sap_id", "?"),
                        rec["exam"]]
                       + [str(int(v)) for v in scores]
                       + [str(avg), db.get_grade(avg)])
            records_table.insert("", "end", values=row)

    refresh_students()
    load_records_table()
    parent.refresh = lambda: (refresh_students(), load_records_table())


# ════════════════════════════════════════════════════════════
#  TAB 3 — DASHBOARD (CHARTS)
# ════════════════════════════════════════════════════════════

def build_dashboard_tab(parent):
    frame = tk.Frame(parent, bg=BG)
    frame.pack(fill="both", expand=True)

    controls = tk.Frame(frame, bg=PANEL, padx=16, pady=10)
    controls.pack(fill="x")

    tk.Label(controls, text="Student:", bg=PANEL, fg=FG, font=("Arial", 10)).pack(side="left")
    student_var = tk.StringVar()
    student_cb  = ttk.Combobox(controls, textvariable=student_var,
                                state="readonly", font=("Arial", 10), width=28)
    student_cb.pack(side="left", padx=(6, 20))
    student_cb._data = []

    tk.Label(controls, text="Chart:", bg=PANEL, fg=FG, font=("Arial", 10)).pack(side="left")
    chart_var = tk.StringVar(value="Bar — Subject Marks")
    chart_cb  = ttk.Combobox(controls, textvariable=chart_var, state="readonly",
                              font=("Arial", 10), width=22,
                              values=["Bar — Subject Marks",
                                      "Line — Score Trend",
                                      "Radar — Strengths",
                                      "Pie — Class Pass/Fail"])
    chart_cb.pack(side="left", padx=(6, 20))

    tk.Button(controls, text="📊  Show Chart", bg=ACCENT, fg="#1e1e2e",
              font=("Arial", 10, "bold"), relief="flat", cursor="hand2",
              padx=12, pady=5, command=lambda: show_chart()).pack(side="left")

    alert_lbl = tk.Label(controls, text="", bg=PANEL, fg=YELLOW, font=("Arial", 10, "bold"))
    alert_lbl.pack(side="left", padx=20)

    chart_area     = tk.Frame(frame, bg=BG)
    chart_area.pack(fill="both", expand=True, padx=20, pady=16)
    current_canvas = [None]

    def show_chart():
        alert_lbl.config(text="")
        if current_canvas[0]:
            current_canvas[0].get_tk_widget().destroy()

        chart_type = chart_var.get()

        if "Pass/Fail" in chart_type:
            passed, failed = analytics.get_pass_fail_count()
            fig = charts.pie_chart(passed, failed)
        else:
            idx = student_cb.current()
            if idx < 0:
                alert_lbl.config(text="⚠️  Please select a student first.")
                return
            sid     = str(student_cb._data[idx]["_id"])
            sname   = student_cb._data[idx]["name"]
            summary = analytics.get_student_summary(sid)

            if not summary:
                alert_lbl.config(text="⚠️  No marks found for this student.")
                return

            if summary["alert"]:
                alert_lbl.config(text="⚠️  " + summary["alert"])

            if "Bar" in chart_type:
                fig = charts.bar_chart(summary["marks_by_exam"], sname)
            elif "Line" in chart_type:
                fig = charts.line_chart(summary["trend"], sname)
            elif "Radar" in chart_type:
                class_avg = analytics.get_class_subject_averages()
                fig = charts.radar_chart(summary["subject_averages"], class_avg, sname)

        canvas = FigureCanvasTkAgg(fig, master=chart_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        current_canvas[0] = canvas

    def refresh():
        all_students        = db.get_all_students()
        student_cb._data    = all_students
        student_cb["values"] = [f"{s['name']} ({s.get('sap_id','')})" for s in all_students]

    refresh()
    parent.refresh = refresh


# ════════════════════════════════════════════════════════════
#  TAB 4 — REPORTS
# ════════════════════════════════════════════════════════════

def build_reports_tab(parent):
    frame = tk.Frame(parent, bg=BG, padx=16, pady=16)
    frame.pack(fill="both", expand=True)

    hdr = tk.Frame(frame, bg=BG)
    hdr.pack(fill="x", pady=(0, 12))
    tk.Label(hdr, text="📋  Class Reports & Leaderboard", bg=BG,
             fg=ACCENT, font=("Arial", 14, "bold")).pack(side="left")

    tk.Button(hdr, text="🔄  Refresh", bg=ENTRY_BG, fg=FG,
              font=("Arial", 10), relief="flat", cursor="hand2",
              padx=10, pady=5, command=lambda: refresh()).pack(side="right", padx=4)

    tk.Button(hdr, text="📥  Export CSV", bg=GREEN, fg="#1e1e2e",
              font=("Arial", 10, "bold"), relief="flat", cursor="hand2",
              padx=10, pady=5, command=lambda: export_csv()).pack(side="right", padx=4)

    tk.Label(frame, text="🏆  Leaderboard", bg=BG, fg=FG,
             font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 4))

    # Updated leaderboard columns
    _style_table("Report")
    lb_cols = ["Rank", "Name", "SAP ID", "Batch No", "Course", "Avg Score", "Grade"]
    lb_table = ttk.Treeview(frame, columns=lb_cols, show="headings",
                             style="Report.Treeview", height=9)
    for col, w in [("Rank",45),("Name",150),("SAP ID",90),
                   ("Batch No",80),("Course",110),("Avg Score",85),("Grade",65)]:
        lb_table.heading(col, text=col)
        lb_table.column(col, width=w, anchor="center")
    lb_table.pack(fill="x", pady=(0, 16))

    tk.Label(frame, text="⚠️  At-Risk Students  (score dropped > 20 pts)",
             bg=BG, fg=YELLOW, font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 4))

    risk_table = ttk.Treeview(frame, columns=["Student", "Alert"],
                               show="headings", style="Report.Treeview", height=4)
    risk_table.heading("Student", text="Student")
    risk_table.column("Student", width=160, anchor="center")
    risk_table.heading("Alert", text="Alert")
    risk_table.column("Alert", width=500, anchor="w")
    risk_table.pack(fill="x", pady=(0, 12))

    stats_var = tk.StringVar()
    tk.Label(frame, textvariable=stats_var, bg=BG, fg=FG, font=("Arial", 10)).pack(anchor="w")

    def refresh():
        lb_table.delete(*lb_table.get_children())
        df = analytics.get_class_leaderboard()
        for rank, row in df.iterrows():
            tag = "fail" if row["Avg Score"] < 50 else "pass"
            lb_table.insert("", "end", tags=(tag,),
                            values=(rank,
                                    row["Name"],
                                    row["SAP ID"],
                                    row["Batch No"],
                                    row["Course"],
                                    f"{row['Avg Score']:.1f}",
                                    row["Grade"]))
        lb_table.tag_configure("fail", foreground=RED)

        risk_table.delete(*risk_table.get_children())
        for name, alert in analytics.get_at_risk_students():
            risk_table.insert("", "end", values=(name, alert))

        total   = len(df)
        passing = len(df[df["Avg Score"] >= 50]) if total > 0 else 0
        top     = df.iloc[0]["Name"] if total > 0 else "—"
        stats_var.set(
            f"Total: {total}   |   Passing: {passing}   |   "
            f"Failing: {total - passing}   |   Top Student: {top}"
        )

    def export_csv():
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="student_report.csv"
        )
        if path:
            analytics.export_csv(path)
            messagebox.showinfo("Exported ✅", f"Report saved to:\n{path}")

    refresh()
    parent.refresh = refresh


# ════════════════════════════════════════════════════════════
#  HELPER: Style Treeview tables
# ════════════════════════════════════════════════════════════

def _style_table(name):
    style = ttk.Style()
    style.configure(f"{name}.Treeview",
                    background=PANEL, foreground=FG, fieldbackground=PANEL,
                    rowheight=30, font=("Arial", 10))
    style.configure(f"{name}.Treeview.Heading",
                    background=ENTRY_BG, foreground=ACCENT, font=("Arial", 10, "bold"))
    style.map(f"{name}.Treeview",
              background=[("selected", ACCENT)], foreground=[("selected", "#1e1e2e")])


# ════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ════════════════════════════════════════════════════════════

def main():
    try:
        import pymongo
        pymongo.MongoClient("mongodb://localhost:27017/",
                            serverSelectionTimeoutMS=2000).server_info()
        mongo_status = ("🟢 MongoDB Connected", "#a6e3a1")
    except Exception:
        mongo_status = ("🔴 MongoDB Offline", "#f38ba8")
        messagebox.showwarning(
            "MongoDB Not Found",
            "Could not connect to MongoDB.\n\n"
            "Install MongoDB and start it, then relaunch.\n\n"
            "Windows: it starts automatically after install.\n"
            "Mac:     brew services start mongodb-community\n"
            "Linux:   sudo systemctl start mongod"
        )

    root = tk.Tk()
    root.title("Student Performance Tracker")
    root.geometry("1150x700")
    root.minsize(950, 580)
    root.configure(bg=BG)

    header = tk.Frame(root, bg=PANEL, pady=10, padx=20)
    header.pack(fill="x")
    tk.Label(header, text="📚  Student Performance Tracker",
             bg=PANEL, fg=ACCENT, font=("Arial", 16, "bold")).pack(side="left")
    tk.Label(header, text="BTech CS-II | Python Project",
             bg=PANEL, fg="#6c7086", font=("Arial", 9)).pack(side="right")
    tk.Label(header, text=mongo_status[0], bg=PANEL,
             fg=mongo_status[1], font=("Arial", 9)).pack(side="right", padx=20)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TNotebook", background=BG, borderwidth=0)
    style.configure("TNotebook.Tab", background=PANEL, foreground="#6c7086",
                    font=("Arial", 11), padding=[16, 8])
    style.map("TNotebook.Tab",
              background=[("selected", BG)], foreground=[("selected", ACCENT)])

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True)

    t1 = tk.Frame(nb, bg=BG)
    t2 = tk.Frame(nb, bg=BG)
    t3 = tk.Frame(nb, bg=BG)
    t4 = tk.Frame(nb, bg=BG)

    nb.add(t1, text="👥  Students")
    nb.add(t2, text="📝  Marks Entry")
    nb.add(t3, text="📊  Dashboard")
    nb.add(t4, text="📋  Reports")

    build_students_tab(t1)
    build_marks_tab(t2)
    build_dashboard_tab(t3)
    build_reports_tab(t4)

    def on_tab_switch(event):
        tab = nb.index(nb.select())
        if tab == 1 and hasattr(t2, "refresh"):
            t2.refresh()
        elif tab == 2 and hasattr(t3, "refresh"):
            t3.refresh()
        elif tab == 3 and hasattr(t4, "refresh"):
            t4.refresh()

    nb.bind("<<NotebookTabChanged>>", on_tab_switch)
    root.mainloop()


if __name__ == "__main__":
    main()
