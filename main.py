from image_capture import DetectScreen
from tkinter import messagebox
from tkinter import scrolledtext
import tkinter as tk
import re


"""customized scrolled text area class to define method for insert text in a new line everytime"""
class TextareaInfoWidget(scrolledtext.ScrolledText):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.last_line_counter = 1.0

    def insert_text(self, text):
        self.config(state='normal')
        self.insert(str(self.last_line_counter), text + "\n")
        self.config(state='disabled')
        self.last_line_counter += 1.0


class MainFrame(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.config(padx=50, pady=20)
        vldt_ifnum_cmd = (self.register(self.validate_percentage_number), '%S')
        self.program_active = None  # Flag to check if the thread for image_capture is running
        self.percentage_limit_search = tk.LabelFrame(self, text="Introduzca porcentaje de ganancia deseado:", pady=5, padx=5)
        options_list = ["Mayor a", "Menor a"]  # List of options for OptionMenu
        self.value_option_menu = tk.StringVar(self.percentage_limit_search)
        self.bigger_less_than_option = tk.ttk.OptionMenu(self.percentage_limit_search, self.value_option_menu, options_list[0], *options_list)
        self.percentage_sign = tk.Label(self.percentage_limit_search, text="%")
        self.percentage_limit = tk.Spinbox(self.percentage_limit_search, from_=-100, to=100, width=10, justify="center", validate="all", validatecommand=vldt_ifnum_cmd)
        self.percentage_limit.insert("0", "0")
        self.start_button = tk.Button(
            self, 
            text = "Iniciar", 
            command = self.start_program,
            bg = "#84e73f", 
            pady = 5, 
            padx = 10,
            state = "normal",
            font = {"size": 20}
        )
        self.info_window = TextareaInfoWidget(self, width=40, height=10, 
                                                        state='disabled', wrap='word')
        
        # Elements for the self frame
        self.percentage_limit_search.grid(row=0, column=0)
        self.start_button.grid(row=0, column=1, padx=10)
        self.info_window.grid(row=1, column=0, columnspan=2, pady=10)

        # Elements for percentage_limit_search LabelFrame
        self.bigger_less_than_option.grid(row=0, column=0, padx=5)
        self.percentage_limit.grid(row=0, column=1, padx=5)
        self.percentage_sign.grid(row=0, column=2)
        
        

    def validate_percentage_number(self, new_value):
        """Check the value inserted in percentage spinbox are only numbers"""
        match = re.match(r'[\d -]+', new_value)
        valid = new_value == ''
        if match is None and (not valid):
            self.bell()
            return False
        else:
            return True

    def start_program(self):
        if self.program_active is None:
            if not self.percentage_limit.get().lstrip("-").isdigit():
                messagebox.showerror("Error en el porcentaje deseado", 
                                    "Por favor introduzca un dígito válido en el cuadro del porcentaje deseado")
                return
            self.percentage_limit.config(state="disabled")
            self.bigger_less_than_option.configure(state="disabled")
            self.program_active = DetectScreen(self.percentage_limit.get(), self.value_option_menu.get(), self.info_window)
            self.program_active.start()
            self.info_window.insert_text("Iniciando, mantenga la app de Iqoption desplegada en pantalla...")
            self.start_button["bg"] = "#ff4949"
            self.start_button["text"] = "Detener"
        else:
            self.program_active.stop()
            self.start_button["bg"] = "#84e73f"
            self.start_button["text"] = "Iniciar"
            self.percentage_limit.config(state="normal")
            self.bigger_less_than_option.configure(state="normal")
            self.program_active = None
        

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Lector porcentaje de ganancia Iqoption")
    root.iconbitmap("images/iqicon.ico")
    MainFrame(root).pack(expand=True)
    root.resizable(width=False, height=False)
    root.mainloop()
