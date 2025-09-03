import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
from fpdf import FPDF
import math

# ---------- Appearance ----------
ctk.set_appearance_mode("dark")   # "dark" or "light"
ctk.set_default_color_theme("dark-blue")  # built-in themes: 'blue', 'green', 'dark-blue'

# ---------- Helper functions ----------
def calculate_grade(average):
    """Return a letter grade and GPA-like value from average (0-100)."""
    if average >= 90:
        return "A+", 4.0
    if average >= 80:
        return "A", 3.7
    if average >= 70:
        return "B+", 3.3
    if average >= 60:
        return "B", 3.0
    if average >= 50:
        return "C", 2.0
    return "F", 0.0

def safe_float(s):
    try:
        return float(s)
    except:
        return None

# ---------- Main App ----------
class StudentDashboardApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Student Performance Dashboard")
        self.geometry("1200x720")
        self.minsize(1000, 650)

        # Main layout: left form, right dashboard area
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left panel: user input
        self.left_panel = ctk.CTkFrame(self, width=340, corner_radius=12)
        self.left_panel.grid(row=0, column=0, padx=16, pady=16, sticky="ns")
        self.left_panel.grid_rowconfigure(10, weight=1)

        title = ctk.CTkLabel(self.left_panel, text="Student Details", font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, padx=12, pady=(12,8), sticky="w")

        # Student Info entries
        self.entry_name = ctk.CTkEntry(self.left_panel, placeholder_text="Full Name")
        self.entry_roll = ctk.CTkEntry(self.left_panel, placeholder_text="Roll Number")
        self.entry_class = ctk.CTkEntry(self.left_panel, placeholder_text="Class/Section")
        self.entry_attendance = ctk.CTkEntry(self.left_panel, placeholder_text="Attendance % (e.g. 92)")

        self.entry_name.grid(row=1, column=0, padx=12, pady=6, sticky="ew")
        self.entry_roll.grid(row=2, column=0, padx=12, pady=6, sticky="ew")
        self.entry_class.grid(row=3, column=0, padx=12, pady=6, sticky="ew")
        self.entry_attendance.grid(row=4, column=0, padx=12, pady=6, sticky="ew")

        # Subjects - default 6 subjects
        subjects_title = ctk.CTkLabel(self.left_panel, text="Enter marks (0-100)", font=ctk.CTkFont(size=14))
        subjects_title.grid(row=5, column=0, padx=12, pady=(12,6), sticky="w")

        self.subject_vars = []
        self.subject_names = ["Maths", "Physics", "Chemistry", "English", "Computer", "History"]
        for i, subj in enumerate(self.subject_names):
            frame = ctk.CTkFrame(self.left_panel, corner_radius=8)
            frame.grid(row=6+i, column=0, padx=12, pady=6, sticky="ew")
            frame.grid_columnconfigure(1, weight=1)
            lbl = ctk.CTkLabel(frame, text=subj)
            ent = ctk.CTkEntry(frame, placeholder_text="Marks")
            lbl.grid(row=0, column=0, padx=(10,6), pady=6, sticky="w")
            ent.grid(row=0, column=1, padx=(0,10), pady=6, sticky="ew")
            self.subject_vars.append(ent)

        # Buttons: Generate, Export PDF, Clear
        btn_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        btn_frame.grid(row=12+len(self.subject_names), column=0, padx=12, pady=(14,12), sticky="ew")
        btn_frame.grid_columnconfigure((0,1,2), weight=1)

        self.generate_btn = ctk.CTkButton(btn_frame, text="Generate Dashboard", command=self.generate_dashboard, corner_radius=10)
        self.export_btn = ctk.CTkButton(btn_frame, text="Export PDF", command=self.export_pdf, corner_radius=10, state="disabled")
        self.clear_btn = ctk.CTkButton(btn_frame, text="Clear", command=self.clear_form, corner_radius=10)

        self.generate_btn.grid(row=0, column=0, padx=6, pady=4, sticky="ew")
        self.export_btn.grid(row=0, column=1, padx=6, pady=4, sticky="ew")
        self.clear_btn.grid(row=0, column=2, padx=6, pady=4, sticky="ew")

        # Right panel: dashboard
        self.right_panel = ctk.CTkFrame(self, corner_radius=12)
        self.right_panel.grid(row=0, column=1, padx=(0,16), pady=16, sticky="nsew")
        self.right_panel.grid_rowconfigure(2, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        # Top bar
        top_bar = ctk.CTkFrame(self.right_panel, corner_radius=8, height=70)
        top_bar.grid(row=0, column=0, padx=16, pady=(16,8), sticky="ew")
        top_bar.grid_columnconfigure(0, weight=1)
        self.header_label = ctk.CTkLabel(top_bar, text="Student Performance Dashboard", font=ctk.CTkFont(size=20, weight="bold"))
        self.header_label.grid(row=0, column=0, padx=12, pady=12, sticky="w")

        # Cards: total, average, grade, attendance
        cards_frame = ctk.CTkFrame(self.right_panel, corner_radius=8)
        cards_frame.grid(row=1, column=0, padx=16, pady=8, sticky="ew")
        cards_frame.grid_columnconfigure((0,1,2,3), weight=1)

        # Card widgets (CTkLabel used for styled numeric display)
        self.card_total = ctk.CTkFrame(cards_frame, corner_radius=12)
        self.card_avg = ctk.CTkFrame(cards_frame, corner_radius=12)
        self.card_grade = ctk.CTkFrame(cards_frame, corner_radius=12)
        self.card_attendance = ctk.CTkFrame(cards_frame, corner_radius=12)

        self.card_total.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self.card_avg.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        self.card_grade.grid(row=0, column=2, padx=8, pady=8, sticky="nsew")
        self.card_attendance.grid(row=0, column=3, padx=8, pady=8, sticky="nsew")

        # Card contents
        self.lbl_total_title = ctk.CTkLabel(self.card_total, text="Total Marks", anchor="w")
        self.lbl_total_value = ctk.CTkLabel(self.card_total, text="--", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_avg_title = ctk.CTkLabel(self.card_avg, text="Average (%)", anchor="w")
        self.lbl_avg_value = ctk.CTkLabel(self.card_avg, text="--", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_grade_title = ctk.CTkLabel(self.card_grade, text="Grade (GPA)", anchor="w")
        self.lbl_grade_value = ctk.CTkLabel(self.card_grade, text="--", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_att_title = ctk.CTkLabel(self.card_attendance, text="Attendance %", anchor="w")
        self.lbl_att_value = ctk.CTkLabel(self.card_attendance, text="--", font=ctk.CTkFont(size=18, weight="bold"))

        self.lbl_total_title.pack(anchor="w", padx=12, pady=(12,0))
        self.lbl_total_value.pack(anchor="w", padx=12, pady=(6,12))
        self.lbl_avg_title.pack(anchor="w", padx=12, pady=(12,0))
        self.lbl_avg_value.pack(anchor="w", padx=12, pady=(6,12))
        self.lbl_grade_title.pack(anchor="w", padx=12, pady=(12,0))
        self.lbl_grade_value.pack(anchor="w", padx=12, pady=(6,12))
        self.lbl_att_title.pack(anchor="w", padx=12, pady=(12,0))
        self.lbl_att_value.pack(anchor="w", padx=12, pady=(6,12))

        # Middle area: charts + leaderboard
        mid_frame = ctk.CTkFrame(self.right_panel, corner_radius=8)
        mid_frame.grid(row=2, column=0, padx=16, pady=12, sticky="nsew")
        mid_frame.grid_columnconfigure(0, weight=2)
        mid_frame.grid_columnconfigure(1, weight=1)
        mid_frame.grid_rowconfigure(0, weight=1)

        # Chart area (left)
        charts_frame = ctk.CTkFrame(mid_frame, corner_radius=12)
        charts_frame.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
        charts_frame.grid_rowconfigure((0,1), weight=1)
        charts_frame.grid_columnconfigure(0, weight=1)

        # Create Matplotlib Figure
        self.fig = Figure(figsize=(6,4), dpi=100)
        self.ax_trend = self.fig.add_subplot(211)
        self.ax_bar = self.fig.add_subplot(212)
        self.fig.tight_layout(pad=3.0)

        self.canvas = FigureCanvasTkAgg(self.fig, master=charts_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True, padx=8, pady=8)

        # Leaderboard & comparison (right)
        right_small_frame = ctk.CTkFrame(mid_frame, corner_radius=12)
        right_small_frame.grid(row=0, column=1, padx=12, pady=12, sticky="nsew")
        right_small_frame.grid_rowconfigure((0,1,2), weight=1)

        lb_title = ctk.CTkLabel(right_small_frame, text="Class Leaderboard", font=ctk.CTkFont(size=16, weight="bold"))
        lb_title.grid(row=0, column=0, padx=12, pady=(12,6), sticky="w")

        self.leaderboard_listbox = tk.Listbox(right_small_frame, bg="#1b1b1b", fg="white", bd=0, highlightthickness=0, selectbackground="#2a2a2a", font=("Arial", 11))
        self.leaderboard_listbox.grid(row=1, column=0, padx=12, pady=6, sticky="nsew")

        compare_frame = ctk.CTkFrame(right_small_frame, corner_radius=8)
        compare_frame.grid(row=2, column=0, padx=12, pady=12, sticky="ew")
        compare_frame.grid_columnconfigure(1, weight=1)
        self.compare_label = ctk.CTkLabel(compare_frame, text="Class Avg : --", anchor="w")
        self.compare_label.grid(row=0, column=0, padx=12, pady=10, sticky="w")

        # Internal state
        self.last_report = None

    # ---------- Actions ----------
    def clear_form(self):
        self.entry_name.delete(0, tk.END)
        self.entry_roll.delete(0, tk.END)
        self.entry_class.delete(0, tk.END)
        self.entry_attendance.delete(0, tk.END)
        for e in self.subject_vars:
            e.delete(0, tk.END)
        self.reset_dashboard()

    def reset_dashboard(self):
        self.lbl_total_value.configure(text="--")
        self.lbl_avg_value.configure(text="--")
        self.lbl_grade_value.configure(text="--")
        self.lbl_att_value.configure(text="--")
        self.compare_label.configure(text="Class Avg : --")
        self.leaderboard_listbox.delete(0, tk.END)
        self.ax_trend.clear()
        self.ax_bar.clear()
        self.canvas.draw()
        self.export_btn.configure(state="disabled")
        self.last_report = None

    def generate_dashboard(self):
        # Validate inputs
        name = self.entry_name.get().strip()
        roll = self.entry_roll.get().strip()
        cls = self.entry_class.get().strip()
        att = safe_float(self.entry_attendance.get().strip())
        marks = []
        for ent in self.subject_vars:
            m = safe_float(ent.get().strip())
            if m is None or m < 0 or m > 100:
                messagebox.showerror("Invalid Input", "Please enter valid marks (0-100) for all subjects.")
                return
            marks.append(m)

        if name == "" or roll == "" or cls == "":
            messagebox.showerror("Missing Info", "Please fill in Name, Roll and Class.")
            return

        # Compute stats
        total = sum(marks)
        n = len(marks)
        average = total / n
        grade, gpa = calculate_grade(average)

        # Update cards
        self.lbl_total_value.configure(text=f"{int(total)} / {n*100}")
        self.lbl_avg_value.configure(text=f"{average:.2f}%")
        self.lbl_grade_value.configure(text=f"{grade}  ({gpa:.2f})")
        if att is None:
            att_text = "N/A"
        else:
            att_text = f"{att:.1f}%"
        self.lbl_att_value.configure(text=att_text)

        # Charts: trend (line) and bar
        subjects = self.subject_names
        x = range(1, n+1)
        self.ax_trend.clear()
        self.ax_trend.plot(x, marks, marker='o', linewidth=2)
        self.ax_trend.set_title("Performance Trend")
        self.ax_trend.set_xticks(x)
        self.ax_trend.set_xticklabels(subjects, rotation=20)
        self.ax_trend.set_ylim(0, 100)
        self.ax_trend.grid(axis='y', linestyle='--', alpha=0.4)

        self.ax_bar.clear()
        bars = self.ax_bar.bar(subjects, marks)
        # color accents: highlight above-average as brighter
        for bar, val in zip(bars, marks):
            if val >= average:
                bar.set_alpha(0.95)
            else:
                bar.set_alpha(0.6)
        self.ax_bar.set_title("Marks by Subject")
        self.ax_bar.set_ylim(0, 100)

        self.canvas.draw()

        # Populate a sample leaderboard (simulate class data)
        class_data = self._build_sample_leaderboard(name, total)
        self.leaderboard_listbox.delete(0, tk.END)
        for i, row in class_data.iterrows():
            rank_str = f"{int(i)+1}. {row['name']} — {row['total']} ({row['avg']:.1f}%)"
            self.leaderboard_listbox.insert(tk.END, rank_str)

        class_avg = class_data['avg'].mean()
        self.compare_label.configure(text=f"Class Avg : {class_avg:.2f}%")

        # Save a last_report dictionary used for export
        self.last_report = {
            "name": name, "roll": roll, "class": cls,
            "attendance": att_text, "subjects": subjects, "marks": marks,
            "total": total, "average": average, "grade": grade, "gpa": gpa,
            "class_avg": class_avg
        }
        self.export_btn.configure(state="normal")

    def _build_sample_leaderboard(self, student_name, student_total):
        """
        Create a sample leaderboard DataFrame.
        Student is injected with their score; others are simulated.
        """
        # Simulate some students
        import random
        others = []
        for i in range(7):
            nm = f"Student_{i+1}"
            # make totals around 250-580 for 6 subjects (0-100 each)
            tot = random.randint(260, 580)
            others.append({"name": nm, "total": tot, "avg": tot / 6.0})
        # Add current student
        others.append({"name": student_name + " (You)", "total": int(student_total), "avg": student_total / 6.0})
        df = pd.DataFrame(others)
        # sort desc by total
        df = df.sort_values(by="total", ascending=False).reset_index(drop=True)
        return df

    def export_pdf(self):
        if not self.last_report:
            messagebox.showwarning("No Report", "Generate the dashboard before exporting.")
            return

        # Ask where to save
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")],
                                                title="Save performance report as")
        if not filepath:
            return

        # Create a simple PDF using fpdf
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=12)
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Student Performance Report", ln=True)
        pdf.ln(4)

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, f"Name: {self.last_report['name']}", ln=True)
        pdf.cell(0, 8, f"Roll: {self.last_report['roll']}", ln=True)
        pdf.cell(0, 8, f"Class: {self.last_report['class']}", ln=True)
        pdf.cell(0, 8, f"Attendance: {self.last_report['attendance']}", ln=True)
        pdf.ln(6)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(60, 8, "Subject", border=1)
        pdf.cell(40, 8, "Marks", border=1, ln=True)
        pdf.set_font("Arial", size=12)
        for subj, m in zip(self.last_report['subjects'], self.last_report['marks']):
            pdf.cell(60, 8, subj, border=1)
            pdf.cell(40, 8, f"{m}", border=1, ln=True)

        pdf.ln(6)
        pdf.cell(0, 8, f"Total: {int(self.last_report['total'])} / {len(self.last_report['subjects']) * 100}", ln=True)
        pdf.cell(0, 8, f"Average: {self.last_report['average']:.2f}%", ln=True)
        pdf.cell(0, 8, f"Grade: {self.last_report['grade']}  (GPA: {self.last_report['gpa']:.2f})", ln=True)
        pdf.cell(0, 8, f"Class Average: {self.last_report['class_avg']:.2f}%", ln=True)

        try:
            pdf.output(filepath)
            messagebox.showinfo("Saved", f"Report exported successfully to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save PDF: {e}")

# ---------- Run ----------
if __name__ == "__main__":
    app = StudentDashboardApp()
    app.mainloop()






#created by Mr.Rajeshwar Shingade
#GitHub : https://github.com/RajeshwarShingade
#LinkedIn : https://www.linkedin.com/in/rajeshwarshingade
#telegram : https://t.me/rajeshwarshingade
#kaggle : https://www.kaggle.com/rajeshwarshingade


#Happy Coding

#© All Rights Reserved