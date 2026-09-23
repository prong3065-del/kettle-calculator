import tkinter as tk
from tkinter import ttk, messagebox
import sys

class KettleCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("🫖 Умный калькулятор закипания чайника")
        self.root.geometry("500x780")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Состояние приложения
        self.theme = "light"
        self.calculated_seconds = 0
        self.timer_job = None
        self.alert_job = None
        self.is_alerting = False
        self.alert_color_state = False

        # Теплоемкость материалов (Дж/(кг·°C))
        self.materials = {
            "Нержавеющая сталь": 500,
            "Стекло": 840,
            "Керамика": 880,
            "Пластик": 1500
        }

        self.setup_styles()
        self.create_widgets()
        self.apply_theme()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

    def create_widgets(self):
        # Главный фрейм
        self.main_frame = ttk.Frame(self.root, padding=15)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок и кнопка темы
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(header_frame, text="🫖 Калькулятор закипания", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        self.btn_theme = ttk.Button(header_frame, text="🌙 Тема", command=self.toggle_theme, width=8)
        self.btn_theme.pack(side=tk.RIGHT)

        # --- Параметры ввода (Ползунки) ---
        input_frame = ttk.LabelFrame(self.main_frame, text="Параметры", padding=10)
        input_frame.pack(fill=tk.X, pady=5)

        # 1. Объем воды (1 знак после запятой)
        self.create_scale_row(input_frame, "Объем воды (л):", 0, 0.1, 3.0, 0.1, 1.0, "vol", ".1f")
        # 2. Мощность (целое число)
        self.create_scale_row(input_frame, "Мощность (Вт):", 1, 500, 3000, 50, 2000, "pwr", ".0f")
        # 3. Начальная температура (целое число)
        self.create_scale_row(input_frame, "Начальная темп. (°C):", 2, 0, 99, 1, 20, "temp", ".0f")
        # 4. Высота над уровнем моря (целое число)
        self.create_scale_row(input_frame, "Высота над у.м. (м):", 3, 0, 3000, 100, 0, "alt", ".0f")
        # 5. Масса чайника (1 знак после запятой)
        self.create_scale_row(input_frame, "Масса пустого чайника (кг):", 4, 0.1, 2.0, 0.1, 0.8, "mass", ".1f")

        # 6. Материал чайника
        ttk.Label(input_frame, text="Материал корпуса:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.combo_material = ttk.Combobox(input_frame, values=list(self.materials.keys()), state="readonly", width=17)
        self.combo_material.current(0)
        self.combo_material.grid(row=5, column=1, pady=5, padx=10)

        # Кнопка расчета
        self.btn_calc = ttk.Button(self.main_frame, text=" Рассчитать время", command=self.calculate, style="Accent.TButton")
        self.btn_calc.pack(fill=tk.X, pady=15)

        # Результат
        self.label_result = ttk.Label(self.main_frame, text="", font=("Arial", 11), justify=tk.LEFT)
        self.label_result.pack(pady=5)

        # --- Секция таймера ---
        self.timer_frame = ttk.LabelFrame(self.main_frame, text="Таймер", padding=10)
        self.timer_frame.pack_forget() 

        self.label_timer = ttk.Label(self.timer_frame, text="00:00", font=("Arial", 24, "bold"), foreground="gray")
        self.label_timer.pack(pady=5)

        timer_btn_frame = ttk.Frame(self.timer_frame)
        timer_btn_frame.pack(pady=5)

        self.btn_start_timer = ttk.Button(timer_btn_frame, text="▶ Запустить", command=self.confirm_start_timer)
        self.btn_start_timer.pack(side=tk.LEFT, padx=5)

        self.btn_stop_timer = ttk.Button(timer_btn_frame, text=" Стоп", command=self.stop_timer, state=tk.DISABLED)
        self.btn_stop_timer.pack(side=tk.LEFT, padx=5)

        # 👤 Подпись автора
        ttk.Label(self.main_frame, 
                  text="Автор идеи: Савченко И.Е., г. Пермь, 2026", 
                  font=("Arial", 8, "italic"), 
                  foreground="gray").pack(side=tk.BOTTOM, pady=(0, 5))

    def create_scale_row(self, parent, label_text, row, from_, to, resolution, default, var_name, fmt=".1f"):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=3)
        
        scale = ttk.Scale(parent, from_=from_, to=to, orient=tk.HORIZONTAL, length=200)
        scale.set(default)
        scale.grid(row=row, column=1, pady=3, padx=5)
        
        # Метка для отображения текущего значения ползунка с нужным форматом
        val_label = ttk.Label(parent, text=f"{default:{fmt}}", width=6, anchor=tk.E)
        val_label.grid(row=row, column=2, pady=3)
        
        # Обновление метки при движении ползунка
        scale.config(command=lambda v, lbl=val_label, f=fmt: lbl.config(text=f"{float(v):{f}}"))
        
        setattr(self, f"scale_{var_name}", scale)

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.btn_theme.config(text="☀️ Тема" if self.theme == "dark" else "🌙 Тема")
        self.apply_theme()

    def apply_theme(self):
        if self.theme == "light":
            bg_color = "#F0F0F0"
            fg_color = "#000000"
            btn_bg = "#4CAF50"
            self.style.configure("TFrame", background=bg_color)
            self.style.configure("TLabel", background=bg_color, foreground=fg_color)
            self.style.configure("TLabelframe", background=bg_color, foreground=fg_color)
            self.style.configure("TLabelframe.Label", background=bg_color, foreground=fg_color)
            self.style.configure("Accent.TButton", background=btn_bg, foreground="white")
            self.style.map("Accent.TButton", background=[("active", "#45a049")])
        else:
            bg_color = "#2D2D2D"
            fg_color = "#FFFFFF"
            btn_bg = "#2E7D32"
            self.style.configure("TFrame", background=bg_color)
            self.style.configure("TLabel", background=bg_color, foreground=fg_color)
            self.style.configure("TLabelframe", background=bg_color, foreground=fg_color)
            self.style.configure("TLabelframe.Label", background=bg_color, foreground=fg_color)
            self.style.configure("Accent.TButton", background=btn_bg, foreground="white")
            self.style.map("Accent.TButton", background=[("active", "#1b5e20")])

        self.root.config(bg=bg_color)
        if not self.is_alerting:
            self.label_timer.config(foreground="#888888" if self.theme == "light" else "#AAAAAA")

    def calculate(self):
        self.stop_timer()
        
        try:
            volume = float(self.scale_vol.get())
            power = float(self.scale_pwr.get())
            temp_initial = float(self.scale_temp.get())
            altitude = float(self.scale_alt.get())
            mass_kettle = float(self.scale_mass.get())
            material_name = self.combo_material.get()
            
            if power <= 0:
                raise ValueError("Мощность должна быть больше 0")
            
            # Расчет точки кипения с учетом высоты
            boiling_point = 100 - (altitude / 300)
            
            if temp_initial >= boiling_point:
                raise ValueError(f"Начальная темп. должна быть ниже точки кипения ({boiling_point:.1f}°C)")
            
            delta_t = boiling_point - temp_initial
            
            # Расчет энергии
            specific_heat_water = 4200
            specific_heat_kettle = self.materials[material_name]
            
            energy_water = volume * specific_heat_water * delta_t
            energy_kettle = mass_kettle * specific_heat_kettle * delta_t
            total_energy = energy_water + energy_kettle
            
            # Учет КПД 90%
            efficiency = 0.90
            time_seconds = (total_energy / power) / efficiency
            
            self.calculated_seconds = int(time_seconds)
            minutes = int(time_seconds // 60)
            seconds = int(time_seconds % 60)
            
            result_text = (
                f"🌡️ Точка кипения на данной высоте: {boiling_point:.1f}°C\n"
                f"⏱️ Реальное время (КПД 90%): {minutes} мин {seconds} сек\n\n"
                f"📊 Энергия на воду: {energy_water/1000:.1f} кДж\n"
                f"📊 Энергия на чайник: {energy_kettle/1000:.1f} кДж\n"
                f"💡 Потребление: {total_energy/3600000:.1f} кВт·ч"
            )
            
            self.label_result.config(text=result_text)
            
            if messagebox.askyesno("Таймер", f"Время закипания: {minutes} мин {seconds} сек.\nЗапустить обратный отсчет?"):
                self.timer_frame.pack(fill=tk.X, pady=5)
                self.label_timer.config(text=f"{minutes:02d}:{seconds:02d}")
                self.btn_start_timer.config(state=tk.NORMAL)
                self.start_timer()
            else:
                self.timer_frame.pack_forget()
                
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))

    def confirm_start_timer(self):
        if self.calculated_seconds > 0:
            self.start_timer()

    def start_timer(self):
        self.stop_timer()
        self.remaining_seconds = self.calculated_seconds
        self.btn_start_timer.config(state=tk.DISABLED)
        self.btn_stop_timer.config(state=tk.NORMAL)
        self.update_timer()

    def update_timer(self):
        if self.remaining_seconds <= 0:
            self.label_timer.config(text="00:00")
            self.start_alert()
            return
        
        mins = self.remaining_seconds // 60
        secs = self.remaining_seconds % 60
        self.label_timer.config(text=f"{mins:02d}:{secs:02d}")
        
        self.remaining_seconds -= 1
        self.timer_job = self.root.after(1000, self.update_timer)

    def stop_timer(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        
        self.is_alerting = False
        if self.alert_job:
            self.root.after_cancel(self.alert_job)
            self.alert_job = None
            
        # Восстановление нормального цвета текста таймера
        self.label_timer.config(foreground="#888888" if self.theme == "light" else "#AAAAAA")
        
        self.btn_start_timer.config(state=tk.NORMAL)
        self.btn_stop_timer.config(state=tk.DISABLED)
        if self.calculated_seconds > 0:
            mins = self.calculated_seconds // 60
            secs = self.calculated_seconds % 60
            self.label_timer.config(text=f"{mins:02d}:{secs:02d}")

    def start_alert(self):
        self.is_alerting = True
        self.alert_color_state = False
        self.root.bell()
        self.flash_text()

    def flash_text(self):
        if not self.is_alerting:
            return
        
        # Мерцание только текста (красный <-> цвет темы)
        self.alert_color_state = not self.alert_color_state
        
        if self.alert_color_state:
            self.label_timer.config(text="⚠️ ВОДА ЗАКИПЕЛА! ⚠️", foreground="red")
        else:
            theme_color = "#888888" if self.theme == "light" else "#AAAAAA"
            self.label_timer.config(text="⚠️ ВОДА ЗАКИПЕЛА! ⚠️", foreground=theme_color)
            
        self.alert_job = self.root.after(400, self.flash_text)

    def on_closing(self):
        self.stop_timer()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = KettleCalculator(root)
    root.mainloop()
