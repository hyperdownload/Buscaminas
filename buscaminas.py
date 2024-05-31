from tkinter import *  
from tkinter import messagebox 
import tkinter as tk 
import random
import time  
from data import Data
import threading
import traceback
import os
import importlib.util
from PIL import Image, ImageTk

class ModManager:
    def __init__(self, mod_directory="mods"):
        self.mod_directory = mod_directory
        self.mods = []
        self.load_mods()

    def load_mods(self):
        if not os.path.exists(self.mod_directory):
            os.makedirs(self.mod_directory)
        for filename in os.listdir(self.mod_directory):
            if filename.endswith(".py"):
                self.load_mod(filename)

    def load_mod(self, filename):
        mod_path = os.path.join(self.mod_directory, filename)
        spec = importlib.util.spec_from_file_location(filename[:-3], mod_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.mods.append(mod)

    def apply_mods(self, game):
        for mod in self.mods:
            if hasattr(mod, 'apply_mod'):
                mod.apply_mod(game)
class Minesweeper:
    def __init__(self, root):
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

        self.listaBotones = []  
        self.reset = False 
        self.inicio = False 
        self.tiempoInicio = time.time()  
        self.flags = 0  
        self.bombas = [] 
        self.contadorTiempo = Label(self.frame)  
        self.contadorTiempo.grid(column=1, row=0, columnspan=4) 
        self.flags_counter = Label(self.frame, text="Banderas disponibles: " + str(self.flags), font=("Arial 15")) 
        self.flags_counter.grid(column=5, row=0, columnspan=4)  
        
        self.tiempoHabilitado = False  
        # Imagenes originales
        img_bomb_original = Image.open("img\\bomba3.png")
        img_flag_original = Image.open("img\\bandera.png")

        # Redimensionamiento de imagenes
        img_bomb_rescaled = img_bomb_original.resize((50, 50), Image.ANTIALIAS) 
        img_flag_rescaled = img_flag_original.resize((50, 50), Image.ANTIALIAS)  

        # Conversion a un formato que acepte tk
        self.bomb = ImageTk.PhotoImage(img_bomb_rescaled)
        self.flag = ImageTk.PhotoImage(img_flag_rescaled)
        
        # Mod Manager
        self.mod_manager = ModManager()
        self.mod_manager.apply_mods(self)
        
        self.generarBotones() 
        self.bombasRandom()  
    
    def difficultyToString(self, difficulty):
        return "Easy" if difficulty == self.difficulty["Easy"] else self.difficulty["Normal"] if difficulty == self.difficulty["Hard"] else "Hard" if difficulty == self.difficulty["Hard"] else difficulty == self.difficulty["ELDETONACULOS"]
    
    def stats(self):
        self.statsWindow = Toplevel(self.root)
        self.statsWindow.title("Estadísticas")
        self.statsWindow.geometry("300x200")
       
        stats = Data.getStats(self.file_path)

        for i, (username, score, dif) in enumerate(stats):
            Label(self.statsWindow, text=f"Jugador:{username}").grid(row=i, column=0, padx=10, pady=5)
            Label(self.statsWindow, text=f"Tiempo:{score}s").grid(row=i, column=1, padx=10, pady=5)
            Label(self.statsWindow, text=f"Dificultad:{dif}").grid(row=i, column=2, padx=10, pady=5)
    
    def options(self):
        self.ventana_opciones = Toplevel(self.root)  
        self.ventana_opciones.title("Opciones")  
        self.ventana_opciones.geometry("300x200")  

        opciones = ["Easy", "Normal", "Hard", "ELDETONACULOS"]

        opcion_seleccionada = StringVar(self.ventana_opciones)
        opcion_seleccionada.set(self.difficultyToString(self.current_difficulty))

        def seleccionar_opcion(opcion):
            self.current_difficulty = self.difficulty[opcion]
            self.resetGame()

        self.entry = Entry(self.ventana_opciones, width=30, textvariable=self.player)
        self.entry.pack(pady=20)

        def aplicar_input():
            input_text = self.entry.get()
            messagebox.showinfo("Options changed", "Los valores se ajustaron correctamente!")

        boton_aplicar = Button(self.ventana_opciones, text="Aplicar", command=aplicar_input)
        boton_aplicar.pack(pady=10)
        
        label_dificultad = Label(self.ventana_opciones, text="Dificultad:", font=("Arial 12"))
        label_dificultad.pack(side=LEFT)

        option_menu = OptionMenu(self.ventana_opciones, opcion_seleccionada, *opciones, command=seleccionar_opcion)
        option_menu.pack(side=LEFT)

        boton_cerrar = Button(self.ventana_opciones, text="Cerrar", command=self.ventana_opciones.destroy)
        boton_cerrar.pack(side=BOTTOM)

    def tiempo(self):
        if self.tiempoHabilitado:
            self.tiempo_actual = int(time.time() - self.tiempoInicio)
            self.contadorTiempo.config(text="Tiempo transcurrido: " + str(self.tiempo_actual), font=("Arial 15"))
            self.root.after(1000, self.tiempo) 

    def generarBotones(self):
        filas, columnas = self.find_dimensions(self.current_difficulty)
        self.listaBotones = []  

        for i in range(filas):
            fila_botones = [] 
            for j in range(columnas):
                btn = Button(self.frame, width=6, height=3, text="", font=("Arial 8 bold"), bg="grey")
                btn.bind('<Button-1>', lambda event, c=(i, j): self.slotPulsado(c))
                btn.bind('<Button-3>', lambda event, c=(i, j): self.colocarBandera(c))
                btn.grid(column=j + 1, row=i + 1, sticky='nsew')  
                fila_botones.append(btn) 
            self.listaBotones.append(fila_botones)  

    def bombasRandom(self):
        total_casillas = self.current_difficulty
        filas, columnas = self.find_dimensions(total_casillas)
        self.bombas = random.sample(range(total_casillas), total_casillas // 4)
        self.setFlags(len(self.bombas)) 
        for bomba in self.bombas:
            fila, columna = divmod(bomba, columnas)
            self.listaBotones[fila][columna].config(command=lambda i=bomba: self.revealBombas(self.bombas))

    def checkWin(self):
        buttons_discovered = 0
        total_safe_buttons = self.current_difficulty - len(self.bombas)
        
        for i in range(len(self.listaBotones)):
            for j in range(len(self.listaBotones[i])):
                button = self.listaBotones[i][j]
                if (i * len(self.listaBotones[i]) + j) not in self.bombas and button['bg'] != 'grey':
                    buttons_discovered += 1

        if buttons_discovered == total_safe_buttons:
            self.tiempoHabilitado = False
            Data.addStats(self.file_path,self.player.get(), self.tiempo_actual, self.difficultyToString(self.current_difficulty))
            messagebox.showinfo("Victory", "¡Has ganado el juego!")
            self.resetGame()

    def setFlags(self, flags):
        self.flags = flags
        self.flags_counter.config(text="Banderas disponibles: " + str(flags))
        self.updateFlagsCounter()

    def revealBombas(self, index):
        filas, columnas = self.find_dimensions(self.current_difficulty)
        for i in index:
            fila, columna = divmod(i, columnas)
            self.listaBotones[fila][columna].config(bg='red', image=self.bomb)
        self.tiempoHabilitado = False
        messagebox.showinfo("Game Over", "Has pulsado una bomba!")
        self.resetGame()

    def find_factors(self, n):
        factors = [(i, n // i) for i in range(1, int(n**0.5) + 1) if n % i == 0]
        return factors

    def find_dimensions(self, n):
        factors = self.find_factors(n)
        closest_to_square = min(factors, key=lambda x: abs(x[0] - x[1]))
        return closest_to_square

    def contarBombasCercanas(self, index):
        count = 0 
        filas, columnas = self.find_dimensions(self.current_difficulty)
        fila, columna = index
        for dy in (-1, 0, 1):  
            for dx in (-1, 0, 1): 
                if dx == 0 and dy == 0:
                    continue 
                nx, ny = columna + dx, fila + dy  
                if 0 <= nx < columnas and 0 <= ny < filas: 
                    if (ny * columnas + nx) in self.bombas:  
                        count += 1  
        return count  

    def slotPulsado(self, index):
        filas, columnas = self.find_dimensions(self.current_difficulty)
        fila, columna = index
        
        if not self.inicio:
            if fila * columnas + columna in self.bombas and self.current_difficulty in [self.difficulty["Easy"], self.difficulty["Normal"]]:
                # Reasignar bomba
                self.reassignBomb(fila, columna)
            
            self.tiempoInicio = time.time()
            self.tiempoHabilitado = True
            self.tiempo()
            self.inicio = True
        
        if self.listaBotones[fila][columna]['text'] == '' and self.listaBotones[fila][columna]['bg'] == 'grey':
            bombas_cercanas = self.contarBombasCercanas(index)
            self.listaBotones[fila][columna].config(bg='SystemButtonFace', text=str(bombas_cercanas) if bombas_cercanas > 0 else '')
            if bombas_cercanas == 0:
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = columna + dx, fila + dy
                        if 0 <= nx < columnas and 0 <= ny < filas:
                            adj_index = (ny, nx)
                            if adj_index not in self.bombas and self.listaBotones[ny][nx]['text'] == '' and self.listaBotones[ny][nx]['bg'] == 'grey':
                                self.slotPulsado(adj_index)
            self.checkWin()

    def reassignBomb(self, fila, columna):
        filas, columnas = self.find_dimensions(self.current_difficulty)
        bomb_index = fila * columnas + columna
        self.bombas.remove(bomb_index)

        available_spots = set(range(self.current_difficulty)) - set(self.bombas) - {bomb_index}
        new_bomb = random.choice(list(available_spots))
        self.bombas.append(new_bomb)
        
        # Actualizar el comando del nuevo botón de bomba
        new_fila, new_columna = divmod(new_bomb, columnas)
        self.listaBotones[new_fila][new_columna].config(command=lambda i=new_bomb: self.revealBombas(self.bombas))
        
        # Eliminar el comando del botón donde se quitó la bomba
        self.listaBotones[fila][columna].config(command=lambda: None)

    def colocarBandera(self, index):
        fila, columna = index
        if self.listaBotones[fila][columna]['bg'] == 'grey':
            if self.flags > 0:
                self.listaBotones[fila][columna].config(bg='orange', image=self.flag)
                self.flags -= 1
                self.updateFlagsCounter()
        elif self.listaBotones[fila][columna]['bg'] == 'orange':
            self.listaBotones[fila][columna].config(bg='grey', image=self.transparent_image)
            self.flags += 1
            self.updateFlagsCounter()

    def updateFlagsCounter(self):
        self.flags_counter.config(text="Banderas disponibles: " + str(self.flags))

    def resetGame(self):
        self.tiempoHabilitado = False
        self.contadorTiempo.config(text="Tiempo transcurrido: " + str(0), font=("Arial 15"))
        for fila in self.listaBotones:
            for boton in fila:
                boton.unbind('<Button-1>')
                boton.unbind('<Button-3>')
                boton.destroy()
        self.listaBotones = []
        self.frame.pack_forget()
        self.frame.pack()
        self.generarBotones()
        self.bombasRandom()
        self.inicio = False
        self.updateFlagsCounter()

def debugConsole():
    while True:
        command = input("Introduce un comando: ")
        try:
            exec(command)
        except Exception as e:
            l = traceback.format_exc()
            print(f"Error al ejecutar el comando: {e} {l}")

if __name__ == "__main__":
    hilo_consola = threading.Thread(target=debugConsole, daemon=True)
    hilo_consola.start()
    root = Tk() 
    app = Minesweeper(root)  
    root.mainloop()  
