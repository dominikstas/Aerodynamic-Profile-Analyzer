import tkinter as tk
from tkinter import Toplevel, ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from calculations.aero_calculations import analyze_airfoil

class ProfileComparisonWindow:
    def __init__(self, master, naca_data, profile_info, colors):
        self.master = master
        self.naca_data = naca_data
        self.profile_info = profile_info
        self.colors = colors

        self.top = Toplevel(master)
        self.top.title("Compare Two Profiles")
        self.top.configure(bg=self.colors["background"])
        self.top.geometry("1000x700")

        self.profile1 = tk.StringVar()
        self.profile2 = tk.StringVar()
        self.air_speed = tk.DoubleVar(value=25.0)
        self.air_density = tk.DoubleVar(value=1.225)
        self.wing_area = tk.DoubleVar(value=12.0)

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.top, style="Card.TFrame")
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        control_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=10)
        control_frame.grid(row=0, column=0, sticky="nsw")

        profiles = list(self.naca_data.keys())

        ttk.Label(control_frame, text="Profile 1:", style="Card.TLabel").pack(anchor="w")
        ttk.Combobox(control_frame, textvariable=self.profile1, values=profiles, state="readonly").pack(fill="x", pady=5)

        ttk.Label(control_frame, text="Profile 2:", style="Card.TLabel").pack(anchor="w")
        ttk.Combobox(control_frame, textvariable=self.profile2, values=profiles, state="readonly").pack(fill="x", pady=5)

        ttk.Button(control_frame, text="Compare", command=self.compare_profiles, style="Action.TButton").pack(fill="x", pady=10)

        chart_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=10)
        chart_frame.grid(row=0, column=1, sticky="nsew")
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)

        self.figure = Figure(figsize=(6, 5), dpi=100, facecolor=self.colors["surface"])
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(self.colors["background"])
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def add_entry(self, parent, label, var):
        ttk.Label(parent, text=label, style="Card.TLabel").pack(anchor="w")
        entry = ttk.Entry(parent, textvariable=var)
        entry.pack(fill="x", pady=5)

    def compare_profiles(self):
        p1 = self.profile1.get()
        p2 = self.profile2.get()
        if not p1 or not p2:
            messagebox.showerror("Error", "Select both profiles")
            return

        try:
            alpha_range = self.naca_data[p1]["alpha"]
            V, rho, S = self.air_speed.get(), self.air_density.get(), self.wing_area.get()

            results1 = [analyze_airfoil(a, V, rho, S, p1, self.naca_data) for a in alpha_range]
            results2 = [analyze_airfoil(a, V, rho, S, p2, self.naca_data) for a in alpha_range]

            best1 = max(results1, key=lambda r: r["L_D_ratio"])
            best2 = max(results2, key=lambda r: r["L_D_ratio"])

            self.ax.clear()
            self.ax.grid(True, linestyle='--', alpha=0.3)
            self.ax.set_title("L/D Ratio Comparison", color=self.colors["text"])
            self.ax.set_xlabel("Angle of Attack [deg]", color=self.colors["text"])
            self.ax.set_ylabel("L/D Ratio", color=self.colors["text"])
            self.ax.tick_params(colors=self.colors["text"])

            self.ax.plot(alpha_range, [r["L_D_ratio"] for r in results1], label=f"{p1} (max @ {best1['alpha']:.1f}°)", color=self.colors["primary"])
            self.ax.plot(alpha_range, [r["L_D_ratio"] for r in results2], label=f"{p2} (max @ {best2['alpha']:.1f}°)", color=self.colors["secondary"])
            self.ax.legend()

            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Calculation Error", str(e))
