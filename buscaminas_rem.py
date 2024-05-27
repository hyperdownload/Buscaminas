from tkinter import *  # Importa todo del módulo tkinter para la interfaz gráfica
from tkinter import messagebox  # Importa el módulo messagebox de tkinter para mostrar mensajes emergentes
import tkinter as tk # sino no funca
import random  # Importa el módulo random para la generación aleatoria de números
import time  # Importa el módulo time para manejar el tiempo
from data import Data
class Minesweeper:
    def __init__(self, root):
        self.root = root  # Inicializa la ventana principal de la aplicación
        self.frame = Frame(self.root)  # Crea un marco dentro de la ventana
        self.frame.pack()  # Empaqueta el marco en la ventana
        self.root.title("Siria Simulator")  # Establece el título de la ventana
        self.root.iconbitmap("img/bomba.ico")  # Establece el ícono de la ventana
        self.root.resizable(False, False)  # Evita que la ventana se pueda redimensionar
        #ahora se configura la posicion de la ventana
        self.frame.config(width=400, height=400)  # Configura el tamaño del marco
        self.navbar = Menu(self.root)
        self.root.config(menu=self.navbar)
        self.transparent_image = PhotoImage(width=1, height=1)
        
        self.player=tk.StringVar()
        self.player.set("Player")
        self.file_path = 'stats.csv'
        # Crea los elementos del menú
        self.file_menu = Menu(self.navbar, tearoff=0)
        self.file_menu.add_command(label="Nuevo Juego", command=self.resetGame)
        self.file_menu.add_command(label="Stats", command=self.stats)
        self.file_menu.add_command(label="Opciones", command=self.options)
        self.file_menu.add_command(label="Salir", command=self.root.quit)
        self.navbar.add_cascade(label="Archivo", menu=self.file_menu)

        self.difficulty = {"easy": 40, "normal": 64, "hard": 81}
        self.current_difficulty = self.difficulty["easy"]

        self.win = False  # Inicializa la variable para verificar si el jugador ha ganado
        self.listaBotones = []  # Inicializa una lista para almacenar los botones del tablero
        self.reset = False  # Inicializa una bandera para indicar si se ha reiniciado el juego
        self.inicio = False  # Inicializa una bandera para indicar si el juego ha comenzado
        self.tiempoInicio = time.time()  # Obtiene el tiempo actual al iniciar el juego
        self.flags = 0  # Establece la cantidad de banderas disponibles al inicio del juego
        self.bombas = []  # Inicializa una lista para almacenar las posiciones de las bombas
        self.contadorTiempo = Label(self.frame)  # Crea una etiqueta para mostrar el tiempo transcurrido
        self.contadorTiempo.grid(column=1, row=0, columnspan=4)  # Coloca la etiqueta en el marco
        self.flags_counter = Label(self.frame, text="Banderas disponibles: " + str(self.flags), font=("Arial 15"))  # Crea una etiqueta para mostrar la cantidad de banderas disponibles
        self.flags_counter.grid(column=5, row=0, columnspan=4)  # Coloca la etiqueta en el marco
        self.generarBotones()  # Genera los botones del tablero
        self.bombasRandom()  # Genera las posiciones aleatorias de las bombas
        self.tiempoHabilitado = False  # Inicializa una bandera para habilitar el tiempo de juego
        self.bomba_img = PhotoImage(file="img\\bomba3.png")
        self.bandera = PhotoImage(file="img\\bandera.png")
        
    def stats(self):
        self.statsWindow = Toplevel(self.root)
        self.statsWindow.title("Estadísticas")
        self.statsWindow.geometry("300x200")
        
        # Obtiene las estadísticas usando el módulo Data
        stats = Data.getStats(self.file_path)
        
        # Crear una etiqueta para cada fila de estadísticas
        for i, (username, score) in enumerate(stats):
            Label(self.statsWindow, text=f"Jugador:{username}").grid(row=i, column=0, padx=10, pady=5)
            Label(self.statsWindow, text=f"Tiempo:{score}s").grid(row=i, column=1, padx=10, pady=5)
    
    def options(self):
        self.ventana_opciones = Toplevel(self.root)  # Crea una nueva ventana
        self.ventana_opciones.title("Opciones")  # Establece el título de la ventana
        self.ventana_opciones.geometry("300x200")  # Establece el tamaño de la ventana

        # Define las opciones que se mostrarán en el OptionMenu
        opciones = ["easy", "normal", "hard"]

        # Crea una variable de control para almacenar la opción seleccionada
        opcion_seleccionada = StringVar(self.ventana_opciones)
        opcion_seleccionada.set("Easy" if self.current_difficulty == 40 else "Normal" if self.current_difficulty == 64 else "Hard" if self.current_difficulty == 81 else "Undefined")

        # Define una función para manejar la selección de una opción
        def seleccionar_opcion(opcion):
            self.current_difficulty = self.difficulty[opcion]
            self.resetGame()

        # Crea una etiqueta para indicar que las opciones representan la dificultad
        label_dificultad = Label(self.ventana_opciones, text="Dificultad:", font=("Arial 12"))
        label_dificultad.pack(side=LEFT)

        # Crea el OptionMenu y lo añade a la ventana de opciones
        option_menu = OptionMenu(self.ventana_opciones, opcion_seleccionada, *opciones, command=seleccionar_opcion)
        option_menu.pack(side=LEFT)

        # Crea un campo de entrada
        self.entry = Entry(self.ventana_opciones, width=30, textvariable=self.player)
        self.entry.pack(pady=20)

        # Define una función para manejar la acción del botón "Aplicar"
        def aplicar_input():
            input_text = self.entry.get()
            # Aquí puedes hacer lo que necesites con el contenido del input
            messagebox.showinfo("Options changed", "Los valores se ajustaron correctamente!")

        # Crea el botón "Aplicar" y lo añade a la ventana de opciones
        boton_aplicar = Button(self.ventana_opciones, text="Aplicar", command=aplicar_input)
        boton_aplicar.pack(pady=10)

        # Crea el botón de cerrar y lo añade a la ventana de opciones
        boton_cerrar = Button(self.ventana_opciones, text="Cerrar", command=self.ventana_opciones.destroy)
        boton_cerrar.pack(side=BOTTOM)

    def tiempo(self):
        if self.tiempoHabilitado:
            self.tiempo_actual = int(time.time() - self.tiempoInicio)
            self.contadorTiempo.config(text="Tiempo transcurrido: " + str(self.tiempo_actual), font=("Arial 15"))
            self.root.after(1000, self.tiempo)  # Actualiza el tiempo cada segundo

    def generarBotones(self):
        filas, columnas = self.find_dimensions(self.current_difficulty)
        self.listaBotones = []  # Inicializa la lista de botones

        for i in range(filas):
            fila_botones = []  # Inicializa una nueva fila de botones
            for j in range(columnas):
                btn = Button(self.frame, width=6, height=3, text="", font=("Arial 12 bold"), bg="grey")
                btn.bind('<Button-1>', lambda event, c=(i, j): self.slotPulsado(c))
                btn.bind('<Button-3>', lambda event, c=(i, j): self.colocarBandera(c))
                btn.grid(column=j + 1, row=i + 1, sticky='nsew')  # Ubica el botón en el tablero
                fila_botones.append(btn)  # Agrega el botón a la fila de botones
            self.listaBotones.append(fila_botones)  # Agrega la fila de botones a la lista de botones

        # Asegura que los botones se expandan para llenar el espacio disponible
        for i in range(columnas):
            self.frame.grid_columnconfigure(i, weight=1)
        for i in range(filas):
            self.frame.grid_rowconfigure(i, weight=1)

    def bombasRandom(self):
        total_casillas = self.current_difficulty
        filas, columnas = self.find_dimensions(total_casillas)
        self.bombas = random.sample(range(total_casillas), total_casillas // 14)
        #print(self.bombas)
        self.setFlags(len(self.bombas)) 
        for bomba in self.bombas:
            fila, columna = divmod(bomba, columnas)
            self.listaBotones[fila][columna].config(command=lambda i=bomba: self.revealBombas(self.bombas))

    def checkWin(self):
        # Variables para contar el número de botones descubiertos y el total de botones sin minas
        buttons_discovered = 0
        total_safe_buttons = self.current_difficulty - len(self.bombas)
        
        for i in range(len(self.listaBotones)):
            for j in range(len(self.listaBotones[i])):
                button = self.listaBotones[i][j]
                # Comprobar si el botón no tiene bomba y está descubierto
                if (i * len(self.listaBotones[i]) + j) not in self.bombas and button['bg'] != 'grey':
                    buttons_discovered += 1
        
        # Si el número de botones descubiertos es igual al número total de botones sin minas, el jugador gana
        if buttons_discovered == total_safe_buttons:
            messagebox.showinfo("Victory", "¡Has ganado el juego!")
            self.tiempoHabilitado = False
            Data.addStats(self.file_path,self.player.get(), self.tiempo_actual)

    def setFlags(self, flags):
        self.flags = flags
        self.flags_counter.config(text="Banderas disponibles: " + str(flags))
        self.updateFlagsCounter()

    def revealBombas(self, index):
        filas, columnas = self.find_dimensions(self.current_difficulty)
        for i in index:
            fila, columna = divmod(i, columnas)
            self.listaBotones[fila][columna].config(bg='red', image=self.bomba_img, width=64, height=65)
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
        count = 0  # Inicializa el contador de bombas cercanas a cero
        filas, columnas = self.find_dimensions(self.current_difficulty)
        fila, columna = index
        for dy in (-1, 0, 1):  # Itera sobre los desplazamientos verticales
            for dx in (-1, 0, 1):  # Itera sobre los desplazamientos horizontales
                if dx == 0 and dy == 0:
                    continue  # Salta la iteración si el desplazamiento es cero en ambas direcciones (la misma casilla)
                nx, ny = columna + dx, fila + dy  # Calcula las coordenadas de la casilla vecina
                if 0 <= nx < columnas and 0 <= ny < filas:  # Verifica si las coordenadas están dentro del tablero
                    if (ny * columnas + nx) in self.bombas:  # Verifica si la casilla vecina contiene una bomba
                        count += 1  # Incrementa el contador si hay una bomba en la casilla vecina
        return count  # Devuelve el número total de bombas cercanas a la casilla

    def slotPulsado(self, index):
        filas, columnas = self.find_dimensions(self.current_difficulty)
        fila, columna = index
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
            self.tiempoHabilitado = True
            if not self.inicio:
                self.tiempoInicio = time.time()
                self.tiempoHabilitado = True
                self.tiempo()
                self.inicio = True
            self.checkWin()

    def colocarBandera(self, index):
        fila, columna = index
        if self.listaBotones[fila][columna]['bg'] == 'grey':
            if self.flags > 0:
                self.listaBotones[fila][columna].config(bg='orange', image=self.bandera, width=64, height=65)
                self.flags -= 1
                self.updateFlagsCounter()
        elif self.listaBotones[fila][columna]['bg'] == 'orange':
            self.listaBotones[fila][columna].config(bg='grey', image=self.transparent_image, width=64, height=65)
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
        self.win = False  # Resetea el estado de la victoria
        self.updateFlagsCounter()

if __name__ == "__main__":
    root = Tk()  # Crea una ventana principal
    app = Minesweeper(root)  # Inicia la aplicación del buscaminas
    root.mainloop()  # Inicia el bucle principal de la interfaz gráfica