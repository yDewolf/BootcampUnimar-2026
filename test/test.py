import tkinter as tk

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerenciador de Quadros Simples")
        self.geometry("300x200")
        
        # Container principal
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.frames = {}
        
        # Inicializa as telas
        for F in (Tela1, Tela2):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.mostrar_tela(Tela1)
        
    def mostrar_tela(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class Tela1(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Esta é a Tela 1")
        label.pack(padx=20, pady=20)
        
        botao = tk.Button(self, text="Ir para Tela 2", 
                          command=lambda: controller.mostrar_tela(Tela2))
        botao.pack(pady=10)

class Tela2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Esta é a Tela 2")
        label.pack(padx=20, pady=20)
        
        botao = tk.Button(self, text="Voltar para Tela 1", 
                          command=lambda: controller.mostrar_tela(Tela1))
        botao.pack(pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()