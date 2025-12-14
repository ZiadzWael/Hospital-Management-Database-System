import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
import csv
from tkinter import filedialog
from fpdf import FPDF
from tkinter import simpledialog

# --- Database connection ---
def get_db_connection():
    return mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='Carrot1223',
        database='hospital_management_system1'
    )

# --- Utility function ---
def fetch_all(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def execute_query(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class TreatmentTab(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.entries = {}
        self.create_widgets()
        self.load_treatments()

    def create_widgets(self):
        """Create and arrange all widgets in the tab"""
        self.create_form_section()
        self.create_button_section()
        self.create_search_section()
        self.create_treeview_section()

    def create_form_section(self):
        """Create the form fields for treatment data"""
        form_frame = ttk.LabelFrame(self, text="Treatment Details", padding=(10, 5))
        form_frame.pack(fill='x', padx=10, pady=5)

        fields = [
            ("Patient ID", 0, 0),
            ("Doctor ID", 0, 2),
            ("Diagnosis", 1, 0),
            ("Treatment", 1, 2),
            ("Start Date (YYYY-MM-DD)", 2, 0),
            ("End Date (YYYY-MM-DD)", 2, 2),
            ("Amount", 3, 0)
        ]

        for text, row, col in fields:
            label = ttk.Label(form_frame, text=text)
            label.grid(row=row, column=col, sticky='w', padx=5, pady=2)
            
            entry = ttk.Entry(form_frame)
            entry.grid(row=row, column=col+1, padx=5, pady=2, sticky='ew')
            self.entries[text] = entry

        # Configure grid weights
        for i in range(4):  # 4 rows
            form_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):  # 4 columns (0-3)
            form_frame.grid_columnconfigure(i, weight=1 if i % 2 else 0)

    def create_button_section(self):
        """Create the action buttons"""
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=5)

        buttons = [
            ("Add Treatment", self.add_treatment),
            ("Update Treatment", self.update_treatment),
            ("Delete Treatment", self.delete_treatment),
            ("Clear Fields", self.clear_fields)
        ]

        for text, command in buttons:
            btn = ttk.Button(btn_frame, text=text, command=command)
            btn.pack(side='left', padx=5, expand=True, fill='x')

    def create_search_section(self):
        """Create search and filter controls"""
        search_frame = ttk.LabelFrame(self, text="Search & Filter", padding=(10, 5))
        search_frame.pack(fill='x', padx=10, pady=5)

        # Search entry
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        # Search button
        ttk.Button(search_frame, text="Search", command=self.search_treatments).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Reset", command=self.load_treatments).pack(side='left', padx=5)

        # Filter combobox
        filter_frame = ttk.Frame(search_frame)
        filter_frame.pack(side='left', padx=10)
        
        ttk.Label(filter_frame, text="Filter by:").pack(side='left', padx=5)
        self.filter_field = ttk.Combobox(filter_frame, values=[
            "All", "Treatment ID", "Patient ID", "Doctor ID", 
            "Diagnosis", "Treatment", "Date Range", "Amount"
        ], state="readonly", width=12)
        self.filter_field.set("All")
        self.filter_field.pack(side='left', padx=5)
        self.filter_field.bind("<<ComboboxSelected>>", self.update_filter_fields)

        # Date range fields (hidden by default)
        self.date_range_frame = ttk.Frame(search_frame)
        ttk.Label(self.date_range_frame, text="From:").pack(side='left')
        self.from_date = ttk.Entry(self.date_range_frame, width=10)
        self.from_date.pack(side='left', padx=5)
        ttk.Label(self.date_range_frame, text="To:").pack(side='left')
        self.to_date = ttk.Entry(self.date_range_frame, width=10)
        self.to_date.pack(side='left', padx=5)

    def create_treeview_section(self):
        """Create the treatment records table"""
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Create scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')

        # Create treeview
        columns = [
            ("TreatmentID", "ID", 50),
            ("Patient_ID", "Patient ID", 80),
            ("Patient_Name", "Patient Name", 120),
            ("DoctorID", "Doctor ID", 80),
            ("Doctor_Name", "Doctor Name", 120),
            ("Diagnosis", "Diagnosis", 150),
            ("Treatment", "Treatment", 150),
            ("StartDate", "Start Date", 100),
            ("EndDate", "End Date", 100),
            ("Amount", "Amount", 80)
        ]

        self.tree = ttk.Treeview(
            tree_frame,
            columns=[col[0] for col in columns],
            show='headings',
            yscrollcommand=scrollbar.set
        )

        # Configure columns
        for col_id, col_text, width in columns:
            self.tree.heading(col_id, text=col_text)
            self.tree.column(col_id, width=width, anchor='center')

        self.tree.pack(fill='both', expand=True)
        scrollbar.config(command=self.tree.yview)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def update_filter_fields(self, event=None):
        """Show/hide special filter fields based on selection"""
        self.date_range_frame.pack_forget()
        
        if self.filter_field.get() == "Date Range":
            self.date_range_frame.pack(side='left', padx=10)

    def load_treatments(self):
        """Load all treatments from database"""
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        query = """
        SELECT t.*, p.F_name AS patient_fname, p.L_name AS patient_lname,
               s.F_name AS doctor_fname, s.L_name AS doctor_lname
        FROM Treatments t
        JOIN Patient p ON t.Patient_ID = p.Patient_ID
        JOIN Staff s ON t.DoctorID = s.Staff_ID
        ORDER BY t.StartDate DESC
        """
        
        treatments = fetch_all(query)
        for t in treatments:
            self.tree.insert('', 'end', values=(
                t['TreatmentID'],
                t['Patient_ID'],
                f"{t['patient_fname']} {t['patient_lname']}",
                t['DoctorID'],
                f"{t['doctor_fname']} {t['doctor_lname']}",
                t['Diagnosis'],
                t['Treatment'],
                t['StartDate'].strftime('%Y-%m-%d') if t['StartDate'] else '',
                t['EndDate'].strftime('%Y-%m-%d') if t['EndDate'] else '',
                f"${t['Amount']:.2f}" if t['Amount'] else ''
            ))

    def clear_fields(self):
        """Clear all form fields"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def on_tree_select(self, event):
        """Populate form fields when a treatment is selected"""
        selected = self.tree.selection()
        if not selected:
            return
            
        values = self.tree.item(selected[0])['values']
        if not values:
            return

        # Map treeview columns to form fields
        field_map = [
            ('Patient ID', 1),
            ('Doctor ID', 3),
            ('Diagnosis', 5),
            ('Treatment', 6),
            ('Start Date (YYYY-MM-DD)', 7),
            ('End Date (YYYY-MM-DD)', 8),
            ('Amount', 9)
        ]

        self.clear_fields()
        for field_name, col_index in field_map:
            if col_index < len(values):
                self.entries[field_name].insert(0, values[col_index])

    def validate_fields(self):
        """Validate form fields before submission"""
        required_fields = [
            'Patient ID', 'Doctor ID', 'Diagnosis', 
            'Start Date (YYYY-MM-DD)'
        ]
        
        for field in required_fields:
            if not self.entries[field].get().strip():
                messagebox.showwarning("Validation Error", f"{field} is required")
                return False

        # Validate dates
        try:
            start_date = self.entries['Start Date (YYYY-MM-DD)'].get()
            datetime.strptime(start_date, '%Y-%m-%d')
            
            end_date = self.entries['End Date (YYYY-MM-DD)'].get()
            if end_date:
                datetime.strptime(end_date, '%Y-%m-%d')
                if end_date < start_date:
                    messagebox.showwarning("Validation Error", "End date cannot be before start date")
                    return False
        except ValueError:
            messagebox.showwarning("Validation Error", "Invalid date format (YYYY-MM-DD)")
            return False

        # Validate amount
        amount = self.entries['Amount'].get()
        if amount:
            try:
                float(amount)
            except ValueError:
                messagebox.showwarning("Validation Error", "Amount must be a number")
                return False

        return True

    def add_treatment(self):
        """Add a new treatment record"""
        if not self.validate_fields():
            return

        try:
            vals = {key: (self.entries[key].get().strip() or None) for key in self.entries}
            
            query = """
                INSERT INTO Treatments 
                (Patient_ID, DoctorID, Diagnosis, Treatment, StartDate, EndDate, Amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                vals['Patient ID'],
                vals['Doctor ID'],
                vals['Diagnosis'],
                vals['Treatment'],
                vals['Start Date (YYYY-MM-DD)'],
                vals['End Date (YYYY-MM-DD)'] or None,
                vals['Amount'] or None
            )
            
            execute_query(query, params)
            messagebox.showinfo("Success", "Treatment added successfully")
            self.load_treatments()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add treatment:\n{str(e)}")

    def update_treatment(self):
        """Update selected treatment record"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a treatment to update")
            return
            
        if not self.validate_fields():
            return

        treatment_id = self.tree.item(selected[0])['values'][0]
        
        try:
            vals = {key: (self.entries[key].get().strip() or None) for key in self.entries}
            
            query = """
                UPDATE Treatments SET 
                    Patient_ID = %s,
                    DoctorID = %s,
                    Diagnosis = %s,
                    Treatment = %s,
                    StartDate = %s,
                    EndDate = %s,
                    Amount = %s
                WHERE TreatmentID = %s
            """
            params = (
                vals['Patient ID'],
                vals['Doctor ID'],
                vals['Diagnosis'],
                vals['Treatment'],
                vals['Start Date (YYYY-MM-DD)'],
                vals['End Date (YYYY-MM-DD)'] or None,
                vals['Amount'] or None,
                treatment_id
            )
            
            execute_query(query, params)
            messagebox.showinfo("Success", "Treatment updated successfully")
            self.load_treatments()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update treatment:\n{str(e)}")

    def delete_treatment(self):
        """Delete selected treatment record"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a treatment to delete")
            return
            
        treatment_id = self.tree.item(selected[0])['values'][0]
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this treatment?"):
            return
            
        try:
            execute_query("DELETE FROM Treatments WHERE TreatmentID = %s", (treatment_id,))
            messagebox.showinfo("Success", "Treatment deleted successfully")
            self.load_treatments()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete treatment:\n{str(e)}")

    def search_treatments(self):
        """Search treatments based on criteria"""
        search_term = self.search_entry.get().strip()
        filter_by = self.filter_field.get()
        
        base_query = """
        SELECT t.*, p.F_name AS patient_fname, p.L_name AS patient_lname,
               s.F_name AS doctor_fname, s.L_name AS doctor_lname
        FROM Treatments t
        JOIN Patient p ON t.Patient_ID = p.Patient_ID
        JOIN Staff s ON t.DoctorID = s.Staff_ID
        """
        
        conditions = []
        params = []
        
        if filter_by == "All" and search_term:
            conditions.append("""
                (t.TreatmentID LIKE %s OR 
                 t.Patient_ID LIKE %s OR 
                 t.DoctorID LIKE %s OR 
                 t.Diagnosis LIKE %s OR 
                 t.Treatment LIKE %s OR 
                 CONCAT(p.F_name, ' ', p.L_name) LIKE %s OR
                 CONCAT(s.F_name, ' ', s.L_name) LIKE %s)
            """)
            params = [f"%{search_term}%"] * 7
            
        elif filter_by != "All":
            if filter_by == "Date Range":
                try:
                    from_date = self.from_date.get().strip()
                    to_date = self.to_date.get().strip()
                    if from_date and to_date:
                        datetime.strptime(from_date, '%Y-%m-%d')
                        datetime.strptime(to_date, '%Y-%m-%d')
                        conditions.append("(t.StartDate BETWEEN %s AND %s OR t.EndDate BETWEEN %s AND %s)")
                        params.extend([from_date, to_date, from_date, to_date])
                except ValueError:
                    messagebox.showwarning("Invalid Date", "Please use YYYY-MM-DD format for dates")
                    return
                    
            elif filter_by == "Amount":
                if search_term:
                    try:
                        amount = float(search_term)
                        conditions.append("t.Amount = %s")
                        params.append(amount)
                    except ValueError:
                        messagebox.showwarning("Invalid Amount", "Amount must be a number")
                        return
            else:
                field_map = {
                    "Treatment ID": "t.TreatmentID",
                    "Patient ID": "t.Patient_ID",
                    "Doctor ID": "t.DoctorID",
                    "Diagnosis": "t.Diagnosis",
                    "Treatment": "t.Treatment"
                }
                if search_term:
                    conditions.append(f"{field_map[filter_by]} LIKE %s")
                    params.append(f"%{search_term}%")
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += " ORDER BY t.StartDate DESC"
        
        # Clear current treeview
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        # Load filtered results
        treatments = fetch_all(base_query, params)
        for t in treatments:
            self.tree.insert('', 'end', values=(
                t['TreatmentID'],
                t['Patient_ID'],
                f"{t['patient_fname']} {t['patient_lname']}",
                t['DoctorID'],
                f"{t['doctor_fname']} {t['doctor_lname']}",
                t['Diagnosis'],
                t['Treatment'],
                t['StartDate'].strftime('%Y-%m-%d') if t['StartDate'] else '',
                t['EndDate'].strftime('%Y-%m-%d') if t['EndDate'] else '',
                f"${t['Amount']:.2f}" if t['Amount'] else ''
            ))
            
# --- Query Tab ---
class QueryTab(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.create_widgets()
        self.query_results = None
        
    def create_widgets(self):
        # Query Input Area
        query_frame = ttk.LabelFrame(self, text="SQL Query")
        query_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.query_text = tk.Text(query_frame, height=10, wrap=tk.WORD)
        self.query_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Buttons Frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Execute Query", command=self.execute_query).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_query).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Save as View", command=self.save_as_view).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Export to CSV", command=self.export_to_csv).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Export to PDF", command=self.export_to_pdf).pack(side='left', padx=5)
        
        # Results Area
        results_frame = ttk.LabelFrame(self, text="Results")
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview for tabular results
        self.tree = ttk.Treeview(results_frame)
        self.tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Text widget for non-tabular results
        self.results_text = tk.Text(results_frame, height=5, state='disabled')
        self.results_text.pack(fill='x', padx=5, pady=5)
    
    def execute_query(self):
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a SQL query to execute")
            return
            
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Split multiple queries if they exist
            queries = [q.strip() for q in query.split(';') if q.strip()]
            
            for q in queries:
                cursor.execute(q)
            
            # Try to fetch results (works for SELECT queries)
            try:
                results = cursor.fetchall()
                self.query_results = results  # Store results for export
                self.display_tabular_results(results)
            except:
                # For non-SELECT queries (CREATE, UPDATE, etc.)
                conn.commit()
                self.query_results = None
                self.display_text_result(f"Query executed successfully. Rows affected: {cursor.rowcount}")
            
        except Exception as e:
            self.query_results = None
            self.display_text_result(f"Error executing query:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def display_tabular_results(self, results):
        self.clear_results()
        
        if not results:
            self.display_text_result("Query executed successfully but returned no results")
            return
            
        # Configure treeview columns
        self.tree["columns"] = list(results[0].keys())
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='w')
        
        # Add data to treeview
        for row in results:
            self.tree.insert('', 'end', values=list(row.values()))
    
    def display_text_result(self, message):
        self.clear_results()
        self.results_text.config(state='normal')
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert('1.0', message)
        self.results_text.config(state='disabled')
    
    def clear_results(self):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = []
        self.results_text.config(state='normal')
        self.results_text.delete('1.0', tk.END)
        self.results_text.config(state='disabled')
    
    def clear_query(self):
        self.query_text.delete('1.0', tk.END)
        self.clear_results()
        self.query_results = None
    
    def save_as_view(self):
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a SQL query to save as view")
            return
            
        view_name = simpledialog.askstring("Save as View", "Enter view name:")
        if not view_name:
            return
            
        try:
            execute_query(f"CREATE OR REPLACE VIEW {view_name} AS {query}")
            messagebox.showinfo("Success", f"View '{view_name}' created successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create view:\n{str(e)}")
    
    def export_to_csv(self):
        if not self.query_results:
            messagebox.showwarning("No Results", "No query results to export. Please execute a SELECT query first.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Query Results As CSV"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write headers
                headers = self.tree["columns"]
                writer.writerow(headers)
                
                # Write data
                for item in self.tree.get_children():
                    row = self.tree.item(item)['values']
                    writer.writerow(row)
                    
            messagebox.showinfo("Success", f"Query results exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results:\n{str(e)}")
    
    def export_to_pdf(self):
        if not self.query_results:
            messagebox.showwarning("No Results", "No query results to export. Please execute a SELECT query first.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save Query Results As PDF"
        )
        
        if not file_path:
            return
            
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            
            # Get column widths based on content
            col_widths = self.calculate_column_widths()
            
            # Add title with query
            query = self.query_text.get("1.0", tk.END).strip()
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Query Results Report", 0, 1, 'C')
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 5, f"Query: {query[:100]}..." if len(query) > 100 else f"Query: {query}")
            pdf.ln(5)
            
            # Add headers
            pdf.set_font("Arial", 'B', 10)
            headers = self.tree["columns"]
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
            pdf.ln()
            
            # Add data
            pdf.set_font("Arial", '', 10)
            for item in self.tree.get_children():
                row = self.tree.item(item)['values']
                for i, value in enumerate(row):
                    pdf.cell(col_widths[i], 10, str(value), 1, 0, 'L')
                pdf.ln()
            
            pdf.output(file_path)
            messagebox.showinfo("Success", f"Query results exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results:\n{str(e)}")
    
    def calculate_column_widths(self):
        # Calculate column widths based on content
        headers = self.tree["columns"]
        col_widths = [pdf.get_string_width(header) + 6 for header in headers]
        
        # Check data widths
        for item in self.tree.get_children():
            row = self.tree.item(item)['values']
            for i, value in enumerate(row):
                width = pdf.get_string_width(str(value)) + 6
                if width > col_widths[i]:
                    col_widths[i] = width
        
        # Normalize widths to fit page (assuming A4 width = 210mm)
        total_width = sum(col_widths)
        max_width = 190  # Leave some margin
        
        if total_width > max_width:
            scale_factor = max_width / total_width
            col_widths = [int(w * scale_factor) for w in col_widths]
        
        return col_widths

class ReportsTab(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.create_widgets()
        
    def create_widgets(self):
        # Report Type Selection
        report_frame = ttk.LabelFrame(self, text="Report Type")
        report_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(report_frame, text="Select Report:").pack(side='left', padx=5)
        self.report_type = ttk.Combobox(report_frame, values=[
            "Patients Report", 
            "Staff Report", 
            "Appointments Report",
            "Rooms Report",
            "Room Bookings Report",
            "Treatments Report"
        ], state="readonly")
        self.report_type.pack(side='left', padx=5, fill='x', expand=True)
        self.report_type.bind("<<ComboboxSelected>>", self.update_filter_fields)
        
        # Date Range Filter
        self.date_frame = ttk.Frame(self)
        ttk.Label(self.date_frame, text="From:").pack(side='left', padx=5)
        self.from_date = ttk.Entry(self.date_frame, width=12)
        self.from_date.pack(side='left', padx=5)
        ttk.Label(self.date_frame, text="To:").pack(side='left', padx=5)
        self.to_date = ttk.Entry(self.date_frame, width=12)
        self.to_date.pack(side='left', padx=5)
        
        # Status Filter
        self.status_frame = ttk.Frame(self)
        ttk.Label(self.status_frame, text="Status:").pack(side='left', padx=5)
        self.status_filter = ttk.Combobox(self.status_frame, state="readonly")
        self.status_filter.pack(side='left', padx=5)
        
        # Type Filter
        self.type_frame = ttk.Frame(self)
        ttk.Label(self.type_frame, text="Type:").pack(side='left', padx=5)
        self.type_filter = ttk.Combobox(self.type_frame, state="readonly")
        self.type_filter.pack(side='left', padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Generate Report", command=self.generate_report).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Export to CSV", command=self.export_to_csv).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Export to PDF", command=self.export_to_pdf).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear Filters", command=self.clear_filters).pack(side='left', padx=5)
        
        # Results Treeview
        self.tree = ttk.Treeview(self)
        self.tree.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)
    
    def update_filter_fields(self, event=None):
        self.date_frame.pack_forget()
        self.status_frame.pack_forget()
        self.type_frame.pack_forget()
        
        report_type = self.report_type.get()
        
        if report_type in ["Appointments Report", "Treatments Report", "Room Bookings Report"]:
            self.date_frame.pack(fill='x', padx=10, pady=5)
            
        if report_type == "Appointments Report":
            self.status_frame.pack(fill='x', padx=10, pady=5)
            self.status_filter['values'] = ['All', 'Scheduled', 'Completed', 'Cancelled']
            self.status_filter.set('All')
            
        if report_type in ["Patients Report", "Staff Report"]:
            self.type_frame.pack(fill='x', padx=10, pady=5)
            if report_type == "Patients Report":
                self.type_filter['values'] = ['All', 'InPatient', 'OutPatient', 'EmergencyPatient']
            else:
                self.type_filter['values'] = ['All', 'Doctor', 'Nurse', 'Technician']
            self.type_filter.set('All')
            
        if report_type == "Rooms Report":
            self.status_frame.pack(fill='x', padx=10, pady=5)
            self.status_filter['values'] = ['All', 'Available', 'Occupied', 'Maintenance']
            self.status_filter.set('All')
            self.type_frame.pack(fill='x', padx=10, pady=5)
            self.type_filter['values'] = ['All', 'Regular', 'ICU', 'Operation']
            self.type_filter.set('All')
    
    def clear_filters(self):
        self.from_date.delete(0, tk.END)
        self.to_date.delete(0, tk.END)
        if hasattr(self, 'status_filter'):
            self.status_filter.set('All')
        if hasattr(self, 'type_filter'):
            self.type_filter.set('All')
    
    def generate_report(self):
        report_type = self.report_type.get()
        
        if not report_type:
            messagebox.showwarning("Select Report", "Please select a report type first")
            return
            
        # Clear previous results
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = []
        
        # Generate the appropriate report
        if report_type == "Patients Report":
            self.generate_patients_report()
        elif report_type == "Staff Report":
            self.generate_staff_report()
        elif report_type == "Appointments Report":
            self.generate_appointments_report()
        elif report_type == "Rooms Report":
            self.generate_rooms_report()
        elif report_type == "Room Bookings Report":
            self.generate_room_bookings_report()
        elif report_type == "Treatments Report":
            self.generate_treatments_report()
    
    def generate_patients_report(self):
        query = "SELECT * FROM Patient"
        conditions = []
        params = []
        
        patient_type = self.type_filter.get()
        if patient_type != 'All':
            conditions.append("PatientType=%s")
            params.append(patient_type)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY Patient_ID"
        patients = fetch_all(query, params)
        
        self.tree["columns"] = ("ID", "First Name", "Middle Name", "Last Name", "Phone", "Gender", 
                              "Type", "DOB", "Blood Type", "City", "State", "Gov")
        
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor='center')
        
        for patient in patients:
            self.tree.insert('', 'end', values=(
                patient['Patient_ID'],
                patient['F_name'],
                patient['M_name'],
                patient['L_name'],
                patient['Phone_no'],
                patient['Gender'],
                patient['PatientType'],
                str(patient['DOB']),
                patient['Blood_type'],
                patient['City'],
                patient['State'],
                patient['Gov']
            ))
    
    def generate_staff_report(self):
        query = "SELECT * FROM Staff"
        conditions = []
        params = []
        
        staff_type = self.type_filter.get()
        if staff_type != 'All':
            conditions.append("StaffType=%s")
            params.append(staff_type)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY Staff_ID"
        staff = fetch_all(query, params)
        
        self.tree["columns"] = ("ID", "First Name", "Middle Name", "Last Name", "Type", "Phone", "Department")
        
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
        
        for member in staff:
            self.tree.insert('', 'end', values=(
                member['Staff_ID'],
                member['F_name'],
                member['M_name'],
                member['L_name'],
                member['StaffType'],
                member['Phone_no'],
                member['Department']
            ))
    
    def generate_appointments_report(self):
        query = "SELECT * FROM Appointments"
        conditions = []
        params = []
        
        status = self.status_filter.get()
        if status != 'All':
            conditions.append("Status=%s")
            params.append(status)
            
        if self.from_date.get() and self.to_date.get():
            conditions.append("AppointmentDate BETWEEN %s AND %s")
            params.extend([self.from_date.get(), self.to_date.get()])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY AppointmentDate DESC"
        appointments = fetch_all(query, params)
        
        self.tree["columns"] = ("ID", "Patient ID", "Staff ID", "Date", "Status", "Fee", "Cause")
        
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center')
        
        for appt in appointments:
            self.tree.insert('', 'end', values=(
                appt['Appointment_ID'],
                appt['Patient_ID'],
                appt['Staff_ID'],
                str(appt['AppointmentDate']),
                appt['Status'],
                appt['Fee'],
                appt['Cause']
            ))
    
    def generate_rooms_report(self):
        query = "SELECT * FROM Room"
        conditions = []
        params = []
        
        status = self.status_filter.get()
        if status != 'All':
            conditions.append("Status=%s")
            params.append(status)
            
        room_type = self.type_filter.get()
        if room_type != 'All':
            conditions.append("RoomType=%s")
            params.append(room_type)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY Room_no"
        rooms = fetch_all(query, params)
        
        self.tree["columns"] = ("Room No", "Type", "Status", "Floor", "Price/Day")
        
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
        
        for room in rooms:
            self.tree.insert('', 'end', values=(
                room['Room_no'],
                room['RoomType'],
                room['Status'],
                room['Floor'],
                room['PricePerDay']
            ))
        def get_patient_report(patient_id=None, date_range=None):
            query = "SELECT * FROM Patient"
            params = []
    
            if patient_id:
               query += " WHERE Patient_ID = %s"
               params.append(patient_id)
    
            if date_range:  # date_range would be a tuple (start_date, end_date)
               if "WHERE" in query:
                   query += " AND DOB BETWEEN %s AND %s"
            else:
                   query += " WHERE DOB BETWEEN %s AND %s"
                   params.extend(date_range)
    
            return fetch_all(query, params)
    def get_patient_appointments_report():
            query = """
    SELECT p.Patient_ID, p.F_name, p.L_name, 
           a.AppointmentDate, a.Status, s.F_name AS Doctor_Fname, s.L_name AS Doctor_Lname
    FROM Patient p
    JOIN Appointments a ON p.Patient_ID = a.Patient_ID
    JOIN Staff s ON a.Staff_ID = s.Staff_ID
    ORDER BY a.AppointmentDate DESC
    """
            return fetch_all(query)
    
    def generate_room_bookings_report(self):
        query = """
        SELECT b.*, p.F_name, p.L_name, r.RoomType 
        FROM Room_Booking b
        JOIN Patient p ON b.Patient_ID = p.Patient_ID
        JOIN Room r ON b.Room_no = r.Room_no
        """
        conditions = []
        params = []
        
        if self.from_date.get() and self.to_date.get():
            conditions.append("(b.From_date BETWEEN %s AND %s OR b.To_date BETWEEN %s AND %s)")
            params.extend([self.from_date.get(), self.to_date.get(), self.from_date.get(), self.to_date.get()])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY b.From_date DESC"
        bookings = fetch_all(query, params)
        
        self.tree["columns"] = ("Booking ID", "Patient ID", "Patient Name", "Room No", "Room Type", "From Date", "To Date")
        
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
        
        for booking in bookings:
            self.tree.insert('', 'end', values=(
                booking['Booking_ID'],
                booking['Patient_ID'],
                f"{booking['F_name']} {booking['L_name']}",
                booking['Room_no'],
                booking['RoomType'],
                str(booking['From_date']),
                str(booking['To_date'])
            ))
    
    def generate_treatments_report(self):
        query = """
        SELECT t.*, p.F_name, p.L_name, s.F_name AS Doctor_Fname, s.L_name AS Doctor_Lname 
        FROM Treatments t
        JOIN Patient p ON t.Patient_ID = p.Patient_ID
        JOIN Staff s ON t.DoctorID = s.Staff_ID
        """
        conditions = []
        params = []
        
        if self.from_date.get() and self.to_date.get():
            conditions.append("(t.StartDate BETWEEN %s AND %s OR t.EndDate BETWEEN %s AND %s)")
            params.extend([self.from_date.get(), self.to_date.get(), self.from_date.get(), self.to_date.get()])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY t.StartDate DESC"
        treatments = fetch_all(query, params)
        
        self.tree["columns"] = ("ID", "Patient ID", "Patient Name", "Doctor ID", "Doctor Name", 
                              "Diagnosis", "Treatment", "Start Date", "End Date", "Amount")
        
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
        
        for treatment in treatments:
            self.tree.insert('', 'end', values=(
                treatment['TreatmentID'],
                treatment['Patient_ID'],
                f"{treatment['F_name']} {treatment['L_name']}",
                treatment['DoctorID'],
                f"{treatment['Doctor_Fname']} {treatment['Doctor_Lname']}",
                treatment['Diagnosis'],
                treatment['Treatment'],
                str(treatment['StartDate']),
                str(treatment['EndDate']),
                treatment['Amount']
            ))
    
    def export_to_csv(self):
        items = self.tree.get_children()
        if not items:
            messagebox.showwarning("No Data", "No data to export. Please generate a report first.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Report As"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write headers
                headers = [self.tree.heading(col)['text'] for col in self.tree['columns']]
                writer.writerow(headers)
                
                # Write data
                for item in items:
                    row = self.tree.item(item)['values']
                    writer.writerow(row)
                    
            messagebox.showinfo("Success", f"Report exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report:\n{str(e)}")
    
    def export_to_pdf(self):
        items = self.tree.get_children()
        if not items:
            messagebox.showwarning("No Data", "No data to export")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        headers = [self.tree.heading(col)['text'] for col in self.tree['columns']]

        for header in headers:
            pdf.cell(40, 10, txt=header, border=1)
        pdf.ln()

        for item in items:
            row = self.tree.item(item)['values']
            for value in row:
                pdf.cell(40, 10, txt=str(value), border=1)
            pdf.ln()

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save Report As PDF"
        )

        if file_path:
            pdf.output(file_path)
            messagebox.showinfo("Success", f"Report saved to {file_path}")

# --- Patient Tab ---
class PatientTab(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.create_widgets()
        self.load_patients()

    def create_widgets(self):
        form_frame = ttk.Frame(self)
        form_frame.pack(side='top', fill='x', padx=10, pady=5)

        labels = ["First Name", "Middle Name", "Last Name", "Phone", "Gender", 
                 "Patient Type", "DOB (YYYY-MM-DD)", "Blood Type", "City", "State", "Gov"]
        self.entries = {}

        for i, label in enumerate(labels):
            ttk.Label(form_frame, text=label).grid(row=i//4, column=(i%4)*2, sticky='w', padx=5, pady=2)
            if label == "Gender":
                self.entries[label] = ttk.Combobox(form_frame, values=['Male', 'Female', 'Other'], state='readonly')
            elif label == "Patient Type":
                self.entries[label] = ttk.Combobox(form_frame, values=['InPatient', 'OutPatient', 'EmergencyPatient'], state='readonly')
            else:
                self.entries[label] = ttk.Entry(form_frame)
            self.entries[label].grid(row=i//4, column=(i%4)*2 +1, padx=5, pady=2)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Patient", command=self.add_patient).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Patient", command=self.update_patient).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Patient", command=self.delete_patient).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear Fields", command=self.clear_fields).pack(side='left', padx=5)

        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        ttk.Button(search_frame, text="Search", command=self.search_patients).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Reset", command=self.load_patients).pack(side='left', padx=5)

        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Filter by:").pack(side='left', padx=5)
        self.filter_field = ttk.Combobox(filter_frame, values=[
            "All", "Patient ID", "First Name", "Last Name", "Phone", 
            "Gender", "Patient Type", "Blood Type", "City"
        ], state="readonly")
        self.filter_field.set("All")
        self.filter_field.pack(side='left', padx=5)

        self.tree = ttk.Treeview(self, columns=("Patient_ID", "F_name", "M_name", "L_name", "Phone_no", 
                                              "Gender", "PatientType", "DOB", "Blood_type", "City", "State", "Gov"), 
                               show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90)
        self.tree.pack(fill='both', expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def load_patients(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = fetch_all("SELECT * FROM Patient ORDER BY Patient_ID")
        for r in rows:
            self.tree.insert('', 'end', values=(
                r['Patient_ID'], r['F_name'], r['M_name'], r['L_name'], r['Phone_no'],
                r['Gender'], r['PatientType'], str(r['DOB']), r['Blood_type'], r['City'], r['State'], r['Gov']
            ))

    def clear_fields(self):
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set('')
            else:
                entry.delete(0, tk.END)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            keys = list(self.entries.keys())
            for i, key in enumerate(keys):
                if isinstance(self.entries[key], ttk.Combobox):
                    self.entries[key].set(values[i+1])
                else:
                    self.entries[key].delete(0, tk.END)
                    self.entries[key].insert(0, values[i+1])

    def add_patient(self):
        try:
            vals = {key: (self.entries[key].get().strip() or None) for key in self.entries}
            sql = """
                INSERT INTO Patient 
                (F_name, M_name, L_name, Phone_no, Gender, PatientType, DOB, Blood_type, City, State, Gov)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            execute_query(sql, (
                vals['First Name'], vals['Middle Name'], vals['Last Name'], vals['Phone'], 
                vals['Gender'], vals['Patient Type'], vals['DOB (YYYY-MM-DD)'], 
                vals['Blood Type'], vals['City'], vals['State'], vals['Gov']
            ))
            messagebox.showinfo("Success", "Patient added successfully")
            self.load_patients()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Error adding patient:\n{e}")

    def update_patient(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Patient", "Please select a patient to update")
            return
        pid = self.tree.item(selected[0])['values'][0]
        try:
            vals = {key: (self.entries[key].get().strip() or None) for key in self.entries}
            sql = """
                UPDATE Patient SET 
                    F_name=%s, M_name=%s, L_name=%s, Phone_no=%s, Gender=%s, PatientType=%s, DOB=%s,
                    Blood_type=%s, City=%s, State=%s, Gov=%s
                WHERE Patient_ID=%s
            """
            execute_query(sql, (
                vals['First Name'], vals['Middle Name'], vals['Last Name'], vals['Phone'], 
                vals['Gender'], vals['Patient Type'], vals['DOB (YYYY-MM-DD)'], 
                vals['Blood Type'], vals['City'], vals['State'], vals['Gov'], pid
            ))
            messagebox.showinfo("Success", "Patient updated successfully")
            self.load_patients()
        except Exception as e:
            messagebox.showerror("Error", f"Error updating patient:\n{e}")

    def delete_patient(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Patient", "Please select a patient to delete")
            return
        pid = self.tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patient and all related records?"):
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                tables = ["InPatient", "OutPatient", "EmergencyPatient", "Appointments", 
                         "Treatments", "Admission", "Room_Booking", "RoomAllocations"]
                for table in tables:
                    try:
                        cursor.execute(f"DELETE FROM {table} WHERE Patient_ID=%s", (pid,))
                    except:
                        pass
                
                cursor.execute("DELETE FROM Patient WHERE Patient_ID=%s", (pid,))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                messagebox.showinfo("Success", "Patient and all related records deleted successfully")
                self.load_patients()
                self.clear_fields()
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting patient:\n{e}")

    def search_patients(self):
        search_term = self.search_entry.get()
        filter_by = self.filter_field.get()
        
        if not search_term:
            self.load_patients()
            return
            
        query = "SELECT * FROM Patient WHERE "
        params = []
        
        if filter_by == "All":
            query += """
                (Patient_ID LIKE %s OR F_name LIKE %s OR L_name LIKE %s OR Phone_no LIKE %s 
                OR Gender LIKE %s OR PatientType LIKE %s OR Blood_type LIKE %s OR City LIKE %s)
            """
            params = [f"%{search_term}%"] * 8
        else:
            field_map = {
                "Patient ID": "Patient_ID",
                "First Name": "F_name",
                "Last Name": "L_name",
                "Phone": "Phone_no",
                "Gender": "Gender",
                "Patient Type": "PatientType",
                "Blood Type": "Blood_type",
                "City": "City"
            }
            query += f"{field_map[filter_by]} LIKE %s"
            params = [f"%{search_term}%"]
        
        query += " ORDER BY Patient_ID"
        
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        rows = fetch_all(query, params)
        for r in rows:
            self.tree.insert('', 'end', values=(
                r['Patient_ID'], r['F_name'], r['M_name'], r['L_name'], r['Phone_no'],
                r['Gender'], r['PatientType'], str(r['DOB']), r['Blood_type'], r['City'], r['State'], r['Gov']
            ))

# --- Staff Tab ---
class StaffTab(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.create_widgets()
        self.load_staff()

    def create_widgets(self):
        form_frame = ttk.Frame(self)
        form_frame.pack(side='top', fill='x', padx=10, pady=5)

        labels = ["First Name", "Middle Name", "Last Name", "Staff Type", "Phone", "Department"]
        self.entries = {}

        for i, label in enumerate(labels):
            ttk.Label(form_frame, text=label).grid(row=i//3, column=(i%3)*2, sticky='w', padx=5, pady=2)
            if label == "Staff Type":
                self.entries[label] = ttk.Combobox(form_frame, values=['Doctor', 'Nurse', 'Technician'], state='readonly')
            else:
                self.entries[label] = ttk.Entry(form_frame)
            self.entries[label].grid(row=i//3, column=(i%3)*2 +1, padx=5, pady=2)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Staff", command=self.add_staff).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Staff", command=self.update_staff).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Staff", command=self.delete_staff).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear Fields", command=self.clear_fields).pack(side='left', padx=5)

        # Search Frame
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        ttk.Button(search_frame, text="Search", command=self.search_staff).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Reset", command=self.load_staff).pack(side='left', padx=5)

        # Filter Options
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Filter by:").pack(side='left', padx=5)
        self.filter_field = ttk.Combobox(filter_frame, values=[
            "All", "Staff ID", "First Name", "Last Name", "Phone", 
            "Staff Type", "Department"
        ], state="readonly")
        self.filter_field.set("All")
        self.filter_field.pack(side='left', padx=5)

        # Treeview
        self.tree = ttk.Treeview(self, columns=("Staff_ID", "F_name", "M_name", "L_name", "StaffType", "Phone_no", "Department"), 
                               show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill='both', expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def load_staff(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = fetch_all("SELECT * FROM Staff ORDER BY Staff_ID")
        for r in rows:
            self.tree.insert('', 'end', values=(
                r['Staff_ID'], r['F_name'], r['M_name'], r['L_name'], 
                r['StaffType'], r['Phone_no'], r['Department']
            ))

    def clear_fields(self):
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set('')
            else:
                entry.delete(0, tk.END)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            keys = list(self.entries.keys())
            for i, key in enumerate(keys):
                if isinstance(self.entries[key], ttk.Combobox):
                    self.entries[key].set(values[i+1])
                else:
                    self.entries[key].delete(0, tk.END)
                    self.entries[key].insert(0, values[i+1])

    def add_staff(self):
        try:
            vals = {key: self.entries[key].get().strip() or None for key in self.entries}
            sql = """
                INSERT INTO Staff (F_name, M_name, L_name, StaffType, Phone_no, Department)
                VALUES (%s,%s,%s,%s,%s,%s)
            """
            execute_query(sql, (
                vals['First Name'], vals['Middle Name'], vals['Last Name'], 
                vals['Staff Type'], vals['Phone'], vals['Department']
            ))
            messagebox.showinfo("Success", "Staff added successfully")
            self.load_staff()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Error adding staff:\n{e}")

    def update_staff(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Staff", "Please select a staff member to update")
            return
        sid = self.tree.item(selected[0])['values'][0]
        try:
            vals = {key: self.entries[key].get().strip() or None for key in self.entries}
            sql = """
                UPDATE Staff SET F_name=%s, M_name=%s, L_name=%s, StaffType=%s, Phone_no=%s, Department=%s
                WHERE Staff_ID=%s
            """
            execute_query(sql, (
                vals['First Name'], vals['Middle Name'], vals['Last Name'], 
                vals['Staff Type'], vals['Phone'], vals['Department'], sid
            ))
            messagebox.showinfo("Success", "Staff updated successfully")
            self.load_staff()
        except Exception as e:
            messagebox.showerror("Error", f"Error updating staff:\n{e}")

    def delete_staff(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Staff", "Please select a staff member to delete")
            return
        sid = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this staff member?"):
            try:
                execute_query("DELETE FROM Staff WHERE Staff_ID=%s", (sid,))
                messagebox.showinfo("Success", "Staff deleted successfully")
                self.load_staff()
                self.clear_fields()
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting staff:\n{e}")

    def search_staff(self):
        search_term = self.search_entry.get()
        filter_by = self.filter_field.get()
        
        if not search_term:
            self.load_staff()
            return
            
        query = "SELECT * FROM Staff WHERE "
        params = []
        
        if filter_by == "All":
            query += """
                (Staff_ID LIKE %s OR F_name LIKE %s OR L_name LIKE %s OR Phone_no LIKE %s 
                OR StaffType LIKE %s OR Department LIKE %s)
            """
            params = [f"%{search_term}%"] * 6
        else:
            field_map = {
                "Staff ID": "Staff_ID",
                "First Name": "F_name",
                "Last Name": "L_name",
                "Phone": "Phone_no",
                "Staff Type": "StaffType",
                "Department": "Department"
            }
            query += f"{field_map[filter_by]} LIKE %s"
            params = [f"%{search_term}%"]
        
        query += " ORDER BY Staff_ID"
        
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        rows = fetch_all(query, params)
        for r in rows:
            self.tree.insert('', 'end', values=(
                r['Staff_ID'], r['F_name'], r['M_name'], r['L_name'], 
                r['StaffType'], r['Phone_no'], r['Department']
            ))

# --- Appointment Tab ---
class AppointmentTab(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.create_widgets()
        self.load_appointments()

    def create_widgets(self):
        form_frame = ttk.Frame(self)
        form_frame.pack(side='top', fill='x', padx=10, pady=5)

        labels = ["Patient ID", "Staff ID", "Appointment Date (YYYY-MM-DD HH:MM:SS)", "Status", "Fee", "Cause"]
        self.entries = {}

        for i, label in enumerate(labels):
            ttk.Label(form_frame, text=label).grid(row=i//3, column=(i%3)*2, sticky='w', padx=5, pady=2)
            if label == "Status":
                self.entries[label] = ttk.Combobox(form_frame, values=['Scheduled', 'Completed', 'Cancelled'], state='readonly')
            else:
                self.entries[label] = ttk.Entry(form_frame)
            self.entries[label].grid(row=i//3, column=(i%3)*2 +1, padx=5, pady=2)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Appointment", command=self.add_appointment).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Appointment", command=self.update_appointment).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Appointment", command=self.delete_appointment).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear Fields", command=self.clear_fields).pack(side='left', padx=5)

        # Search Frame
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        ttk.Button(search_frame, text="Search", command=self.search_appointments).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Reset", command=self.load_appointments).pack(side='left', padx=5)

        # Filter Options
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Filter by:").pack(side='left', padx=5)
        self.filter_field = ttk.Combobox(filter_frame, values=[
            "All", "Appointment ID", "Patient ID", "Staff ID", 
            "Status", "Date Range", "Fee Range"
        ], state="readonly")
        self.filter_field.set("All")
        self.filter_field.pack(side='left', padx=5)

        # Date Range Fields
        self.date_range_frame = ttk.Frame(self)
        ttk.Label(self.date_range_frame, text="From:").pack(side='left', padx=5)
        self.from_date = ttk.Entry(self.date_range_frame)
        self.from_date.pack(side='left', padx=5)
        ttk.Label(self.date_range_frame, text="To:").pack(side='left', padx=5)
        self.to_date = ttk.Entry(self.date_range_frame)
        self.to_date.pack(side='left', padx=5)

        # Fee Range Fields
        self.fee_range_frame = ttk.Frame(self)
        ttk.Label(self.fee_range_frame, text="Min:").pack(side='left', padx=5)
        self.min_fee = ttk.Entry(self.fee_range_frame)
        self.min_fee.pack(side='left', padx=5)
        ttk.Label(self.fee_range_frame, text="Max:").pack(side='left', padx=5)
        self.max_fee = ttk.Entry(self.fee_range_frame)
        self.max_fee.pack(side='left', padx=5)

        # Show/hide frames based on filter selection
        self.filter_field.bind("<<ComboboxSelected>>", self.update_filter_fields)

        # Treeview
        self.tree = ttk.Treeview(self, columns=("Appointment_ID", "Patient_ID", "Staff_ID", "AppointmentDate", "Status", "Fee", "Cause"), 
                               show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140)
        self.tree.pack(fill='both', expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def load_appointments(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = fetch_all("SELECT * FROM Appointments ORDER BY Appointment_ID")
        for r in rows:
            self.tree.insert('', 'end', values=(
                r['Appointment_ID'], r['Patient_ID'], r['Staff_ID'], 
                str(r['AppointmentDate']), r['Status'], r['Fee'], r['Cause']
            ))

    def clear_fields(self):
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set('')
            else:
                entry.delete(0, tk.END)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            keys = list(self.entries.keys())
            for i, key in enumerate(keys):
                if isinstance(self.entries[key], ttk.Combobox):
                    self.entries[key].set(values[i+1])
                else:
                    self.entries[key].delete(0, tk.END)
                    self.entries[key].insert(0, values[i+1])

    def add_appointment(self):
        try:
            vals = {key: (self.entries[key].get().strip() or None) for key in self.entries}
            sql = """
                INSERT INTO Appointments (Patient_ID, Staff_ID, AppointmentDate, Status, Fee, Cause)
                VALUES (%s,%s,%s,%s,%s,%s)
            """
            execute_query(sql, (
                vals['Patient ID'], vals['Staff ID'], vals['Appointment Date (YYYY-MM-DD HH:MM:SS)'], 
                vals['Status'], vals['Fee'], vals['Cause']
            ))
            messagebox.showinfo("Success", "Appointment added successfully")
            self.load_appointments()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Error adding appointment:\n{e}")

    def update_appointment(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Appointment", "Please select an appointment to update")
            return
        aid = self.tree.item(selected[0])['values'][0]
        try:
            vals = {key: (self.entries[key].get().strip() or None) for key in self.entries}
            sql = """
                UPDATE Appointments SET Patient_ID=%s, Staff_ID=%s, AppointmentDate=%s, Status=%s, Fee=%s, Cause=%s
                WHERE Appointment_ID=%s
            """
            execute_query(sql, (
                vals['Patient ID'], vals['Staff ID'], vals['Appointment Date (YYYY-MM-DD HH:MM:SS)'], 
                vals['Status'], vals['Fee'], vals['Cause'], aid
            ))
            messagebox.showinfo("Success", "Appointment updated successfully")
            self.load_appointments()
        except Exception as e:
            messagebox.showerror("Error", f"Error updating appointment:\n{e}")

    def delete_appointment(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Appointment", "Please select an appointment to delete")
            return
        aid = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this appointment?"):
            try:
                execute_query("DELETE FROM Appointments WHERE Appointment_ID=%s", (aid,))
                messagebox.showinfo("Success", "Appointment deleted successfully")
                self.load_appointments()
                self.clear_fields()
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting appointment:\n{e}")

    def update_filter_fields(self, event):
        selected_filter = self.filter_field.get()
        
        # Hide all special filter frames
        self.date_range_frame.pack_forget()
        self.fee_range_frame.pack_forget()
        
        if selected_filter == "Date Range":
            self.date_range_frame.pack(fill='x', padx=10, pady=5)
        elif selected_filter == "Fee Range":
            self.fee_range_frame.pack(fill='x', padx=10, pady=5)

    def search_appointments(self):
        search_term = self.search_entry.get()
        filter_by = self.filter_field.get()
        
        query = "SELECT * FROM Appointments"
        params = []
        conditions = []
        
        if filter_by == "All" and search_term:
            conditions.append("""
                (Appointment_ID LIKE %s OR Patient_ID LIKE %s OR Staff_ID LIKE %s 
                OR Status LIKE %s OR Fee LIKE %s OR Cause LIKE %s)
            """)
            params.extend([f"%{search_term}%"] * 6)
        elif filter_by != "All":
            if filter_by == "Date Range":
                if self.from_date.get() and self.to_date.get():
                    conditions.append("AppointmentDate BETWEEN %s AND %s")
                    params.extend([self.from_date.get(), self.to_date.get()])
            elif filter_by == "Fee Range":
                if self.min_fee.get() and self.max_fee.get():
                    conditions.append("Fee BETWEEN %s AND %s")
                    params.extend([self.min_fee.get(), self.max_fee.get()])
            else:
                field_map = {
                    "Appointment ID": "Appointment_ID",
                    "Patient ID": "Patient_ID",
                    "Staff ID": "Staff_ID",
                    "Status": "Status"
                }
                if search_term:
                    conditions.append(f"{field_map[filter_by]} LIKE %s")
                    params.append(f"%{search_term}%")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY AppointmentDate DESC"
        
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        rows = fetch_all(query, params)
        for r in rows:
            self.tree.insert('', 'end', values=(
                r['Appointment_ID'], r['Patient_ID'], r['Staff_ID'], 
                str(r['AppointmentDate']), r['Status'], r['Fee'], r['Cause']
            ))

# --- Room Tab ---
class RoomTab(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.create_widgets()
        self.load_rooms()
        self.load_room_bookings()

    def create_widgets(self):
        room_notebook = ttk.Notebook(self)
        room_notebook.pack(fill='both', expand=True)
        
        # Room Management Tab
        self.room_management_tab = ttk.Frame(room_notebook)
        room_notebook.add(self.room_management_tab, text="Room Management")
        
        # Room Type Selection
        ttk.Label(self.room_management_tab, text="Room Type:").grid(row=0, column=0, padx=5, pady=5)
        self.room_type = tk.StringVar()
        self.room_type.set("Regular")
        
        room_types = ["Regular", "ICU", "Operation"]
        for i, r_type in enumerate(room_types):
            ttk.Radiobutton(self.room_management_tab, text=r_type, variable=self.room_type, 
                           value=r_type).grid(row=0, column=i+1, padx=5, pady=5)
        
        # Common Room Fields
        ttk.Label(self.room_management_tab, text="Room Status:").grid(row=1, column=0, padx=5, pady=5)
        self.room_status = ttk.Combobox(self.room_management_tab, values=["Available", "Occupied", "Maintenance"], state="readonly")
        self.room_status.grid(row=1, column=1, padx=5, pady=5)
        self.room_status.set("Available")
        
        ttk.Label(self.room_management_tab, text="Floor:").grid(row=2, column=0, padx=5, pady=5)
        self.floor = ttk.Entry(self.room_management_tab)
        self.floor.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self.room_management_tab, text="Price Per Day:").grid(row=3, column=0, padx=5, pady=5)
        self.price_per_day = ttk.Entry(self.room_management_tab)
        self.price_per_day.grid(row=3, column=1, padx=5, pady=5)
        
        # Specific Fields Frame
        self.room_specific_fields_frame = ttk.LabelFrame(self.room_management_tab, text="Room Specific Fields")
        self.room_specific_fields_frame.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
        self.show_room_specific_fields()
        self.room_type.trace('w', lambda *args: self.show_room_specific_fields())
        
        # Room Management Buttons
        btn_frame = ttk.Frame(self.room_management_tab)
        btn_frame.grid(row=5, column=0, columnspan=4, pady=10)
        
        ttk.Button(btn_frame, text="Add Room", command=self.add_room).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Update Room", command=self.update_room).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Room", command=self.delete_room).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear Fields", command=self.clear_room_fields).pack(side='left', padx=5)

        # Room Treeview
        self.room_tree = ttk.Treeview(self.room_management_tab, columns=("Room_no", "RoomType", "Status", "Floor", "PricePerDay"), show='headings')
        for col in ["Room_no", "RoomType", "Status", "Floor", "PricePerDay"]:
            self.room_tree.heading(col, text=col)
            self.room_tree.column(col, width=100)
        self.room_tree.grid(row=6, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")
        self.room_tree.bind("<<TreeviewSelect>>", self.on_room_select)
        
        # Search Frame for Rooms
        room_search_frame = ttk.Frame(self.room_management_tab)
        room_search_frame.grid(row=7, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
        
        ttk.Label(room_search_frame, text="Search Rooms:").pack(side='left', padx=5)
        self.room_search_entry = ttk.Entry(room_search_frame)
        self.room_search_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        ttk.Button(room_search_frame, text="Search", command=self.search_rooms).pack(side='left', padx=5)
        ttk.Button(room_search_frame, text="Reset", command=self.load_rooms).pack(side='left', padx=5)

        # Room Filter Options
        room_filter_frame = ttk.Frame(self.room_management_tab)
        room_filter_frame.grid(row=8, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
        
        ttk.Label(room_filter_frame, text="Filter by:").pack(side='left', padx=5)
        self.room_filter_field = ttk.Combobox(room_filter_frame, values=[
            "All", "Room No", "Room Type", "Status", "Floor", "Price Range"
        ], state="readonly")
        self.room_filter_field.set("All")
        self.room_filter_field.pack(side='left', padx=5)

        # Price Range Fields
        self.price_range_frame = ttk.Frame(self.room_management_tab)
        ttk.Label(self.price_range_frame, text="Min:").pack(side='left', padx=5)
        self.min_price = ttk.Entry(self.price_range_frame)
        self.min_price.pack(side='left', padx=5)
        ttk.Label(self.price_range_frame, text="Max:").pack(side='left', padx=5)
        self.max_price = ttk.Entry(self.price_range_frame)
        self.max_price.pack(side='left', padx=5)

        # Show/hide price range based on filter selection
        self.room_filter_field.bind("<<ComboboxSelected>>", self.update_room_filter_fields)

        # Room Booking Tab
        self.room_booking_tab = ttk.Frame(room_notebook)
        room_notebook.add(self.room_booking_tab, text="Room Bookings")
        
        # Booking Form
        ttk.Label(self.room_booking_tab, text="Patient ID:").grid(row=0, column=0, padx=5, pady=5)
        self.booking_patient_id = ttk.Entry(self.room_booking_tab)
        self.booking_patient_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.room_booking_tab, text="Room No:").grid(row=1, column=0, padx=5, pady=5)
        self.booking_room_no = ttk.Entry(self.room_booking_tab)
        self.booking_room_no.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.room_booking_tab, text="From Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
        self.booking_from_date = ttk.Entry(self.room_booking_tab)
        self.booking_from_date.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self.room_booking_tab, text="To Date (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5)
        self.booking_to_date = ttk.Entry(self.room_booking_tab)
        self.booking_to_date.grid(row=3, column=1, padx=5, pady=5)
        
        # Booking Buttons
        booking_btn_frame = ttk.Frame(self.room_booking_tab)
        booking_btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(booking_btn_frame, text="Book Room", command=self.book_room).pack(side='left', padx=5)
        ttk.Button(booking_btn_frame, text="Update Booking", command=self.update_booking).pack(side='left', padx=5)
        ttk.Button(booking_btn_frame, text="Delete Booking", command=self.delete_booking).pack(side='left', padx=5)
        ttk.Button(booking_btn_frame, text="Clear Booking Fields", command=self.clear_booking_fields).pack(side='left', padx=5)

        # Booking Treeview
        self.booking_tree = ttk.Treeview(self.room_booking_tab, columns=("Booking_ID", "Patient_ID", "Room_no", "From_date", "To_date"), show='headings')
        for col in ["Booking_ID", "Patient_ID", "Room_no", "From_date", "To_date"]:
            self.booking_tree.heading(col, text=col)
            self.booking_tree.column(col, width=120)
        self.booking_tree.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.booking_tree.bind("<<TreeviewSelect>>", self.on_booking_select)

        # Search Frame for Bookings
        booking_search_frame = ttk.Frame(self.room_booking_tab)
        booking_search_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        ttk.Label(booking_search_frame, text="Search Bookings:").pack(side='left', padx=5)
        self.booking_search_entry = ttk.Entry(booking_search_frame)
        self.booking_search_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        ttk.Button(booking_search_frame, text="Search", command=self.search_bookings).pack(side='left', padx=5)
        ttk.Button(booking_search_frame, text="Reset", command=self.load_room_bookings).pack(side='left', padx=5)

        # Configure grid weights
        self.room_management_tab.grid_rowconfigure(6, weight=1)
        self.room_management_tab.grid_columnconfigure(0, weight=1)
        self.room_booking_tab.grid_rowconfigure(5, weight=1)
        self.room_booking_tab.grid_columnconfigure(0, weight=1)
    
    def show_room_specific_fields(self):
        for widget in self.room_specific_fields_frame.winfo_children():
            widget.destroy()
            
        r_type = self.room_type.get()
        
        if r_type == "Regular":
            ttk.Label(self.room_specific_fields_frame, text="Bed Count:").grid(row=0, column=0, padx=5, pady=5)
            self.bed_count = ttk.Entry(self.room_specific_fields_frame)
            self.bed_count.grid(row=0, column=1, padx=5, pady=5)
            
            ttk.Label(self.room_specific_fields_frame, text="Room Size:").grid(row=1, column=0, padx=5, pady=5)
            self.room_size = ttk.Combobox(self.room_specific_fields_frame, values=["Single", "Double", "Triple"], state="readonly")
            self.room_size.grid(row=1, column=1, padx=5, pady=5)
            self.room_size.set("Single")
            
        elif r_type == "ICU":
            ttk.Label(self.room_specific_fields_frame, text="ICU Level:").grid(row=0, column=0, padx=5, pady=5)
            self.icu_level = ttk.Combobox(self.room_specific_fields_frame, values=["Level 1", "Level 2", "Level 3"], state="readonly")
            self.icu_level.grid(row=0, column=1, padx=5, pady=5)
            self.icu_level.set("Level 1")
            
        elif r_type == "Operation":
            ttk.Label(self.room_specific_fields_frame, text="Surgical Speciality:").grid(row=0, column=0, padx=5, pady=5)
            self.surgical_speciality = ttk.Entry(self.room_specific_fields_frame)
            self.surgical_speciality.grid(row=0, column=1, padx=5, pady=5)
    
    def clear_room_fields(self):
        self.room_status.set("Available")
        self.floor.delete(0, tk.END)
        self.price_per_day.delete(0, tk.END)
        
        r_type = self.room_type.get()
        if r_type == "Regular":
            self.bed_count.delete(0, tk.END)
            self.room_size.set("Single")
        elif r_type == "ICU":
            self.icu_level.set("Level 1")
        elif r_type == "Operation":
            self.surgical_speciality.delete(0, tk.END)
    
    def clear_booking_fields(self):
        self.booking_patient_id.delete(0, tk.END)
        self.booking_room_no.delete(0, tk.END)
        self.booking_from_date.delete(0, tk.END)
        self.booking_to_date.delete(0, tk.END)
    
    def load_rooms(self):
        for row in self.room_tree.get_children():
            self.room_tree.delete(row)
        
        rooms = fetch_all("SELECT * FROM Room ORDER BY Room_no")
        for room in rooms:
            self.room_tree.insert('', 'end', values=(
                room['Room_no'], room['RoomType'], room['Status'], 
                room['Floor'], room['PricePerDay']
            ))
    
    def load_room_bookings(self):
        for row in self.booking_tree.get_children():
            self.booking_tree.delete(row)
        
        bookings = fetch_all("SELECT * FROM Room_Booking ORDER BY Booking_ID")
        for booking in bookings:
            self.booking_tree.insert('', 'end', values=(
                booking['Booking_ID'], booking['Patient_ID'], booking['Room_no'], 
                str(booking['From_date']), str(booking['To_date'])
            ))
    
    def on_room_select(self, event):
        selected = self.room_tree.selection()
        if selected:
            values = self.room_tree.item(selected[0])['values']
            self.room_type.set(values[1])
            self.room_status.set(values[2])
            self.floor.delete(0, tk.END)
            self.floor.insert(0, values[3])
            self.price_per_day.delete(0, tk.END)
            self.price_per_day.insert(0, values[4])
            
            room_no = values[0]
            r_type = values[1]
            
            if r_type == "Regular":
                room_data = fetch_all("SELECT * FROM Regular WHERE Room_no=%s", (room_no,))
                if room_data:
                    self.bed_count.delete(0, tk.END)
                    self.bed_count.insert(0, room_data[0]['Bed_count'])
                    self.room_size.set(room_data[0]['Room_size'])
            
            elif r_type == "ICU":
                room_data = fetch_all("SELECT * FROM ICU WHERE Room_no=%s", (room_no,))
                if room_data:
                    self.icu_level.set(room_data[0]['ICU_level'])
            
            elif r_type == "Operation":
                room_data = fetch_all("SELECT * FROM Operation WHERE Room_no=%s", (room_no,))
                if room_data:
                    self.surgical_speciality.delete(0, tk.END)
                    self.surgical_speciality.insert(0, room_data[0]['SurgicalSpeciality'])
    
    def on_booking_select(self, event):
        selected = self.booking_tree.selection()
        if selected:
            values = self.booking_tree.item(selected[0])['values']
            self.booking_patient_id.delete(0, tk.END)
            self.booking_patient_id.insert(0, values[1])
            self.booking_room_no.delete(0, tk.END)
            self.booking_room_no.insert(0, values[2])
            self.booking_from_date.delete(0, tk.END)
            self.booking_from_date.insert(0, values[3])
            self.booking_to_date.delete(0, tk.END)
            self.booking_to_date.insert(0, values[4])
    
    def update_room_filter_fields(self, event):
        selected_filter = self.room_filter_field.get()
        self.price_range_frame.grid_forget()
        
        if selected_filter == "Price Range":
            self.price_range_frame.grid(row=9, column=0, columnspan=4, padx=10, pady=5, sticky="ew")

    def search_rooms(self):
        search_term = self.room_search_entry.get()
        filter_by = self.room_filter_field.get()
        
        query = "SELECT * FROM Room"
        params = []
        conditions = []
        
        if filter_by == "All" and search_term:
            conditions.append("""
                (Room_no LIKE %s OR RoomType LIKE %s OR Status LIKE %s 
                OR Floor LIKE %s OR PricePerDay LIKE %s)
            """)
            params.extend([f"%{search_term}%"] * 5)
        elif filter_by != "All":
            if filter_by == "Price Range":
                if self.min_price.get() and self.max_price.get():
                    conditions.append("PricePerDay BETWEEN %s AND %s")
                    params.extend([self.min_price.get(), self.max_price.get()])
            else:
                field_map = {
                    "Room No": "Room_no",
                    "Room Type": "RoomType",
                    "Status": "Status",
                    "Floor": "Floor"
                }
                if search_term:
                    conditions.append(f"{field_map[filter_by]} LIKE %s")
                    params.append(f"%{search_term}%")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY Room_no"
        
        for row in self.room_tree.get_children():
            self.room_tree.delete(row)
            
        rooms = fetch_all(query, params)
        for room in rooms:
            self.room_tree.insert('', 'end', values=(
                room['Room_no'], room['RoomType'], room['Status'], 
                room['Floor'], room['PricePerDay']
            ))

    def search_bookings(self):
        search_term = self.booking_search_entry.get()
        
        query = """
        SELECT * FROM Room_Booking 
        WHERE Patient_ID LIKE %s OR Room_no LIKE %s
        ORDER BY From_date DESC
        """
        params = [f"%{search_term}%", f"%{search_term}%"]
        
        for row in self.booking_tree.get_children():
            self.booking_tree.delete(row)
            
        bookings = fetch_all(query, params)
        for booking in bookings:
            self.booking_tree.insert('', 'end', values=(
                booking['Booking_ID'], booking['Patient_ID'], booking['Room_no'], 
                str(booking['From_date']), str(booking['To_date'])
            ))
    
    def add_room(self):
        try:
            # Start a transaction
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                # First insert into Room table
                query = """
                INSERT INTO Room (RoomType, Status, Floor, PricePerDay)
                VALUES (%s, %s, %s, %s)
                """
                values = (
                    self.room_type.get(),
                    self.room_status.get(),
                    self.floor.get(),
                    self.price_per_day.get()
                )
                cursor.execute(query, values)
                
                # Get the auto-incremented Room_no
                room_no = cursor.lastrowid
                
                # Then insert into specific room table
                r_type = self.room_type.get()
                
                if r_type == "Regular":
                    query = """
                    INSERT INTO Regular (Room_no, Bed_count, Room_size)
                    VALUES (%s, %s, %s)
                    """
                    values = (
                        room_no,
                        self.bed_count.get(),
                        self.room_size.get()
                    )
                    
                elif r_type == "ICU":
                    query = """
                    INSERT INTO ICU (Room_no, ICU_level)
                    VALUES (%s, %s)
                    """
                    values = (
                        room_no,
                        self.icu_level.get()
                    )
                    
                elif r_type == "Operation":
                    query = """
                    INSERT INTO Operation (Room_no, SurgicalSpeciality)
                    VALUES (%s, %s)
                    """
                    values = (
                        room_no,
                        self.surgical_speciality.get()
                    )
                
                cursor.execute(query, values)
                conn.commit()
                
                messagebox.showinfo("Success", f"Room added successfully with number: {room_no}")
                self.load_rooms()
                self.clear_room_fields()
                
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add room: {str(e)}")
    
    def update_room(self):
        selected = self.room_tree.selection()
        if not selected:
            messagebox.showwarning("Select Room", "Please select a room to update")
            return
        
        try:
            room_no = self.room_tree.item(selected[0])['values'][0]
            r_type = self.room_type.get()
            
            query = """
            UPDATE Room SET RoomType=%s, Status=%s, Floor=%s, PricePerDay=%s
            WHERE Room_no=%s
            """
            values = (
                r_type,
                self.room_status.get(),
                self.floor.get(),
                self.price_per_day.get(),
                room_no
            )
            execute_query(query, values)
            
            if r_type == "Regular":
                query = """
                UPDATE Regular SET Bed_count=%s, Room_size=%s
                WHERE Room_no=%s
                """
                values = (
                    self.bed_count.get(),
                    self.room_size.get(),
                    room_no
                )
                
            elif r_type == "ICU":
                query = """
                UPDATE ICU SET ICU_level=%s
                WHERE Room_no=%s
                """
                values = (
                    self.icu_level.get(),
                    room_no
                )
                
            elif r_type == "Operation":
                query = """
                UPDATE Operation SET SurgicalSpeciality=%s
                WHERE Room_no=%s
                """
                values = (
                    self.surgical_speciality.get(),
                    room_no
                )
            
            execute_query(query, values)
            
            messagebox.showinfo("Success", "Room updated successfully")
            self.load_rooms()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update room: {str(e)}")
    
    def delete_room(self):
        selected = self.room_tree.selection()
        if not selected:
            messagebox.showwarning("Select Room", "Please select a room to delete")
            return
        
        room_no = self.room_tree.item(selected[0])['values'][0]
        r_type = self.room_tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete this {r_type} room?"):
            try:
                if r_type == "Regular":
                    execute_query("DELETE FROM Regular WHERE Room_no=%s", (room_no,))
                elif r_type == "ICU":
                    execute_query("DELETE FROM ICU WHERE Room_no=%s", (room_no,))
                elif r_type == "Operation":
                    execute_query("DELETE FROM Operation WHERE Room_no=%s", (room_no,))
                
                execute_query("DELETE FROM Room WHERE Room_no=%s", (room_no,))
                
                messagebox.showinfo("Success", "Room deleted successfully")
                self.load_rooms()
                self.clear_room_fields()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete room: {str(e)}")
    
    def book_room(self):
        try:
            query = """
            INSERT INTO Room_Booking (Patient_ID, Room_no, From_date, To_date)
            VALUES (%s, %s, %s, %s)
            """
            values = (
                self.booking_patient_id.get(),
                self.booking_room_no.get(),
                self.booking_from_date.get(),
                self.booking_to_date.get()
            )
            
            execute_query(query, values)
            execute_query("UPDATE Room SET Status='Occupied' WHERE Room_no=%s", (self.booking_room_no.get(),))
            
            messagebox.showinfo("Success", "Room booked successfully")
            self.load_room_bookings()
            self.load_rooms()
            self.clear_booking_fields()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to book room: {str(e)}")
    
    def update_booking(self):
        selected = self.booking_tree.selection()
        if not selected:
            messagebox.showwarning("Select Booking", "Please select a booking to update")
            return
        
        try:
            booking_id = self.booking_tree.item(selected[0])['values'][0]
            old_room_no = self.booking_tree.item(selected[0])['values'][2]
            new_room_no = self.booking_room_no.get()
            
            query = """
            UPDATE Room_Booking SET Patient_ID=%s, Room_no=%s, From_date=%s, To_date=%s
            WHERE Booking_ID=%s
            """
            values = (
                self.booking_patient_id.get(),
                new_room_no,
                self.booking_from_date.get(),
                self.booking_to_date.get(),
                booking_id
            )
            
            execute_query(query, values)
            
            if old_room_no != new_room_no:
                has_other_bookings = fetch_all("""
                    SELECT COUNT(*) AS count FROM Room_Booking 
                    WHERE Room_no=%s AND Booking_ID != %s
                    AND To_date >= CURDATE()
                """, (old_room_no, booking_id))[0]['count']
                
                if not has_other_bookings:
                    execute_query("UPDATE Room SET Status='Available' WHERE Room_no=%s", (old_room_no,))
                
                execute_query("UPDATE Room SET Status='Occupied' WHERE Room_no=%s", (new_room_no,))
            
            messagebox.showinfo("Success", "Booking updated successfully")
            self.load_room_bookings()
            self.load_rooms()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update booking: {str(e)}")
    
    def delete_booking(self):
        selected = self.booking_tree.selection()
        if not selected:
            messagebox.showwarning("Select Booking", "Please select a booking to delete")
            return
        
        booking_id = self.booking_tree.item(selected[0])['values'][0]
        room_no = self.booking_tree.item(selected[0])['values'][2]
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this booking?"):
            try:
                execute_query("DELETE FROM Room_Booking WHERE Booking_ID=%s", (booking_id,))
                
                has_other_bookings = fetch_all("""
                    SELECT COUNT(*) AS count FROM Room_Booking 
                    WHERE Room_no=%s AND To_date >= CURDATE()
                """, (room_no,))[0]['count']
                
                if not has_other_bookings:
                    execute_query("UPDATE Room SET Status='Available' WHERE Room_no=%s", (room_no,))
                
                messagebox.showinfo("Success", "Booking deleted successfully")
                self.load_room_bookings()
                self.load_rooms()
                self.clear_booking_fields()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete booking: {str(e)}")

# --- Main Application ---
class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Management System")
        self.geometry("1200x700")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        # Create tabs
        self.patient_tab = PatientTab(self.notebook)
        self.staff_tab = StaffTab(self.notebook)
        self.appointment_tab = AppointmentTab(self.notebook)
        self.room_tab = RoomTab(self.notebook)
        self.treatment_tab = TreatmentTab(self.notebook)  # New tab
        self.reports_tab = ReportsTab(self.notebook)
        self.query_tab = QueryTab(self.notebook)

        self.notebook.add(self.patient_tab, text="Patients")
        self.notebook.add(self.staff_tab, text="Staff")
        self.notebook.add(self.appointment_tab, text="Appointments")
        self.notebook.add(self.room_tab, text="Rooms")
        self.notebook.add(self.treatment_tab, text="Treatments")  # Add to notebook
        self.notebook.add(self.reports_tab, text="Reports")
        self.notebook.add(self.query_tab, text="SQL Query")

if __name__ == "__main__":
    app = HospitalApp()
    app.mainloop()