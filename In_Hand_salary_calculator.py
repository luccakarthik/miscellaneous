import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont

class IndianSalaryCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Indian Salary Calculator (Detailed)")
        self.root.geometry("950x750")
        
        # Fonts
        self.bold_font = tkfont.Font(weight="bold")
        self.title_font = tkfont.Font(size=10, weight="bold")
        
        # Variables
        self.ctc_var = tk.DoubleVar()
        self.basic_var = tk.DoubleVar()
        self.hra_var = tk.DoubleVar()
        self.special_allowance_var = tk.DoubleVar()
        self.bonus_var = tk.DoubleVar(value=0)
        self.pf_employer_var = tk.DoubleVar()
        self.gratuity_var = tk.DoubleVar(value=0)
        self.medical_var = tk.DoubleVar(value=0)
        self.other_allowances_var = tk.DoubleVar(value=0)
        self.regime_var = tk.StringVar(value="new")  # new, old, new_post_2025
        self.in_hand_var = tk.DoubleVar()
        
        # Create main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input Section
        input_frame = ttk.LabelFrame(self.main_frame, text="Salary Components (Monthly)", padding="10")
        input_frame.pack(fill=tk.X, pady=5)
        
        # Input fields
        components = [
            ("Basic Salary:", self.basic_var),
            ("HRA:", self.hra_var),
            ("Special Allowance:", self.special_allowance_var),
            ("Bonus/Ex Gratia (Annual):", self.bonus_var),
            ("Employer PF Contribution:", self.pf_employer_var),
            ("Gratuity:", self.gratuity_var),
            ("Medical Insurance:", self.medical_var),
            ("Other Allowances:", self.other_allowances_var)
        ]
        
        for i, (label, var) in enumerate(components):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Entry(input_frame, textvariable=var).grid(row=i, column=1, sticky=tk.EW, padx=5, pady=2)
        
        # Tax Regime Selection
        regime_frame = ttk.LabelFrame(self.main_frame, text="Tax Regime", padding="10")
        regime_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(regime_frame, text="Old Regime", variable=self.regime_var, value="old").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(regime_frame, text="New Regime (Current)", variable=self.regime_var, value="new").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(regime_frame, text="New Regime (Post FY 2025-26 Budget)", variable=self.regime_var, value="new_post_2025").pack(side=tk.LEFT, padx=10)
        
        # Calculate Button
        ttk.Button(self.main_frame, text="Calculate Salary", command=self.calculate_salary).pack(pady=10)
        
        # Results Section
        results_frame = ttk.LabelFrame(self.main_frame, text="Salary Breakup", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for results
        self.tree = ttk.Treeview(results_frame, columns=("Component", "Monthly", "Annual"), show="headings")
        self.tree.heading("Component", text="Component")
        self.tree.heading("Monthly", text="Monthly (₹)")
        self.tree.heading("Annual", text="Annual (₹)")
        self.tree.column("Component", width=250)
        self.tree.column("Monthly", width=150, anchor=tk.E)
        self.tree.column("Annual", width=150, anchor=tk.E)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Summary Section
        summary_frame = ttk.Frame(self.main_frame)
        summary_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(summary_frame, text="Monthly In-Hand Salary:", font=self.title_font).pack(side=tk.LEFT, padx=5)
        self.in_hand_label = ttk.Label(summary_frame, text="₹0", font=('Arial', 12, 'bold'))
        self.in_hand_label.pack(side=tk.LEFT, padx=5)
        
        # Action Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Share Results", command=self.share_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Formulas", command=self.show_formulas).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Help", command=self.show_help).pack(side=tk.RIGHT, padx=5)
    
    def calculate_salary(self):
        try:
            # Get monthly components
            monthly_basic = self.basic_var.get()
            monthly_hra = self.hra_var.get()
            monthly_special_allowance = self.special_allowance_var.get()
            monthly_bonus = self.bonus_var.get() / 12  # Convert annual bonus to monthly
            monthly_pf_employer = self.pf_employer_var.get()
            monthly_gratuity = self.gratuity_var.get()
            monthly_medical = self.medical_var.get()
            monthly_other_allowances = self.other_allowances_var.get()
            
            # Calculate annual values
            annual_basic = monthly_basic * 12
            annual_hra = monthly_hra * 12
            annual_special_allowance = monthly_special_allowance * 12
            annual_bonus = self.bonus_var.get()
            annual_pf_employer = monthly_pf_employer * 12
            annual_gratuity = monthly_gratuity * 12
            annual_medical = monthly_medical * 12
            annual_other_allowances = monthly_other_allowances * 12
            
            # Calculate gross salary
            monthly_gross = (monthly_basic + monthly_hra + monthly_special_allowance + 
                            monthly_bonus + monthly_medical + monthly_other_allowances)
            annual_gross = monthly_gross * 12
            
            # Standard Deduction (₹50,000 as per Indian tax laws)
            annual_standard_deduction = 50000
            
            # Professional Tax (₹200 per month in most states)
            annual_professional_tax = 2400
            monthly_professional_tax = 200
            
            # Calculate taxable income based on regime
            regime = self.regime_var.get()
            
            if regime == "old":
                # Old regime deductions
                taxable_income = annual_gross - annual_standard_deduction
                
                # HRA exemption calculation
                hra_exemption = self.calculate_hra_exemption(
                    annual_basic, annual_hra, 
                    min(monthly_hra*12, 0.5*(annual_gross - annual_basic)))  # For metro cities
                taxable_income -= hra_exemption
                
                # Standard deduction already subtracted
                # Section 80C deductions (PF, LIC, etc.)
                section_80c = min(annual_pf_employer + 150000, 150000)  # Max ₹1.5L
                taxable_income -= section_80c
                
                # Medical insurance deduction (Section 80D)
                section_80d = min(annual_medical, 25000)  # For individuals <60 years
                taxable_income -= section_80d
                
                # Calculate tax as per old regime slabs
                annual_income_tax = self.calculate_old_regime_tax(taxable_income)
                
            elif regime == "new":
                # New regime (current)
                taxable_income = annual_gross - annual_standard_deduction
                annual_income_tax = self.calculate_new_regime_tax(taxable_income)
                
            else:  # new_post_2025
                # New regime post 2025-26 budget
                taxable_income = annual_gross - annual_standard_deduction
                annual_income_tax = self.calculate_new_post_2025_regime_tax(taxable_income)
            
            # Cess (4% of income tax)
            annual_income_tax *= 1.04
            monthly_income_tax = annual_income_tax / 12
            
            # Calculate in-hand salary
            monthly_deductions = monthly_professional_tax + monthly_income_tax
            monthly_in_hand = monthly_gross - monthly_deductions
            
            # Update treeview
            self.update_treeview(
                monthly_basic, annual_basic,
                monthly_hra, annual_hra,
                monthly_special_allowance, annual_special_allowance,
                monthly_bonus, annual_bonus,
                monthly_medical, annual_medical,
                monthly_other_allowances, annual_other_allowances,
                monthly_pf_employer, annual_pf_employer,
                monthly_gratuity, annual_gratuity,
                monthly_professional_tax, annual_professional_tax,
                monthly_income_tax, annual_income_tax,
                monthly_in_hand, monthly_in_hand * 12
            )
            
            # Update summary
            self.in_hand_label.config(text=f"₹{monthly_in_hand:,.2f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def calculate_hra_exemption(self, basic, hra, rent_paid):
        """Calculate HRA exemption as per old regime rules"""
        # Least of:
        # 1. Actual HRA received
        # 2. Rent paid - 10% of basic salary
        # 3. 50% of basic (metro) or 40% (non-metro)
        exemption1 = hra
        exemption2 = rent_paid - (0.1 * basic)
        exemption3 = 0.5 * basic  # Assuming metro city
        
        return min(exemption1, exemption2, exemption3)
    
    def calculate_old_regime_tax(self, taxable_income):
        """Calculate tax as per old regime slabs"""
        if taxable_income <= 250000:
            return 0
        elif taxable_income <= 500000:
            return (taxable_income - 250000) * 0.05
        elif taxable_income <= 1000000:
            return 12500 + (taxable_income - 500000) * 0.20
        else:
            return 112500 + (taxable_income - 1000000) * 0.30
    
    def calculate_new_regime_tax(self, taxable_income):
        """Calculate tax as per current new regime slabs"""
        if taxable_income <= 300000:
            return 0
        elif taxable_income <= 600000:
            return (taxable_income - 300000) * 0.05
        elif taxable_income <= 900000:
            return 15000 + (taxable_income - 600000) * 0.10
        elif taxable_income <= 1200000:
            return 45000 + (taxable_income - 900000) * 0.15
        elif taxable_income <= 1500000:
            return 90000 + (taxable_income - 1200000) * 0.20
        else:
            return 150000 + (taxable_income - 1500000) * 0.30
    
    def calculate_new_post_2025_regime_tax(self, taxable_income):
        """Calculate tax as per new regime post 2025-26 budget"""
        # Assuming simplified slabs (example - actual budget may vary)
        if taxable_income <= 400000:
            return 0
        elif taxable_income <= 800000:
            return (taxable_income - 400000) * 0.05
        elif taxable_income <= 1200000:
            return 20000 + (taxable_income - 800000) * 0.10
        elif taxable_income <= 1600000:
            return 60000 + (taxable_income - 1200000) * 0.15
        elif taxable_income <= 2000000:
            return 120000 + (taxable_income - 1600000) * 0.20
        else:
            return 200000 + (taxable_income - 2000000) * 0.25
    
    def update_treeview(self, *args):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add new items
        components = [
            ("Basic Salary", args[0], args[1]),
            ("HRA", args[2], args[3]),
            ("Special Allowance", args[4], args[5]),
            ("Bonus/Ex Gratia", args[6], args[7]),
            ("Medical Insurance", args[8], args[9]),
            ("Other Allowances", args[10], args[11]),
            ("Employer PF Contribution", args[12], args[13]),
            ("Gratuity", args[14], args[15]),
            ("Professional Tax", args[16], args[17]),
            ("Income Tax", args[18], args[19]),
            ("In-Hand Salary", args[20], args[21])
        ]
        
        for component in components:
            self.tree.insert("", tk.END, values=(
                component[0],
                f"{component[1]:,.2f}",
                f"{component[2]:,.2f}"
            ))
    
    def share_results(self):
        if not self.tree.get_children():
            messagebox.showwarning("Warning", "Please calculate salary first")
            return
        
        result_text = "Salary Breakup:\n"
        result_text += f"{'Component':<25}{'Monthly (₹)':>15}{'Annual (₹)':>15}\n"
        result_text += "-" * 55 + "\n"
        
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            result_text += f"{values[0]:<25}{values[1]:>15}{values[2]:>15}\n"
        
        result_text += "\n"
        result_text += f"Monthly In-Hand Salary: ₹{self.in_hand_var.get():,.2f}\n"
        result_text += f"Annual In-Hand Salary: ₹{self.in_hand_var.get() * 12:,.2f}\n"
        
        # Show regime used
        regime = self.regime_var.get()
        regime_name = {
            "old": "Old Tax Regime",
            "new": "New Tax Regime (Current)",
            "new_post_2025": "New Tax Regime (Post 2025-26 Budget)"
        }.get(regime, "Unknown Regime")
        result_text += f"\nTax Calculation: {regime_name}\n"
        
        messagebox.showinfo("Salary Breakup", result_text)
    
    def reset_fields(self):
        # Reset all input fields
        self.basic_var.set(0)
        self.hra_var.set(0)
        self.special_allowance_var.set(0)
        self.bonus_var.set(0)
        self.pf_employer_var.set(0)
        self.gratuity_var.set(0)
        self.medical_var.set(0)
        self.other_allowances_var.set(0)
        self.regime_var.set("new")
        
        # Clear results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.in_hand_label.config(text="₹0")
    
    def show_formulas(self):
        formulas_text = """
        Salary Calculation Formulas:
        
        1. Basic Salary: Direct input (typically 40-50% of CTC)
        
        2. HRA: Direct input (typically 40-50% of Basic)
        
        3. Special Allowance: Direct input (balance amount after Basic and HRA)
        
        4. Employer PF Contribution: 12% of Basic Salary (₹15,000 max per month)
           Formula: min(12% of Basic, ₹15,000)
        
        5. Gratuity: (Basic Salary × 15/26) × Number of years of service
           (Simplified to direct input in this calculator)
        
        6. Professional Tax: ₹200/month (standard for most states)
        
        7. Standard Deduction: ₹50,000 (applied before tax calculation)
        
        8. HRA Exemption (Old Regime Only):
           Least of:
           - Actual HRA received
           - Rent paid - 10% of Basic Salary
           - 50% of Basic (metro) or 40% (non-metro)
        
        9. Tax Calculations:
        
           Old Regime:
           - Up to ₹2.5L: 0%
           - ₹2.5L-5L: 5%
           - ₹5L-10L: 20%
           - Above ₹10L: 30%
        
           New Regime (Current):
           - Up to ₹3L: 0%
           - ₹3L-6L: 5%
           - ₹6L-9L: 10%
           - ₹9L-12L: 15%
           - ₹12L-15L: 20%
           - Above ₹15L: 30%
        
           New Regime (Post 2025-26 Budget Projected):
           - Up to ₹4L: 0%
           - ₹4L-8L: 5%
           - ₹8L-12L: 10%
           - ₹12L-16L: 15%
           - ₹16L-20L: 20%
           - Above ₹20L: 25%
        
        10. Cess: 4% of income tax
        
        11. In-Hand Salary:
            Gross Salary - (Professional Tax + Income Tax + Employee PF)
        """
        messagebox.showinfo("Calculation Formulas", formulas_text)
    
    def show_help(self):
        help_text = """
        Indian Salary Calculator (Detailed) Help:
        
        1. Enter all your monthly salary components:
           - Basic Salary, HRA, Special Allowance
           - Employer PF Contribution
           - Other components like Bonus, Gratuity, Medical Insurance
        
        2. Select your preferred tax regime:
           - Old Regime (with all deductions)
           - New Regime (current)
           - New Regime (Post 2025-26 Budget) - projected
        
        3. Click 'Calculate Salary' to see detailed breakup
        
        4. The calculator will show:
           - Monthly and annual values for each component
           - All applicable deductions
           - Final in-hand salary
        
        5. Use 'Share Results' to get a text version of your salary breakup
        6. 'Reset' clears all fields for a new calculation
        7. 'Formulas' shows all calculation methods used
        
        Note: This calculator provides estimates based on standard Indian tax laws.
        Actual salary structure may vary based on company policies and location.
        """
        messagebox.showinfo("Help", help_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = IndianSalaryCalculator(root)
    root.mainloop()
