from tkinter import *  
from tkinter import messagebox 
import tkinter as tk 
from tkinter import ttk
import random
import time  
from data import Data
import threading
import traceback
import os
import importlib.util
from PIL import Image, ImageTk

class ModManager:
    def __init__(self, mod_directory="mods")->None:
        try:
            self.mod_directory = mod_directory
            self.mods = []
            self.load_mods()
        except:
            messagebox.showerror("Error", "Hubo un error cargando los mods debido a un error o incompatibilidad en el mod, se iniciara en vanilla.")

    def load_mods(self)->None:
        if not os.path.exists(self.mod_directory):
            os.makedirs(self.mod_directory)
        for filename in os.listdir(self.mod_directory):
            if filename.endswith(".py"):
                self.load_mod(filename)
                    
    def load_mod(self, filename)->None:
        mod_path = os.path.join(self.mod_directory, filename)
        spec = importlib.util.spec_from_file_location(filename[:-3], mod_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.mods.append(mod)

    def apply_mods(self, game)->None:
        for mod in self.mods:
            if hasattr(mod, 'apply_mod'):
                mod.apply_mod(game)

class Minesweeper:
    def __init__(self, root)->None:
        self.root = root 
        self.frame = Frame(self.root)  
        self.frame.pack()  
        self.root.title("Siria Simulator") 
        self.root.iconbitmap("img/bomba.ico")  
        self.root.resizable(False, False)  
        self.frame.config(width=400, height=400) 
        self.navbar = Menu(self.root)
        self.root.config(menu=self.navbar)
        self.transparent_image = PhotoImage(width=1, height=1)
        
        # Mod Manager
        self.mod_manager = ModManager()
        self.mod_manager.apply_mods(self)
        
        self.player=tk.StringVar()
        self.player.set("Player")
        self.file_path = 'stats.csv'
        self.file_menu = Menu(self.navbar, tearoff=0)
        self.file_menu.add_command(label="Nuevo Juego", command=self.resetGame)
        self.file_menu.add_command(label="Stats", command=self.stats)
        self.file_menu.add_command(label="Opciones", command=self.options)
        self.file_menu.add_command(label="Salir", command=self.root.quit)
        self.navbar.add_cascade(label="Archivo", menu=self.file_menu)

        self.difficulty = {"Easy": 40, "Normal": 64, "Hard": 81, "ELDETONACULOS":150}
        self.current_difficulty = self.difficulty["Easy"]

        self.buttonsList = []  
        self.reset = False 
        self.inicio = False 
        self.timeInicio = time.time()  
        self.flags = 0  
        self.bombs = [] 
        self.contadortime = Label(self.frame)  
        self.contadortime.grid(column=1, row=0, columnspan=4) 
        self.flags_counter = Label(self.frame, text="Banderas disponibles: " + str(self.flags), font=("Arial 15")) 
        self.flags_counter.grid(column=5, row=0, columnspan=4)  
        
        self.timeHabilited = False  
        # Imagenes originales
        img_bomb_original = Image.open("img\\bomba3.png")
        img_flag_original = Image.open("img\\bandera.png")

        # Redimensionamiento de imagenes
        img_bomb_rescaled = img_bomb_original.resize((50, 50), Image.Resampling.LANCZOS) 
        img_flag_rescaled = img_flag_original.resize((50, 50), Image.Resampling.LANCZOS)  

        # Conversion a un formato que acepte tk
        self.bomb = ImageTk.PhotoImage(img_bomb_rescaled)
        self.flag = ImageTk.PhotoImage(img_flag_rescaled)
        
        #Opciones
        self.isShakeWindowEnabled = tk.BooleanVar()
        self.isShakeWindowEnabled.set(True)
        self.defaultNoInstaLoseAttemps = 3
        
        self.currentAttemps = self.defaultNoInstaLoseAttemps
        
        self.generateButtons() 
        self.bombsRandom()  
    
    def difficultyToString(self, difficulty)->str:
        if difficulty == self.difficulty["Easy"]:
            return "Easy"
        elif difficulty == self.difficulty["Normal"]:
            return "Normal"
        elif difficulty == self.difficulty["Hard"]:
            return "Hard"
        elif difficulty == self.difficulty["ELDETONACULOS"]:
            return "ELDETONACULOS"
        
    def stats(self)->None:
        self.statsWindow = Toplevel(self.root)
        self.statsWindow.title("Estadísticas")
        self.statsWindow.geometry("300x200")
       
        stats = Data.getStats(self.file_path)

        for i, (username, score, dif) in enumerate(stats):
            Label(self.statsWindow, text=f"Jugador:{username}").grid(row=i, column=0, padx=10, pady=5)
            Label(self.statsWindow, text=f"time:{score}s").grid(row=i, column=1, padx=10, pady=5)
            Label(self.statsWindow, text=f"Dificultad:{dif}").grid(row=i, column=2, padx=10, pady=5)
    
    def options(self) -> None:
        self.optionsWindow = Toplevel(self.root)
        self.optionsWindow.title("Opciones")
        self.optionsWindow.geometry("300x250")

        options = ["Easy", "Normal", "Hard", "ELDETONACULOS"]

        selectedOption = StringVar(self.optionsWindow)
        selectedOption.set(self.difficultyToString(self.current_difficulty))

        def seleccionar_opcion(opcion)->None:
            self.current_difficulty = self.difficulty[opcion]
            self.resetGame()

        self.entry = Entry(self.optionsWindow, width=30, textvariable=self.player)
        self.entry.grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        def applyInput()->None:
            input_text = self.entry.get()
            messagebox.showinfo("Options changed", "Los valores se ajustaron correctamente!")

        applyButton = Button(self.optionsWindow, text="Aplicar", command=applyInput)
        applyButton.grid(row=1, column=0, columnspan=2, pady=10)

        difficultyLabel = Label(self.optionsWindow, text="Dificultad:", font=("Arial", 12))
        difficultyLabel.grid(row=2, column=0, padx=10, pady=10, sticky=E)

        option_menu = OptionMenu(self.optionsWindow, selectedOption, *options, command=seleccionar_opcion)
        option_menu.grid(row=2, column=1, padx=10, pady=10, sticky=W)
        
        checkbox = ttk.Checkbutton(self.optionsWindow, text="Movimiento de ventana al perder", variable=self.isShakeWindowEnabled)
        checkbox.grid(row=3, column=0, padx=10, pady=10)

        exitButton = Button(self.optionsWindow, text="Cerrar", command=self.optionsWindow.destroy)
        exitButton.grid(row=4, column=1, columnspan=2, pady=20)

    def time(self)->None:
        if self.timeHabilited:
            self.time_actual = int(time.time() - self.timeInicio)
            self.contadortime.config(text="time transcurrido: " + str(self.time_actual), font=("Arial 15"))
            self.root.after(1000, self.time) 

    def generateButtons(self)->None:
        filas, columnas = self.find_dimensions(self.current_difficulty)
        self.buttonsList = []  

        for i in range(filas):
            fila_botones = [] 
            for j in range(columnas):
                btn = Button(self.frame, width=6, height=3, text="", font=("Arial 8 bold"), bg="grey")
                btn.bind('<Button-1>', lambda event, c=(i, j): self.slotPressed(c))
                btn.bind('<Button-3>', lambda event, c=(i, j): self.placeFlag(c))
                btn.grid(column=j + 1, row=i + 1, sticky='nsew')  
                fila_botones.append(btn) 
            self.buttonsList.append(fila_botones)  

    def bombsRandom(self)->None:
        total_casillas = self.current_difficulty
        filas, columnas = self.find_dimensions(total_casillas)
        self.bombs = random.sample(range(total_casillas), total_casillas // 4)
        self.setFlags(len(self.bombs)) 
        for bomba in self.bombs:
            fila, columna = divmod(bomba, columnas)
            self.buttonsList[fila][columna].config(command=lambda i=bomba: self.revealBombas(self.bombs))
    
    def checkWin(self)->None:
        buttons_discovered = 0
        total_safe_buttons = self.current_difficulty - len(self.bombs)
        
        for i in range(len(self.buttonsList)):
            for j in range(len(self.buttonsList[i])):
                button = self.buttonsList[i][j]
                if (i * len(self.buttonsList[i]) + j) not in self.bombs and button['bg'] != 'grey':
                    buttons_discovered += 1

        if buttons_discovered == total_safe_buttons:
            self.timeHabilited = False
            Data.addStats(self.file_path,self.player.get(), self.time_actual, self.difficultyToString(self.current_difficulty))
            messagebox.showinfo("Victory", "¡Has ganado el juego!")
            self.resetGame()

    def setFlags(self, flags)->None:
        self.flags = flags
        self.flags_counter.config(text="Banderas disponibles: " + str(flags))
        self.updateFlagsCounter()

    def revealBombas(self, index)->None:
        explosionPower=0
        filas, columnas = self.find_dimensions(self.current_difficulty)
        for i in index:
            fila, columna = divmod(i, columnas)
            if self.buttonsList[fila][columna]['bg'] != 'orange':
                self.buttonsList[fila][columna].config(bg='red', image=self.bomb)
                explosionPower+=1
        if self.isShakeWindowEnabled.get():
            self.shakeWindow(explosionPower)
        self.timeHabilited = False
        messagebox.showinfo("Game Over", "Has pulsado una bomba!")
        self.resetGame()

    def shakeWindow(self, intensity, duration=2000)->None:
        """
        Sacude la ventana de Tkinter con una intensidad específica durante un periodo de time.

        Parámetros:
        intensity (int): La intensidad del sacudido.
        duration (int): Duración del sacudido en milisegundos (por defecto es 2000ms, equivalente a 2s).
        """
        def shake():
            if self.shake_count < max_shakes:
                # Mueve la ventana a una nueva posición aleatoria alrededor de su posición original
                delta_x = random.randint(-intensity, intensity)
                delta_y = random.randint(-intensity, intensity)
                self.root.geometry(f'+{self.original_x + delta_x}+{self.original_y + delta_y}')
                self.shake_count += 1
                self.root.after(interval, shake)
            else:
                # Restaura la posición original
                self.root.geometry(f'+{self.original_x}+{self.original_y}')
        # Obtiene la posición actual de la ventana
        self.original_x = self.root.winfo_x()
        self.original_y = self.root.winfo_y()

        # Calcula la cantidad de sacudidas y el intervalo entre ellas
        interval = 50  # Intervalo en milisegundos
        max_shakes = duration // interval
        self.shake_count = 0

        # Inicio
        shake()
    
    def find_factors(self, n)->int:
        factors = [(i, n // i) for i in range(1, int(n**0.5) + 1) if n % i == 0]
        return factors

    def find_dimensions(self, n)->int:
        factors = self.find_factors(n)
        closest_to_square = min(factors, key=lambda x: abs(x[0] - x[1]))
        return closest_to_square

    def countNearbyBombs(self, index)->int:
        count = 0 
        filas, columnas = self.find_dimensions(self.current_difficulty)
        fila, columna = index
        for dy in (-1, 0, 1):  
            for dx in (-1, 0, 1): 
                if dx == 0 and dy == 0:
                    continue 
                nx, ny = columna + dx, fila + dy  
                if 0 <= nx < columnas and 0 <= ny < filas: 
                    if (ny * columnas + nx) in self.bombs:  
                        count += 1  
        return count  

    def coloration(self, num)->str:
        """
        Retorna un color RGB en formato adecuado para Tkinter según el nivel de gravedad dado.

        Parámetros:
        num (int): El nivel de gravedad, de 1 (mínimo) a 9 (máximo).

        Retorno:
        str: Color RGB en formato hexadecimal adecuado para Tkinter.
        """
        # Asegurarse de que num esté dentro del rango 1-9
        if num < 1:
            num = 1
        elif num > 9:
            num = 9

        # Calcular el color
        # De verde (#00FF00) a rojo (#FF0000)
        red = int((num - 1) * (255 / 8))
        green = int(255 - ((num - 1) * (255 / 8)))
        blue = 0

        return f'#{red:02x}{green:02x}{blue:02x}'
    
    def slotPressed(self, index)->None:
        filas, columnas = self.find_dimensions(self.current_difficulty)
        fila, columna = index
        
        if not self.inicio:
            self.currentAttemps -= 1
            if fila * columnas + columna in self.bombs and self.current_difficulty in [self.difficulty["Easy"], self.difficulty["Normal"]]:
                # Reasignar bomba
                self.reassignBomb(fila, columna)
                
            self.timeInicio = time.time()
            self.timeHabilited = True
            self.time()
            if self.currentAttemps==0:
                self.inicio = True
            
        if self.buttonsList[fila][columna]['text'] == '' and self.buttonsList[fila][columna]['bg'] == 'grey':
            bombas_cercanas = self.countNearbyBombs(index)
            self.buttonsList[fila][columna].config(bg='SystemButtonFace', text=str(bombas_cercanas) if bombas_cercanas > 0 else '', fg=self.coloration(bombas_cercanas))
            if bombas_cercanas == 0:
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = columna + dx, fila + dy
                        if 0 <= nx < columnas and 0 <= ny < filas:
                            adj_index = (ny, nx)
                            if adj_index not in self.bombs and self.buttonsList[ny][nx]['text'] == '' and self.buttonsList[ny][nx]['bg'] == 'grey':
                                self.slotPressed(adj_index)
            self.checkWin()

    def reassignBomb(self, fila, columna)->None:
        print("Reasigned")
        filas, columnas = self.find_dimensions(self.current_difficulty)
        bomb_index = fila * columnas + columna
        self.bombs.remove(bomb_index)

        available_spots = set(range(self.current_difficulty)) - set(self.bombs) - {bomb_index}
        new_bomb = random.choice(list(available_spots))
        self.bombs.append(new_bomb)
        
        # Actualizar el comando del nuevo botón de bomba
        new_fila, new_columna = divmod(new_bomb, columnas)
        self.buttonsList[new_fila][new_columna].config(command=lambda i=new_bomb: self.revealBombas(self.bombs))
        
        # Eliminar el comando del botón donde se quitó la bomba
        self.buttonsList[fila][columna].config(command=lambda: None)

    def placeFlag(self, index)->None:
        fila, columna = index
        if self.buttonsList[fila][columna]['bg'] == 'grey':
            if self.flags > 0:
                self.buttonsList[fila][columna].config(bg='orange', image=self.flag)
                self.flags -= 1
                self.updateFlagsCounter()
        elif self.buttonsList[fila][columna]['bg'] == 'orange':
            self.buttonsList[fila][columna].config(bg='grey', image=self.transparent_image)
            self.flags += 1
            self.updateFlagsCounter()

    def updateFlagsCounter(self)->None:
        self.flags_counter.config(text="Banderas disponibles: " + str(self.flags))

    def resetGame(self)->None:
        self.timeHabilited = False
        self.currentAttemps = self.defaultNoInstaLoseAttemps
        self.contadortime.config(text="time transcurrido: " + str(0), font=("Arial 15"))
        for fila in self.buttonsList:
            for boton in fila:
                boton.unbind('<Button-1>')
                boton.unbind('<Button-3>')
                boton.destroy()
        self.buttonsList = []
        self.frame.pack_forget()
        self.frame.pack()
        self.generateButtons()
        self.bombsRandom()
        self.inicio = False
        self.updateFlagsCounter()

def debugConsole()->None:
    while True:
        command = input("Introduce un comando: ")
        try:
            exec(command)
        except Exception as e:
            l = traceback.format_exc()
            print(f"Error al ejecutar el comando: {e} {l}")

if __name__ == "__main__" and os.path.isfile("img/coconut/coconut.jpeg"):
    hilo_consola = threading.Thread(target=debugConsole, daemon=True)
    hilo_consola.start()
    root = Tk() 
    app = Minesweeper(root)  
    root.mainloop()  
else:
    messagebox.showerror("Error", "Hubo un error fatal debido a la falta de un archivo esencial para la ejecucion.") 