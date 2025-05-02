import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from naca_data import naca_data
import aero_calculations

class Airfoil:
    def __init__(self, root):
        self.root = root
        self.root.title("Analiza aerodynamiczna profilu skrzydła")
        self.root.geometry("900x650")
        self.root.minsize(900, 650)
        
        # Definicja kolorów - paleta granatowa
        self.colors = {
            "dark_navy": "#0A2463",  # Ciemny granat - główny kolor
            "medium_navy": "#1E5BA1", # Średni granat - akcenty
            "light_navy": "#5D9DE8",  # Jasny granat - podświetlenia
            "background": "#F0F5FC",  # Jasne tło
            "text": "#051336",        # Kolor tekstu
            "button": "#2471A3",      # Kolor przycisku
            "button_hover": "#1A5276" # Kolor przycisku po najechaniu
        }
        
        # Zmienne do przechowywania danych wejściowych
        self.selected_profile = tk.StringVar()
        self.angle_of_attack = tk.DoubleVar(value=0.0)
        self.air_speed = tk.DoubleVar(value=20.0)
        self.air_density = tk.DoubleVar(value=1.225)  # kg/m³ dla powietrza przy poziomie morza
        self.wing_area = tk.DoubleVar(value=10.0)  # m²
        self.chord_length = tk.DoubleVar(value=1.0)  # m
        self.kinematic_viscosity = tk.DoubleVar(value=1.48e-5)  # m²/s dla powietrza przy 20°C
        
        # Konfiguracja stylu
        self.configure_style()
        
        # Inicjalizacja interfejsu
        self.setup_ui()
    
    def configure_style(self):
        """Konfiguracja stylów dla elementów Tkinter"""
        style = ttk.Style()
        
        # Konfiguracja tła i kolorów
        self.root.configure(bg=self.colors["background"])
        style.configure("TFrame", background=self.colors["background"])
        style.configure("TLabel", background=self.colors["background"], foreground=self.colors["text"])
        style.configure("TLabelframe", background=self.colors["background"], foreground=self.colors["text"])
        style.configure("TLabelframe.Label", background=self.colors["background"], foreground=self.colors["dark_navy"], font=("Arial", 10, "bold"))
        
        # Konfiguracja przycisków
        style.configure("TButton", 
                        background=self.colors["button"], 
                        foreground="white", 
                        font=("Arial", 11, "bold"),
                        borderwidth=0,
                        padding=10)
        style.map("TButton",
                 background=[("active", self.colors["button_hover"])],
                 foreground=[("active", "white")])
        
        # Konfiguracja pól wejściowych
        style.configure("TEntry", 
                       fieldbackground="white", 
                       foreground=self.colors["text"],
                       borderwidth=1,
                       padding=5)
        
        # Konfiguracja ComboBox
        style.configure("TCombobox", 
                       background="white", 
                       foreground=self.colors["text"],
                       padding=5)
        
        # Konfiguracja ramki z nagłówkiem
        style.configure("NavyFrame.TFrame", 
                       background=self.colors["dark_navy"])
        
        # Styl dla paneli
        style.configure("Panel.TFrame", 
                       background="white", 
                       relief="raised",
                       borderwidth=0)
        
        # Styl dla elementów w panelach
        style.configure("Panel.TLabel", 
                       background="white", 
                       foreground=self.colors["text"])
        
        # Styl dla elementów LabelFrame w panelach
        style.configure("Panel.TLabelframe", 
                       background="white", 
                       foreground=self.colors["dark_navy"])
        style.configure("Panel.TLabelframe.Label", 
                       background="white", 
                       foreground=self.colors["dark_navy"],
                       font=("Arial", 10, "bold"))
        
    def setup_ui(self):
        """Konfiguracja interfejsu użytkownika"""
        # Górny nagłówek
        header_frame = ttk.Frame(self.root, style="NavyFrame.TFrame")
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        header_label = ttk.Label(header_frame, 
                                text="Analiza aerodynamiczna profilu skrzydła", 
                                foreground="white", 
                                background=self.colors["dark_navy"],
                                font=("Arial", 18, "bold"))
        header_label.pack(pady=15)
        
        # Główny kontener
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Lewy panel - kontrolki
        left_frame = ttk.Frame(main_frame, style="Panel.TFrame")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15), pady=0)
        
        # Dodajemy efekt cienia dla lewego panelu
        self.add_shadow_effect(left_frame)
        
        # Prawy panel - na wykresy
        right_frame = ttk.Frame(main_frame, style="Panel.TFrame")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Dodajemy efekt cienia dla prawego panelu
        self.add_shadow_effect(right_frame)
        
        # Wypełniamy lewy panel
        self.setup_control_panel(left_frame)
        
        # Wypełniamy prawy panel
        self.setup_chart_panel(right_frame)
    
    def add_shadow_effect(self, frame):
        """Dodaje efekt cienia do ramki"""
        shadow_frame = ttk.Frame(frame.master)
        shadow_frame.place(x=frame.winfo_x() + 3, y=frame.winfo_y() + 3, 
                          width=frame.winfo_width(), height=frame.winfo_height())
        shadow_frame.lower(frame)
        frame.update()
        
    def setup_control_panel(self, parent):
        """Konfiguracja panelu kontrolek"""
        # Wewnętrzny kontener dla odstępu
        inner_frame = ttk.Frame(parent, style="Panel.TFrame", padding=15)
        inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tytuł panelu
        panel_label = ttk.Label(inner_frame, 
                               text="Parametry analizy", 
                               style="Panel.TLabel",
                               font=("Arial", 14, "bold"))
        panel_label.pack(anchor="w", pady=(0, 15))
        
        # Sekcja wyboru profilu
        profile_frame = ttk.LabelFrame(inner_frame, 
                                      text="Wybór profilu", 
                                      style="Panel.TLabelframe",
                                      padding=15)
        profile_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(profile_frame, 
                 text="Profil NACA:", 
                 style="Panel.TLabel").pack(anchor="w")
        
        profile_combo = ttk.Combobox(profile_frame, 
                                    textvariable=self.selected_profile,
                                    values=list(naca_data.keys()),
                                    state="readonly",
                                    width=25)
        profile_combo.pack(fill=tk.X, pady=(5, 0))
        profile_combo.current(0)  # Domyślnie wybierz pierwszy profil
        
        # Sekcja parametrów
        params_frame = ttk.LabelFrame(inner_frame, 
                                     text="Parametry lotu", 
                                     style="Panel.TLabelframe",
                                     padding=15)
        params_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Kąt natarcia
        ttk.Label(params_frame, 
                 text="Kąt natarcia [°]:", 
                 style="Panel.TLabel").pack(anchor="w")
        angle_entry = ttk.Entry(params_frame, textvariable=self.angle_of_attack)
        angle_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Prędkość powietrza
        ttk.Label(params_frame, 
                 text="Prędkość powietrza [m/s]:", 
                 style="Panel.TLabel").pack(anchor="w")
        speed_entry = ttk.Entry(params_frame, textvariable=self.air_speed)
        speed_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Gęstość powietrza
        ttk.Label(params_frame, 
                 text="Gęstość powietrza [kg/m³]:", 
                 style="Panel.TLabel").pack(anchor="w")
        density_entry = ttk.Entry(params_frame, textvariable=self.air_density)
        density_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Powierzchnia skrzydła
        ttk.Label(params_frame, 
                 text="Powierzchnia skrzydła [m²]:", 
                 style="Panel.TLabel").pack(anchor="w")
        area_entry = ttk.Entry(params_frame, textvariable=self.wing_area)
        area_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Advanced parameters section
        advanced_frame = ttk.LabelFrame(inner_frame, 
                                     text="Parametry dodatkowe", 
                                     style="Panel.TLabelframe",
                                     padding=15)
        advanced_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Długość cięciwy
        ttk.Label(advanced_frame, 
                 text="Długość cięciwy [m]:", 
                 style="Panel.TLabel").pack(anchor="w")
        chord_entry = ttk.Entry(advanced_frame, textvariable=self.chord_length)
        chord_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Lepkość kinematyczna
        ttk.Label(advanced_frame, 
                 text="Lepkość kinematyczna [m²/s]:", 
                 style="Panel.TLabel").pack(anchor="w")
        viscosity_entry = ttk.Entry(advanced_frame, textvariable=self.kinematic_viscosity)
        viscosity_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Przycisk "Oblicz"
        calculate_button = ttk.Button(inner_frame, 
                                     text="OBLICZ", 
                                     command=self.calculate,
                                     width=25)
        calculate_button.pack(pady=(15, 0))
        
        # Przyciski eksportu
        export_frame = ttk.Frame(inner_frame, style="Panel.TFrame")
        export_frame.pack(fill=tk.X, pady=(15, 0))
        
        export_data_btn = ttk.Button(export_frame, 
                                   text="Eksportuj dane", 
                                   command=self.export_data,
                                   width=12)
        export_data_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        save_plot_btn = ttk.Button(export_frame, 
                                  text="Zapisz wykres", 
                                  command=self.save_plot,
                                  width=12)
        save_plot_btn.pack(side=tk.LEFT)

    def setup_chart_panel(self, parent):
        """Konfiguracja panelu z wykresem"""
        # Wewnętrzny kontener dla odstępu
        inner_frame = ttk.Frame(parent, style="Panel.TFrame", padding=15)
        inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tytuł panelu
        panel_label = ttk.Label(inner_frame, 
                               text="Wizualizacja danych", 
                               style="Panel.TLabel",
                               font=("Arial", 14, "bold"))
        panel_label.pack(anchor="w", pady=(0, 15))
        
        # Ramka na wykres
        chart_frame = ttk.Frame(inner_frame, style="Panel.TFrame")
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Inicjalizacja wykresu w stylu granatowym
        self.figure = Figure(figsize=(5, 4), dpi=100, facecolor='white')
        self.plot = self.figure.add_subplot(111)
        self.plot.set_title("Dane aerodynamiczne profilu", fontsize=12, color=self.colors["dark_navy"])
        self.plot.set_xlabel("Kąt natarcia [°]", fontsize=10, color=self.colors["text"])
        self.plot.set_ylabel("Współczynnik", fontsize=10, color=self.colors["text"])
        self.plot.grid(True, linestyle='--', alpha=0.7)
        self.plot.tick_params(colors=self.colors["text"])
        
        # Dostosowanie kolorów wykresu
        self.figure.patch.set_facecolor('white')
        self.plot.set_facecolor('#F8FBFF')  # Bardzo jasny odcień niebieskiego
        
        # Utworzenie przykładowego wykresu
        self.plot.plot([-10, -5, 0, 5, 10, 15, 20], 
                      [-0.6, -0.1, 0.4, 0.9, 1.3, 1.5, 1.2], 
                      marker='o', color=self.colors["medium_navy"], 
                      label="CL (przykład)")
        self.plot.plot([-10, -5, 0, 5, 10, 15, 20], 
                      [0.035, 0.012, 0.008, 0.012, 0.035, 0.068, 0.12], 
                      marker='s', color=self.colors["light_navy"], 
                      label="CD (przykład)")
        self.plot.legend()
        
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Dodanie toolbar'a Matplotlib
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar_frame = ttk.Frame(inner_frame, style="Panel.TFrame")
        toolbar_frame.pack(fill=tk.X, pady=(5, 15))
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
        # Panel informacyjny pod wykresem
        info_frame = ttk.Frame(inner_frame, style="Panel.TFrame")
        info_frame.pack(fill=tk.X, pady=(0, 0))
        
        info_label = ttk.Label(info_frame, 
                              text="Wybierz profil i parametry, a następnie kliknij 'OBLICZ' aby zobaczyć wyniki.", 
                              style="Panel.TLabel",
                              foreground=self.colors["medium_navy"],
                              font=("Arial", 10, "italic"))
        info_label.pack(anchor="w")
        
    def validate_inputs(self):
        """Validate user inputs before calculations"""
        try:
            angle = self.angle_of_attack.get()
            speed = self.air_speed.get()
            density = self.air_density.get()
            area = self.wing_area.get()
            
            # Check for valid ranges
            if not (-20 <= angle <= 30):
                return False, "Kąt natarcia powinien być w zakresie od -20° do 30°"
            if speed <= 0:
                return False, "Prędkość powietrza musi być większa niż zero"
            if density <= 0:
                return False, "Gęstość powietrza musi być większa niż zero"
            if area <= 0:
                return False, "Powierzchnia skrzydła musi być większa niż zero"
                
            return True, ""
        except tk.TclError:
            return False, "Wprowadź poprawne wartości liczbowe"
            
    def calculate(self):
        """Metoda wywoływana po kliknięciu przycisku 'Oblicz'"""
        # Walidacja danych wejściowych
        valid, error_msg = self.validate_inputs()
        if not valid:
            messagebox.showerror("Błąd", error_msg)
            return
            
        profile = self.selected_profile.get()
        angle = self.angle_of_attack.get()
        speed = self.air_speed.get()
        density = self.air_density.get()
        area = self.wing_area.get()
        chord = self.chord_length.get()
        viscosity = self.kinematic_viscosity.get()
        
        # Use the aerodynamic calculations module
        results = aero_calculations.analyze_airfoil(
            alpha=angle,
            V=speed,
            rho=density,
            S=area,
            profile_name=profile,
            profiles_data=naca_data
        )
        
        # Calculate Reynolds number
        reynolds = aero_calculations.calculate_reynolds_number(speed, chord, viscosity)
        results["reynolds"] = reynolds
        
        # Store results for possible export
        self.last_results = results
        
        # Print results to console (optional)
        print(f"Analiza dla profilu: {results['profile']}")
        print(f"Siła nośna: {results['lift']:.2f} N")
        print(f"Opór: {results['drag']:.2f} N")
        print(f"Współczynnik L/D: {results['L_D_ratio']:.2f}")
        print(f"Liczba Reynoldsa: {reynolds:.2e}")
        
        # Aktualizacja wykresu z danymi wybranego profilu i wynikami
        self.update_plot(profile, results)
    
    def update_plot(self, profile, results=None):
        """Aktualizuje wykres danymi wybranego profilu i wynikami obliczeń"""
        # Czyszczenie wykresu
        self.plot.clear()
        
        # Konfiguracja wykresu
        self.plot.set_title(f"Profil: {profile}", fontsize=12, color=self.colors["dark_navy"])
        self.plot.set_xlabel("Kąt natarcia [°]", fontsize=10, color=self.colors["text"])
        self.plot.set_ylabel("Współczynnik", fontsize=10, color=self.colors["text"])
        self.plot.grid(True, linestyle='--', alpha=0.7)
        self.plot.set_facecolor('#F8FBFF')
        
        # Pobieranie danych wybranego profilu
        profile_data = naca_data[profile]
        
        # Rysowanie danych
        self.plot.plot(profile_data["alpha"], profile_data["CL"], 
                    marker='o', color=self.colors["medium_navy"], 
                    label="CL", linewidth=2)
        self.plot.plot(profile_data["alpha"], profile_data["CD"], 
                    marker='s', color=self.colors["light_navy"], 
                    label="CD", linewidth=2)
        
        # Zapisanie danych do użycia w tooltipach
        self.plot_data = {
            'x': profile_data["alpha"],
            'cl': profile_data["CL"],
            'cd': profile_data["CD"]
        }
        
        # Jeśli mamy wyniki obliczeń, zaznaczamy aktualny punkt na wykresie
        if results:
            # Zaznaczenie aktualnego punktu dla CL
            self.plot.scatter([results["alpha"]], [results["CL"]], 
                            s=100, color='red', marker='o', 
                            label=f"CL={results['CL']:.3f}")
            
            # Zaznaczenie aktualnego punktu dla CD
            self.plot.scatter([results["alpha"]], [results["CD"]], 
                            s=100, color='red', marker='s', 
                            label=f"CD={results['CD']:.3f}")
            
            # Dodanie informacji o siłach i stosunku L/D na wykresie
            info_text = f"Siła nośna: {results['lift']:.1f} N\n"
            info_text += f"Opór: {results['drag']:.1f} N\n"
            info_text += f"L/D: {results['L_D_ratio']:.2f}\n"
            info_text += f"Reynolds: {results['reynolds']:.2e}"
            
            # Dodanie tekstowych informacji w rogu wykresu
            self.plot.text(0.02, 0.98, info_text,
                        transform=self.plot.transAxes,
                        fontsize=9,
                        verticalalignment='top',
                        bbox=dict(boxstyle='round', 
                                  facecolor='white', 
                                  alpha=0.8))
        
        # Dodanie legendy
        self.plot.legend()
        
        # Odświeżenie wykresu
        self.canvas.draw()
        
    def export_data(self):
        """Export calculation results to CSV file"""
        from tkinter import filedialog
        import csv
        
        if not hasattr(self, 'last_results'):
            messagebox.showinfo("Informacja", "Brak danych do eksportu. Wykonaj najpierw obliczenia.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Zapisz dane jako CSV"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Parametr", "Wartość", "Jednostka"])
                writer.writerow(["Profil", self.last_results['profile'], ""])
                writer.writerow(["Kąt natarcia", self.last_results['alpha'], "°"])
                writer.writerow(["Prędkość powietrza", self.air_speed.get(), "m/s"])
                writer.writerow(["Gęstość powietrza", self.air_density.get(), "kg/m³"])
                writer.writerow(["Powierzchnia skrzydła", self.wing_area.get(), "m²"])
                writer.writerow(["Długość cięciwy", self.chord_length.get(), "m"])
                writer.writerow(["Lepkość kinematyczna", self.kinematic_viscosity.get(), "m²/s"])
                writer.writerow(["Współczynnik siły nośnej (CL)", self.last_results['CL'], ""])
                writer.writerow(["Współczynnik oporu (CD)", self.last_results['CD'], ""])
                writer.writerow(["Siła nośna", self.last_results['lift'], "N"])
                writer.writerow(["Opór", self.last_results['drag'], "N"])
                writer.writerow(["Współczynnik L/D", self.last_results['L_D_ratio'], ""])
                writer.writerow(["Liczba Reynoldsa", self.last_results['reynolds'], ""])
                
            messagebox.showinfo("Sukces", f"Dane zostały zapisane do pliku:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas zapisu pliku:\n{str(e)}")
        
    def save_plot(self):
        """Save current plot as image file"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Zapisz wykres jako obrazek"
        )
        
        if not file_path:
            return
            
        try:
            self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Sukces", f"Wykres został zapisany do pliku:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas zapisu wykresu:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Airfoil(root)
    root.mainloop()