from image_capture import locate_portfolio_section
import tkinter as tk


class MainFrame(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        vldt_ifnum_cmd = (self.register(self.validate_percentage_number), '%S')
        percentage_limit = tk.Spinbox(self, from_=-100, to=100, width=10, justify="center", validate="all", validatecommand=vldt_ifnum_cmd)
        percentage_limit.insert(0, 0)
        percentage_limit.grid(row=0, column=0)
        initiate_button = tk.Button(
            self, 
            text="Iniciar", 
            command=lambda: locate_portfolio_section(percentage_limit.get()),
            bg="green", 
            pady=5, 
            padx=10, 
            font={"size": 20}
        )
        initiate_button.grid(row=0, column=1, padx=10)

    def validate_percentage_number(self, new_value):
        """Check the value inserted in percentage spinbox are only numbers"""
        valid = new_value == '' or new_value.isdigit() or new_value == '-'
        if not valid:
            self.bell()
        return valid
        

if __name__ == "__main__":
    root = tk.Tk()
    root.title = "Lector porcentaje de profit Iqoption"
    root.resizable(width=False, height=False)
    MainFrame(root, width=200, height=200, padx=30, pady=30).grid()
    root.mainloop()
