import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from naca_data import naca_data

class Airfoil:
    def __init__(self, root):
        self.root = root
        self.root.title("Analiza aerodynamiczna profilu skrzydła")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Zmienne do przechowywania danych wejściowych
        self.selected_profile = tk.StringVar()
        self.angle_of_attack = tk.DoubleVar(value=0.0)
        self.air_speed = tk.DoubleVar(value=20.0)
        self.air_density = tk.DoubleVar(value=1.225)  # kg/m³ dla powietrza przy poziomie morza
        self.wing_area = tk.DoubleVar(value=10.0)  # m²
        
        # Inicjalizacja interfejsu
        self.setup_ui()
        
    def setup_ui(self):
        """Konfiguracja interfejsu użytkownika"""
        # Główny kontener
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lewy panel - kontrolki
        left_frame = ttk.Frame(main_frame, padding="10", relief="ridge", borderwidth=2)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Prawy panel - na wykresy
        right_frame = ttk.Frame(main_frame, padding="10", relief="ridge", borderwidth=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Sekcja wyboru profilu
        profile_frame = ttk.LabelFrame(left_frame, text="Wybór profilu", padding="10")
        profile_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(profile_frame, text="Profil NACA:").pack(anchor="w")
        profile_combo = ttk.Combobox(profile_frame, 
                                     textvariable=self.selected_profile,
                                     values=list(naca_data.keys()),
                                     state="readonly")
        profile_combo.pack(fill=tk.X, pady=(5, 0))
        profile_combo.current(0)  # Domyślnie wybierz pierwszy profil
        
        # Sekcja parametrów
        params_frame = ttk.LabelFrame(left_frame, text="Parametry", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Kąt natarcia
        ttk.Label(params_frame, text="Kąt natarcia [°]:").pack(anchor="w")
        angle_entry = ttk.Entry(params_frame, textvariable=self.angle_of_attack)
        angle_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Prędkość powietrza
        ttk.Label(params_frame, text="Prędkość powietrza [m/s]:").pack(anchor="w")
        speed_entry = ttk.Entry(params_frame, textvariable=self.air_speed)
        speed_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Gęstość powietrza
        ttk.Label(params_frame, text="Gęstość powietrza [kg/m³]:").pack(anchor="w")
        density_entry = ttk.Entry(params_frame, textvariable=self.air_density)
        density_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Powierzchnia skrzydła
        ttk.Label(params_frame, text="Powierzchnia skrzydła [m²]:").pack(anchor="w")
        area_entry = ttk.Entry(params_frame, textvariable=self.wing_area)
        area_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Przycisk "Oblicz"
        calculate_button = ttk.Button(left_frame, text="Oblicz", command=self.calculate)
        calculate_button.pack(fill=tk.X, pady=10)
        
        # Placeholder na wykres
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.plot.set_title("Dane aerodynamiczne profilu")
        self.plot.set_xlabel("Kąt natarcia [°]")
        self.plot.set_ylabel("Współczynnik")
        self.plot.grid(True)
        self.canvas = FigureCanvasTkAgg(self.figure, right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def calculate(self):
        """Metoda wywoływana po kliknięciu przycisku 'Oblicz'"""
        profile = self.selected_profile.get()
        angle = self.angle_of_attack.get()
        speed = self.air_speed.get()
        density = self.air_density.get()
        area = self.wing_area.get()
        
        # Na tym etapie tylko wyświetlamy komunikat
        print(f"Wybrano profil: {profile}")
        print(f"Parametry: kąt={angle}°, prędkość={speed} m/s, gęstość={density} kg/m³, powierzchnia={area} m²")
        print("Funkcjonalność obliczeniowa zostanie dodana w przyszłości.")
        
        # Tutaj w przyszłości będzie logika obliczeniowa i aktualizacja wykresu
        
if __name__ == "__main__":
    root = tk.Tk()
    app = Airfoil(root)
    root.mainloop()