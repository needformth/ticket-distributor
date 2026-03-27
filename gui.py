import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from distributor import TicketDistributor
from file_handler import FileHandler

class TicketApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Распределение билетов")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.students = []
        self.distribution = None

        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Количество билетов
        label_tickets = ctk.CTkLabel(main_frame, text="Количество билетов:", font=("Arial", 14))
        label_tickets.grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.entry_tickets = ctk.CTkEntry(main_frame, width=200)
        self.entry_tickets.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        # Способ ввода студентов
        label_input_method = ctk.CTkLabel(main_frame, text="Студенты:", font=("Arial", 14))
        label_input_method.grid(row=1, column=0, padx=5, pady=10, sticky="nw")
        self.input_method = ctk.CTkSegmentedButton(
            main_frame, values=["Ручной ввод", "Загрузить из файла"],
            command=self.on_input_method_change
        )
        self.input_method.grid(row=1, column=1, padx=5, pady=10, sticky="w")
        self.input_method.set("Ручной ввод")

        # Ручной ввод
        self.manual_frame = ctk.CTkFrame(main_frame)
        self.manual_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        # Инструкция
        self.manual_label = ctk.CTkLabel(self.manual_frame, text="Вводите студентов с новой строки:", anchor="w")
        self.manual_label.pack(padx=10, pady=(5, 0), fill="x")
        self.text_students = ctk.CTkTextbox(self.manual_frame, height=150, width=600)
        self.text_students.pack(padx=10, pady=10, fill="both", expand=True)
        self.text_students.bind("<Control-Key>", self.handle_control_key)

        # Загрузка из файла
        self.file_frame = ctk.CTkFrame(main_frame)
        self.file_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.btn_load = ctk.CTkButton(self.file_frame, text="Выбрать файл", command=self.load_from_file)
        self.btn_load.pack(pady=10, padx=10)
        self.label_file = ctk.CTkLabel(self.file_frame, text="Файл не выбран")
        self.label_file.pack(pady=5)
        self.file_frame.grid_remove()   # скрываем, пока не выбран этот способ

        # Сохранение в файл
        self.save_var = ctk.BooleanVar(value=False)
        self.check_save = ctk.CTkCheckBox(main_frame, text="Сохранить результат в Excel",
                                          variable=self.save_var, command=self.on_save_toggle)
        self.check_save.grid(row=3, column=0, columnspan=2, padx=5, pady=10, sticky="w")

        self.save_frame = ctk.CTkFrame(main_frame)
        self.save_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.save_entry = ctk.CTkEntry(self.save_frame, placeholder_text="Путь для сохранения...")
        self.save_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.btn_browse = ctk.CTkButton(self.save_frame, text="Обзор", width=80, command=self.browse_save_path)
        self.btn_browse.pack(side="right", padx=5)
        self.save_frame.grid_remove()

        # Кнопка распределения
        self.btn_distribute = ctk.CTkButton(main_frame, text="Распределить", command=self.distribute,
                                            font=("Arial", 14, "bold"))
        self.btn_distribute.grid(row=5, column=0, columnspan=2, padx=5, pady=20)

        # Область результатов
        self.result_frame = ctk.CTkScrollableFrame(main_frame, label_text="Результаты распределения")
        self.result_frame.grid(row=6, column=0, columnspan=2, padx=5, pady=10, sticky="nsew")

        # Настройка весов для растяжения
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_rowconfigure(6, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

    def on_input_method_change(self, value):
        if value == "Ручной ввод":
            self.manual_frame.grid()
            self.file_frame.grid_remove()
        else:
            self.manual_frame.grid_remove()
            self.file_frame.grid()

    def load_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV файлы", "*.csv"), ("Excel файлы", "*.xlsx")])
        if not file_path:
            return
        try:
            has_name = messagebox.askyesno("Заголовок", "В файле есть строка с заголовками?")
            self.students = FileHandler.load_students(file_path, has_name=has_name)
            self.label_file.configure(text=f"Загружено студентов: {len(self.students)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")

    def on_save_toggle(self):
        if self.save_var.get():
            self.save_frame.grid()
        else:
            self.save_frame.grid_remove()

    def browse_save_path(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            self.save_entry.delete(0, "end")
            self.save_entry.insert(0, file_path)

    def distribute(self):
        try:
            tickets_amount = int(self.entry_tickets.get())
            if tickets_amount < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное количество билетов (целое неотрицательное число)")
            return

        if self.input_method.get() == "Ручной ввод":
            students_text = self.text_students.get("0.0", "end").strip()
            if not students_text:
                messagebox.showerror("Ошибка", "Введите список студентов (каждый с новой строки)")
                return
            self.students = [line.strip() for line in students_text.split("\n") if line.strip()]
            if not self.students:
                messagebox.showerror("Ошибка", "Список студентов пуст")
                return
        else:
            if not self.students:
                messagebox.showerror("Ошибка", "Сначала загрузите список студентов из файла")
                return

        try:
            self.distribution = TicketDistributor.distribute(self.students, tickets_amount)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при распределении:\n{e}")
            return

        self.display_results()

        if self.save_var.get():
            save_path = self.save_entry.get().strip()
            if not save_path:
                messagebox.showerror("Ошибка", "Укажите путь для сохранения результата")
                return
            if not save_path.endswith('.xlsx'):
                messagebox.showerror("Ошибка", "Путь должен заканчиваться на .xlsx")
                return
            try:
                FileHandler.save_results(self.distribution, file_path=save_path)
                messagebox.showinfo("Успех", f"Результаты сохранены в {save_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def display_results(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        if not self.distribution:
            return

        header = ctk.CTkFrame(self.result_frame)
        header.pack(fill="x", pady=2)
        ctk.CTkLabel(header, text="Студент", width=250, font=("Arial", 12, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Билеты (номера)", width=400, font=("Arial", 12, "bold")).pack(side="left", padx=5)

        for student, tickets in self.distribution.items():
            row = ctk.CTkFrame(self.result_frame)
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=student, width=250).pack(side="left", padx=5)
            tickets_str = ", ".join(map(str, tickets)) if tickets else "нет билетов"
            ctk.CTkLabel(row, text=tickets_str, width=400).pack(side="left", padx=5)

        total_tickets = sum(len(t) for t in self.distribution.values())
        info_label = ctk.CTkLabel(self.result_frame, text=f"Всего распределено билетов: {total_tickets}", font=("Arial", 10))
        info_label.pack(pady=5)

    def handle_control_key(self, event):
        # Ctrl+A (выделить всё) – код 65
        if event.keycode == 65:
            self.text_students.tag_add("sel", "1.0", "end")
            return "break"

        # Ctrl+X (вырезать) – код 88
        elif event.keycode == 88:
            try:
                selected = self.text_students.get("sel.first", "sel.last")
                if selected:
                    self.clipboard_clear()
                    self.clipboard_append(selected)
                    self.text_students.delete("sel.first", "sel.last")
                return "break"
            except tk.TclError:
                pass

        # Ctrl+V (вставить) – код 86
        elif event.keycode == 86:
            try:
                text = self.clipboard_get()
                self.text_students.insert("insert", text)
                return "break"
            except:
                pass
                