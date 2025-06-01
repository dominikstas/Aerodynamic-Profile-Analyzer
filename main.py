import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
# from naca_data import naca_data  # Profile data from external file
import aero_calculations

# Sample data for testing (replace with actual naca_data import)
naca_data = {
    "NACA 2412": {
        "alpha": [-10, -5, 0, 5, 10, 15, 20],
        "CL": [-0.6, -0.1, 0.4, 0.9, 1.3, 1.5, 1.2],
        "CD": [0.035, 0.012, 0.008, 0.012, 0.035, 0.068, 0.12]
    },
    "NACA 4412": {
        "alpha": [-10, -5, 0, 5, 10, 15, 20],
        "CL": [-0.5, 0.1, 0.6, 1.1, 1.5, 1.7, 1.4],
        "CD": [0.04, 0.015, 0.01, 0.015, 0.04, 0.075, 0.13]
    }
}

class Airfoil:
    def __init__(self, root):
        self.root = root
        self.root.title("Analiza aerodynamiczna profilu skrzydła")
        
        # Responsive window sizing
        self.setup_window()
        
        # Color scheme
        self.colors = {
            "primary": "#1E3A8A",      # Deep blue
            "secondary": "#3B82F6",     # Medium blue
            "accent": "#60A5FA",        # Light blue
            "background": "#F8FAFC",    # Very light gray-blue
            "surface": "#FFFFFF",       # White
            "text": "#1E293B",          # Dark gray
            "text_light": "#475569"     # Medium gray
        }
        
        # Variables
        self.init_variables()
        
        # Setup UI
        self.configure_styles()
        self.create_interface()
    
    def setup_window(self):
        """Configure responsive window settings"""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate responsive dimensions (80% of screen, with limits)
        window_width = min(max(int(screen_width * 0.8), 900), 1400)
        window_height = min(max(int(screen_height * 0.8), 650), 900)
        
        # Center window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(900, 650)
        
        # Configure grid weights for responsive layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def init_variables(self):
        """Initialize input variables with default values"""
        self.selected_profile = tk.StringVar(value=list(naca_data.keys())[0])
        self.angle_of_attack = tk.DoubleVar(value=0.0)
        self.air_speed = tk.DoubleVar(value=20.0)
        self.air_density = tk.DoubleVar(value=1.225)
        self.wing_area = tk.DoubleVar(value=10.0)
        self.chord_length = tk.DoubleVar(value=1.0)
        self.kinematic_viscosity = tk.DoubleVar(value=1.48e-5)
    
    def configure_styles(self):
        """Configure ttk styles"""
        self.root.configure(bg=self.colors["background"])
        
        style = ttk.Style()
        
        # Configure main styles
        style.configure("TFrame", background=self.colors["background"])
        style.configure("TLabel", background=self.colors["background"], 
                       foreground=self.colors["text"])
        style.configure("TLabelframe", background=self.colors["background"], 
                       foreground=self.colors["text"])
        style.configure("TLabelframe.Label", background=self.colors["background"], 
                       foreground=self.colors["primary"], font=("Arial", 10, "bold"))
        
        # Surface (panel) styles
        style.configure("Surface.TFrame", background=self.colors["surface"], 
                       relief="solid", borderwidth=1)
        style.configure("Surface.TLabel", background=self.colors["surface"], 
                       foreground=self.colors["text"])
        style.configure("Surface.TLabelframe", background=self.colors["surface"])
        style.configure("Surface.TLabelframe.Label", background=self.colors["surface"], 
                       foreground=self.colors["primary"], font=("Arial", 10, "bold"))
        
        # Header style
        style.configure("Header.TFrame", background=self.colors["primary"])
        style.configure("Header.TLabel", background=self.colors["primary"], 
                       foreground="white", font=("Arial", 16, "bold"))
        
        # Button styles - Simplified and more reliable
        style.configure("Calculate.TButton", 
                       font=("Arial", 12, "bold"),
                       padding=(10, 8),
                       width=20)
        
        # Input styles
        style.configure("TEntry", fieldbackground="white", 
                       foreground=self.colors["text"], padding=5)
        style.configure("TCombobox", fieldbackground="white", 
                       foreground=self.colors["text"], padding=5)
    
    def create_interface(self):
        """Create the main interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Header
        self.create_header(main_frame)
        
        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Left panel (controls)
        self.create_control_panel(content_frame)
        
        # Right panel (chart)
        self.create_chart_panel(content_frame)
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = ttk.Frame(parent, style="Header.TFrame")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        ttk.Label(header_frame, text="Analiza aerodynamiczna profilu skrzydła", 
                 style="Header.TLabel").pack(pady=15)
    
    def create_control_panel(self, parent):
        """Create left control panel"""
        # Main control frame with fixed width to prevent layout issues
        control_frame = ttk.Frame(parent, style="Surface.TFrame", padding=15, width=300)
        control_frame.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        control_frame.grid_propagate(False)  # Prevent frame from shrinking
        
        # Panel title
        ttk.Label(control_frame, text="Parametry analizy", 
                 style="Surface.TLabel", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 15))
        
        # Profile selection
        profile_frame = ttk.LabelFrame(control_frame, text="Wybór profilu", 
                                     style="Surface.TLabelframe", padding=10)
        profile_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(profile_frame, text="Profil NACA:", 
                 style="Surface.TLabel").pack(anchor="w", pady=(0, 5))
        profile_combo = ttk.Combobox(profile_frame, textvariable=self.selected_profile,
                                   values=list(naca_data.keys()), state="readonly")
        profile_combo.pack(fill="x")
        
        # Flight parameters
        params_frame = ttk.LabelFrame(control_frame, text="Parametry lotu", 
                                    style="Surface.TLabelframe", padding=10)
        params_frame.pack(fill="x", pady=(0, 15))
        
        # Create parameter inputs with consistent spacing
        self.create_parameter_input(params_frame, "Kąt natarcia [°]:", self.angle_of_attack)
        self.create_parameter_input(params_frame, "Prędkość [m/s]:", self.air_speed)
        self.create_parameter_input(params_frame, "Gęstość powietrza [kg/m³]:", self.air_density)
        self.create_parameter_input(params_frame, "Powierzchnia skrzydła [m²]:", self.wing_area)
        
        # Calculate button with explicit styling
        calculate_btn = ttk.Button(control_frame, text="OBLICZ", 
                                 command=self.calculate, style="Calculate.TButton")
        calculate_btn.pack(fill="x", pady=(15, 15))
        
        # Export buttons frame
        export_frame = ttk.Frame(control_frame, style="Surface.TFrame")
        export_frame.pack(fill="x")
        
        # Export buttons with consistent sizing
        ttk.Button(export_frame, text="Eksportuj dane", 
                  command=self.export_data, width=12).pack(side="left", padx=(0, 5))
        ttk.Button(export_frame, text="Zapisz wykres", 
                  command=self.save_plot, width=12).pack(side="left")
    
    def create_parameter_input(self, parent, label_text, variable):
        """Create a labeled input field with consistent spacing"""
        ttk.Label(parent, text=label_text, style="Surface.TLabel").pack(anchor="w", pady=(0, 3))
        entry = ttk.Entry(parent, textvariable=variable)
        entry.pack(fill="x", pady=(0, 10))
        return entry
    
    def create_chart_panel(self, parent):
        """Create right chart panel"""
        chart_frame = ttk.Frame(parent, style="Surface.TFrame", padding=20)
        chart_frame.grid(row=0, column=1, sticky="nsew")
        chart_frame.grid_rowconfigure(1, weight=1)
        chart_frame.grid_columnconfigure(0, weight=1)
        
        # Panel title
        ttk.Label(chart_frame, text="Wizualizacja danych", 
                 style="Surface.TLabel", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        # Chart container
        plot_frame = ttk.Frame(chart_frame, style="Surface.TFrame")
        plot_frame.grid(row=1, column=0, sticky="nsew")
        
        # Initialize matplotlib figure
        self.setup_chart(plot_frame)
        
        # Commented out toolbar for now (can be restored later)
        # toolbar_frame = ttk.Frame(chart_frame, style="Surface.TFrame")
        # toolbar_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        # from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        # self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        # self.toolbar.update()
        
        # Info label
        info_label = ttk.Label(chart_frame, 
                              text="Wybierz profil i parametry, następnie kliknij 'OBLICZ'.", 
                              style="Surface.TLabel", foreground=self.colors["text_light"],
                              font=("Arial", 10, "italic"))
        info_label.grid(row=3, column=0, sticky="w", pady=(15, 0))
    
    def setup_chart(self, parent):
        """Initialize the matplotlib chart"""
        self.figure = Figure(figsize=(6, 4), dpi=100, facecolor=self.colors["surface"])
        self.plot = self.figure.add_subplot(111)
        
        # Configure plot appearance
        self.plot.set_title("Dane aerodynamiczne profilu", 
                           fontsize=12, color=self.colors["primary"], pad=20)
        self.plot.set_xlabel("Kąt natarcia [°]", fontsize=10, color=self.colors["text"])
        self.plot.set_ylabel("Współczynnik", fontsize=10, color=self.colors["text"])
        self.plot.grid(True, linestyle='--', alpha=0.3)
        self.plot.set_facecolor('#FAFBFC')
        
        # Create sample plot
        sample_angles = [-10, -5, 0, 5, 10, 15, 20]
        sample_cl = [-0.6, -0.1, 0.4, 0.9, 1.3, 1.5, 1.2]
        sample_cd = [0.035, 0.012, 0.008, 0.012, 0.035, 0.068, 0.12]
        
        self.plot.plot(sample_angles, sample_cl, 'o-', color=self.colors["primary"], 
                      label="CL (przykład)", linewidth=2, markersize=6)
        self.plot.plot(sample_angles, sample_cd, 's-', color=self.colors["secondary"], 
                      label="CD (przykład)", linewidth=2, markersize=6)
        self.plot.legend()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def validate_inputs(self):
        """Validate user inputs"""
        try:
            angle = self.angle_of_attack.get()
            speed = self.air_speed.get()
            density = self.air_density.get()
            area = self.wing_area.get()
            
            if not (-20 <= angle <= 30):
                return False, "Kąt natarcia: -20° do 30°"
            if speed <= 0:
                return False, "Prędkość musi być > 0"
            if density <= 0:
                return False, "Gęstość musi być > 0"
            if area <= 0:
                return False, "Powierzchnia musi być > 0"
                
            return True, ""
        except tk.TclError:
            return False, "Wprowadź poprawne wartości liczbowe"
    
    def calculate(self):
        """Perform aerodynamic calculations"""
        # Validate inputs
        valid, error_msg = self.validate_inputs()
        if not valid:
            messagebox.showerror("Błąd", error_msg)
            return
        
        # Get parameters
        profile = self.selected_profile.get()
        angle = self.angle_of_attack.get()
        speed = self.air_speed.get()
        density = self.air_density.get()
        area = self.wing_area.get()
        
        try:
            # Perform analysis
            results = aero_calculations.analyze_airfoil(
                alpha=angle, V=speed, rho=density, S=area,
                profile_name=profile, profiles_data=naca_data
            )
            
            # Store results
            self.last_results = results
            
            # Update plot
            self.update_plot(profile, results)
            
            print(f"Analiza: {results['profile']}")
            print(f"Siła nośna: {results['lift']:.2f} N")
            print(f"Opór: {results['drag']:.2f} N")
            print(f"L/D: {results['L_D_ratio']:.2f}")
            
        except Exception as e:
            messagebox.showerror("Błąd obliczeń", str(e))
    
    def update_plot(self, profile, results=None):
        """Update plot with profile data and results"""
        self.plot.clear()
        
        # Configure plot
        self.plot.set_title(f"Profil: {profile}", 
                           fontsize=12, color=self.colors["primary"], pad=20)
        self.plot.set_xlabel("Kąt natarcia [°]", fontsize=10, color=self.colors["text"])
        self.plot.set_ylabel("Współczynnik", fontsize=10, color=self.colors["text"])
        self.plot.grid(True, linestyle='--', alpha=0.3)
        self.plot.set_facecolor('#FAFBFC')
        
        # Plot profile data
        profile_data = naca_data[profile]
        self.plot.plot(profile_data["alpha"], profile_data["CL"], 'o-', 
                      color=self.colors["primary"], label="CL", linewidth=2, markersize=6)
        self.plot.plot(profile_data["alpha"], profile_data["CD"], 's-', 
                      color=self.colors["secondary"], label="CD", linewidth=2, markersize=6)
        
        # Highlight current point if results available
        if results:
            self.plot.scatter([results["alpha"]], [results["CL"]], 
                            s=120, color='red', marker='o', zorder=5,
                            label=f"CL={results['CL']:.3f}")
            self.plot.scatter([results["alpha"]], [results["CD"]], 
                            s=120, color='red', marker='s', zorder=5,
                            label=f"CD={results['CD']:.3f}")
            
            # Add results text
            info_text = (f"Siła nośna: {results['lift']:.1f} N\n"
                        f"Opór: {results['drag']:.1f} N\n"
                        f"L/D: {results['L_D_ratio']:.2f}")
            
            self.plot.text(0.02, 0.98, info_text, transform=self.plot.transAxes,
                          fontsize=9, verticalalignment='top',
                          bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
        
        self.plot.legend()
        self.canvas.draw()
    
    def export_data(self):
        """Export results to CSV"""
        if not hasattr(self, 'last_results'):
            messagebox.showinfo("Info", "Brak danych. Wykonaj obliczenia.")
            return
        
        from tkinter import filedialog
        import csv
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
            title="Zapisz dane jako CSV")
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Parametr", "Wartość", "Jednostka"])
                results = self.last_results
                writer.writerows([
                    ["Profil", results['profile'], ""],
                    ["Kąt natarcia", results['alpha'], "°"],
                    ["Prędkość", self.air_speed.get(), "m/s"],
                    ["Gęstość", self.air_density.get(), "kg/m³"],
                    ["Powierzchnia", self.wing_area.get(), "m²"],
                    ["CL", results['CL'], ""],
                    ["CD", results['CD'], ""],
                    ["Siła nośna", results['lift'], "N"],
                    ["Opór", results['drag'], "N"],
                    ["L/D", results['L_D_ratio'], ""]
                ])
            messagebox.showinfo("Sukces", f"Zapisano: {file_path}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd zapisu: {e}")
    
    def save_plot(self):
        """Save current plot as image"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png", 
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("PDF files", "*.pdf")],
            title="Zapisz wykres")
        
        if not file_path:
            return
        
        try:
            self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Sukces", f"Zapisano: {file_path}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd zapisu: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Airfoil(root)
    root.mainloop()