import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from calculations.naca_data import naca_data, profile_info
from calculations.aero_calculations import analyze_airfoil
from calculations.profile_manager import ProfileManager
from gui.compare_profiles import ProfileComparisonWindow

class AirfoilGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Aerodynamic Profile Analyzer")

        self.colors = {
            "primary": "#1E3A8A",
            "secondary": "#10B981",
            "accent": "#60A5FA",
            "background": "#0F172A",
            "surface": "#0F172A",
            "text": "#F1F5F9",
            "text_light": "#94A3B8"
        }

        self.setup_window()
        self.init_variables()
        self.profile_manager = ProfileManager(naca_data, profile_info)
        self.configure_styles()
        self.create_interface()

    def setup_window(self):
        screen_w, screen_h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        window_w, window_h = int(screen_w * 0.85), int(screen_h * 0.85)
        self.root.geometry(f"{window_w}x{window_h}+{(screen_w-window_w)//2}+{(screen_h-window_h)//2}")
        self.root.minsize(1000, 700)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.configure(bg=self.colors["background"])

    def init_variables(self):
        profiles = list(naca_data.keys())
        self.selected_profile = tk.StringVar(value=profiles[0])
        self.angle_of_attack = tk.DoubleVar(value=5.0)
        self.air_speed = tk.DoubleVar(value=25.0)
        self.air_density = tk.DoubleVar(value=1.225)
        self.wing_area = tk.DoubleVar(value=12.0)
        self.last_results = None

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure("TFrame", background=self.colors["background"])
        style.configure("TLabel", background=self.colors["background"], foreground=self.colors["text"])

        style.configure("Card.TFrame", background=self.colors["background"])
        style.configure("Card.TLabel", background=self.colors["background"], foreground=self.colors["text"])
        style.configure("Card.TLabelframe", background=self.colors["background"], relief="flat")
        style.configure("Card.TLabelframe.Label", background=self.colors["background"], foreground=self.colors["accent"], font=("Segoe UI", 10, "bold"))

        style.configure("Header.TFrame", background=self.colors["primary"])
        style.configure("Header.TLabel", background=self.colors["primary"], foreground="white", font=("Segoe UI", 16, "bold"))

        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), background=self.colors["primary"], foreground="white", padding=6)
        style.map("Action.TButton", background=[('active', '#1D4ED8')], foreground=[('active', 'white')])

        style.configure("Secondary.TButton", font=("Segoe UI", 9), background="#334155", foreground=self.colors["text"], padding=5)
        style.map("Secondary.TButton", background=[('active', '#475569')], foreground=[('active', self.colors["text"])])

        style.configure("Accent.TButton", font=("Segoe UI", 9), background=self.colors["accent"], foreground="black", padding=5)
        style.map("Accent.TButton", background=[('active', '#3B82F6')], foreground=[('active', 'white')])

    def create_interface(self):
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        self.create_header(main_frame)

        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        self.create_control_panel(content_frame)
        self.create_chart_panel(content_frame)

    def create_header(self, parent):
        header = ttk.Frame(parent, style="Header.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Label(header, text="Aerodynamic Profile Analyzer", style="Header.TLabel").pack(pady=12)

    def create_control_panel(self, parent):
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=0, column=0, sticky="nsw", padx=(0, 10))
        control_frame.configure(width=300)

        profile_frame = ttk.LabelFrame(control_frame, text="NACA Profile", style="Card.TLabelframe", padding=10)
        profile_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(profile_frame, text="Select profile:", style="Card.TLabel").pack(anchor="w", pady=(0, 5))
        profile_combo = ttk.Combobox(profile_frame, textvariable=self.selected_profile, values=list(naca_data.keys()), state="readonly")
        profile_combo.pack(fill="x", pady=(0, 8))
        profile_combo.bind('<<ComboboxSelected>>', self.on_profile_change)

        open_btn = ttk.Button(profile_frame, text="📂 Open", command=self.add_custom_profile, style="Accent.TButton")
        open_btn.pack(fill="x", pady=(0, 5))

        self.profile_desc = ttk.Label(profile_frame, text="", style="Card.TLabel", font=("Segoe UI", 8), foreground=self.colors["text_light"], wraplength=240)
        self.profile_desc.pack(anchor="w")
        self.update_profile_description()

        params_frame = ttk.LabelFrame(control_frame, text="Flight Parameters", style="Card.TLabelframe", padding=10)
        params_frame.pack(fill="x", pady=(0, 15))
        self.create_parameter_input(params_frame, "Angle of attack [°]:", self.angle_of_attack, (-20, 30))
        self.create_parameter_input(params_frame, "Air speed [m/s]:", self.air_speed, (1, 200))
        self.create_parameter_input(params_frame, "Air density [kg/m³]:", self.air_density, (0.1, 5.0))
        self.create_parameter_input(params_frame, "Wing area [m²]:", self.wing_area, (0.1, 1000))

        analyze_btn = ttk.Button(control_frame, text="🔬 ANALYZE", command=self.perform_analysis, style="Action.TButton")
        analyze_btn.pack(fill="x", pady=(10, 5))

    def create_parameter_input(self, parent, label, variable, limits):
        ttk.Label(parent, text=label, style="Card.TLabel").pack(anchor="w", pady=(0, 2))
        entry = ttk.Entry(parent, textvariable=variable)
        entry.pack(fill="x", pady=(0, 8))
        entry.bind('<FocusOut>', lambda e: self.validate_range(variable, limits))

    def create_chart_panel(self, parent):
        chart_frame = ttk.Frame(parent)
        chart_frame.grid(row=0, column=1, sticky="nsew")
        chart_frame.grid_rowconfigure(1, weight=1)
        chart_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(chart_frame, text="Aerodynamic Characteristics", font=("Segoe UI", 14, "bold"), style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 15))

        plot_container = ttk.Frame(chart_frame)
        plot_container.grid(row=1, column=0, sticky="nsew")
        plot_container.grid_rowconfigure(0, weight=1)
        plot_container.grid_columnconfigure(0, weight=1)

        self.figure = Figure(figsize=(7, 5), dpi=100, facecolor=self.colors["background"])
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(self.colors["background"])
        self.canvas = FigureCanvasTkAgg(self.figure, plot_container)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        toolbar_frame = ttk.Frame(plot_container)
        toolbar_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

        bottom_btn_frame = ttk.Frame(chart_frame)
        bottom_btn_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))

        reset_btn = ttk.Button(bottom_btn_frame, text="Reset", command=self.reset_parameters, style="Secondary.TButton")
        reset_btn.pack(side="left", padx=5)

        compare_btn = ttk.Button(bottom_btn_frame, text="Comparision mode", command=self.open_comparison_window, style="Action.TButton")
        compare_btn.pack(side="left", padx=5)

        self.status_label = ttk.Label(chart_frame, text="Select parameters and click 'ANALYZE'", style="Card.TLabel", foreground=self.colors["text_light"], font=("Segoe UI", 9, "italic"))
        self.status_label.grid(row=2, column=0, sticky="w", pady=(15, 0))

        self.plot_initial_data()
    def plot_initial_data(self):
        profile = self.selected_profile.get()
        data = naca_data[profile]
        self.ax.clear()
        self.ax.set_title(f"Profile: {profile}", fontsize=12, pad=15, color=self.colors["text"])
        self.ax.set_xlabel("Angle of attack [°]", fontsize=11, color=self.colors["text"])
        self.ax.set_ylabel("Coefficient", fontsize=11, color=self.colors["text"])
        self.ax.tick_params(colors=self.colors["text"])
        self.ax.grid(True, linestyle='--', alpha=0.4)
        self.ax.plot(data["alpha"], data["CL"], 'o-', color=self.colors["primary"], label="CL", linewidth=2)
        self.ax.plot(data["alpha"], data["CD"], 's-', color=self.colors["secondary"], label="CD", linewidth=2)
        self.ax.legend()
        self.canvas.draw()

    def update_profile_description(self):
        desc = profile_info.get(self.selected_profile.get(), "No description available")
        self.profile_desc.config(text=desc)

    def on_profile_change(self, event=None):
        self.update_profile_description()
        self.plot_initial_data()

    def validate_range(self, variable, limits):
        try:
            value = variable.get()
            min_val, max_val = limits
            if not (min_val <= value <= max_val):
                messagebox.showwarning("Value out of range", f"Value must be between {min_val} and {max_val}")
        except tk.TclError:
            messagebox.showerror("Invalid value", "Enter a valid number")

    def perform_analysis(self):
        if not self.validate_all_inputs(): return
        try:
            results = analyze_airfoil(alpha=self.angle_of_attack.get(), V=self.air_speed.get(), rho=self.air_density.get(), S=self.wing_area.get(), profile_name=self.selected_profile.get(), profiles_data=naca_data)
            self.last_results = results
            self.update_plot_with_results(results)
            self.status_label.config(text=f"✅ L/D: {results['L_D_ratio']:.2f}, Lift: {results['lift']:.1f} N")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def validate_all_inputs(self):
        limits = [(self.angle_of_attack, (-10, 20)), (self.air_speed, (1, 200)), (self.air_density, (0.1, 5.0)), (self.wing_area, (0.1, 1000))]
        for var, rng in limits:
            try:
                val = var.get()
                if not (rng[0] <= val <= rng[1]): return False
            except: return False
        return True

    def update_plot_with_results(self, results):
        profile = results["profile"]
        data = naca_data[profile]
        self.ax.clear()
        self.ax.set_title(f"Analysis: {profile}", fontsize=12, pad=15, color=self.colors["text"])
        self.ax.set_xlabel("Angle of attack [°]", fontsize=11, color=self.colors["text"])
        self.ax.set_ylabel("Coefficient", fontsize=11, color=self.colors["text"])
        self.ax.tick_params(colors=self.colors["text"])
        self.ax.grid(True, linestyle='--', alpha=0.4)
        self.ax.plot(data["alpha"], data["CL"], 'o-', color=self.colors["primary"], label="CL", linewidth=2)
        self.ax.plot(data["alpha"], data["CD"], 's-', color=self.colors["secondary"], label="CD", linewidth=2)
        self.ax.scatter([results["alpha"]], [results["CL"]], s=100, color='red', marker='o', label=f"CL={results['CL']:.3f}")
        self.ax.scatter([results["alpha"]], [results["CD"]], s=100, color='red', marker='s')
        self.ax.text(0.02, 0.98, f"Lift: {results['lift']:.1f} N\nDrag: {results['drag']:.1f} N\nL/D: {results['L_D_ratio']:.2f}", transform=self.ax.transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
        self.ax.legend()
        self.canvas.draw()

    def reset_parameters(self):
        self.selected_profile.set(list(naca_data.keys())[0])
        self.angle_of_attack.set(5.0)
        self.air_speed.set(25.0)
        self.air_density.set(1.225)
        self.wing_area.set(12.0)
        self.update_profile_description()
        self.plot_initial_data()
        self.status_label.config(text="Parameters reset")

    def add_custom_profile(self):
        success, result = self.profile_manager.load_profile_from_file()
        if success:
            self.selected_profile.set(result)
            self.update_profile_description()
            self.plot_initial_data()
            messagebox.showinfo("Success", f"Profile '{result}' added.")
        else:
            messagebox.showerror("Error", result)

    def open_comparison_window(self):
        ProfileComparisonWindow(self.root, naca_data, profile_info, self.colors)
