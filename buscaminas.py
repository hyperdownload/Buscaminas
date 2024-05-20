from tkinter import *  # Importa todo del módulo tkinter para la interfaz gráfica
from tkinter import messagebox  # Importa el módulo messagebox de tkinter para mostrar mensajes emergentes
import random  # Importa el módulo random para la generación aleatoria de números
import time  # Importa el módulo time para manejar el tiempo

class Minesweeper:
    def __init__(self, root):
        self.root = root  # Inicializa la ventana principal de la aplicación
        self.frame = Frame(self.root)  # Crea un marco dentro de la ventana
        self.frame.pack()  # Empaqueta el marco en la ventana
        self.root.title("Siria Simulator")  # Establece el título de la ventana
        self.root.iconbitmap("img/bomba.ico")  # Establece el ícono de la ventana
        self.root.resizable(False, False)  # Evita que la ventana se pueda redimensionar
        self.frame.config(width=400, height=400)  # Configura el tamaño del marco
        
        self.navbar = Menu(self.root)
        self.root.config(menu=self.navbar)

        # Crea los elementos del menú
        self.file_menu = Menu(self.navbar, tearoff=0)
        self.file_menu.add_command(label="Nuevo Juego", command=self.resetGame)
        self.file_menu.add_command(label="Opciones", command=self.options)
        self.file_menu.add_command(label="Salir", command=self.root.quit)
        self.navbar.add_cascade(label="Archivo", menu=self.file_menu)
        
        self.difficulty = {"easy":40 , "normal": 48, "hard": 81}
        self.current_difficulty = self.difficulty["easy"]


        self.win = False  # Inicializa la variable para verificar si el jugador ha ganado
        self.listaBotones = []  # Inicializa una lista para almacenar los botones del tablero
        self.reset = False  # Inicializa una bandera para indicar si se ha reiniciado el juego
        self.inicio = False  # Inicializa una bandera para indicar si el juego ha comenzado
        self.tiempoInicio = time.time()  # Obtiene el tiempo actual al iniciar el juego
        self.banderasDisponibles = 10  # Establece la cantidad de banderas disponibles al inicio del juego
        self.bombas = []  # Inicializa una lista para almacenar las posiciones de las bombas
        self.contadorTiempo = Label(self.frame)  # Crea una etiqueta para mostrar el tiempo transcurrido
        self.contadorTiempo.grid(column=1, row=0, columnspan=4)  # Coloca la etiqueta en el marco
        self.contadorBanderas = Label(self.frame, text="Banderas disponibles: " + str(self.banderasDisponibles), font=("Arial 15"))  # Crea una etiqueta para mostrar la cantidad de banderas disponibles
        self.contadorBanderas.grid(column=5, row=0, columnspan=4)  # Coloca la etiqueta en el marco
        self.generarBotones()  # Genera los botones del tablero
        self.bombasRandom()  # Genera las posiciones aleatorias de las bombas
        self.tiempoHabilitado = False  # Inicializa una bandera para habilitar el tiempo de juego

        self.bomba_img = PhotoImage(file="img\\bomba3.png")
        self.bandera = PhotoImage(file="img\\bandera.png")

    def options(self):
        self.ventana_opciones = Toplevel(self.root)  # Crea una nueva ventana
        self.ventana_opciones.title("Opciones")  # Establece el título de la ventana
        self.ventana_opciones.geometry("300x200")  # Establece el tamaño de la ventana

        # Define las opciones que se mostrarán en el OptionMenu
        opciones = ["easy", "normal", "hard"]

        # Crea una variable de control para almacenar la opción seleccionada
        opcion_seleccionada = StringVar(self.ventana_opciones)
        opcion_seleccionada.set(self.current_difficulty)  # Establece la opción por defecto

        # Define una función para manejar la selección de una opción
        def seleccionar_opcion(opcion):
            self.current_difficulty=self.difficulty[opcion]
            self.resetGame()
        # Crea el OptionMenu y lo añade a la ventana de opciones
        option_menu = OptionMenu(self.ventana_opciones, opcion_seleccionada, *opciones, command=seleccionar_opcion)
        option_menu.pack()

        boton_cerrar = Button(self.ventana_opciones, text="Cerrar", command=self.ventana_opciones.destroy)
        boton_cerrar.pack()
    def tiempo(self):
        if self.tiempoHabilitado:
            tiempo_actual = int(time.time() - self.tiempoInicio)
            self.contadorTiempo.config(text="Tiempo transcurrido: " + str(tiempo_actual), font=("Arial 15"))
            self.root.after(1000, self.tiempo)  # Actualiza el tiempo cada segundo

    def generarBotones(self):
        for c in range(self.current_difficulty):  # Crea botones en un tablero segun la dificultad
            btn = Button(self.frame, width=6, height=3, text="", font=("Arial 12 bold"), bg="grey")  # Crea un botón con un tamaño y estilo específicos
            btn.bind('<Button-1>', lambda event, c=c: self.slotPulsado(c))  # Asocia el evento de clic izquierdo del ratón a la función slotPulsado
            btn.bind('<Button-3>', lambda event, c=c: self.colocarBandera(c))  # Asocia el evento de clic derecho del ratón a la función colocarBandera
            self.listaBotones.append(btn)  # Agrega el botón a la lista de botones
            # Calcula la fila y columna correspondiente a la posición actual del botón en el tablero
            if self.current_difficulty == self.difficulty["easy"]:
                row, col = divmod(c, 8)
            elif self.current_difficulty == self.difficulty["normal"]:
                row, col = divmod(c, 9)
            elif self.current_difficulty == self.difficulty["hard"]:
                row, col = divmod(c, 14)
            btn.grid(column=col + 1, row=row + 1)  # Ubica el botón en el tablero

    def bombasRandom(self):
        self.bombas = random.sample(range(self.current_difficulty), int(self.current_difficulty/4))  # Genera 10 posiciones aleatorias para las bombas en el tablero de 9x9
        print(self.bombas)  # Imprime las posiciones de las bombas en la consola (para fines de depuración)
        for i in self.bombas:
            self.listaBotones[i].config(command=lambda i=i: self.revealBombas(self.bombas))  # Configura los botones con bombas para ejecutar la función revealBombas al hacer clic

    def revealBombas(self, index):
        for i in (index):
            self.listaBotones[i].config(bg='red', image=self.bomba_img, width=64, height=65)  # Cambia el color del botón a rojo y muestra una "B" para indicar una bomba
        self.tiempoHabilitado = False  # Deshabilita el tiempo de juego
        messagebox.showinfo("Game Over", "Has pulsado una bomba!")  # Muestra un mensaje de juego perdido
        self.resetGame()  # Reinicia el juego

    def find_factors(self,n):
        factors = [(i, n//i) for i in range(1, int(n**0.5) + 1) if n % i == 0]
        return factors

    def find_dimensions(self,n):
        factors = self.find_factors(n)
        length, width = min(factors, key=lambda x: x[1] - x[0])
        return length, width
    
    def contarBombasCercanas(self, index):
        count = 0  # Inicializa el contador de bombas cercanas a cero
        x, y= self.find_dimensions(self.current_difficulty)
        print(x, y)
        for dy in (-1, 0, 1):  # Itera sobre los desplazamientos verticales
            for dx in (-1, 0, 1):  # Itera sobre los desplazamientos horizontales
                if dx == 0 and dy == 0:
                    continue  # Salta la iteración si el desplazamiento es cero en ambas direcciones (la misma casilla)
                nx, ny = index % 9 + dx, index // 9 + dy  # Calcula las coordenadas de la casilla vecina
                if 0 <= nx < 9 and 0 <= ny < 9:  # Verifica si las coordenadas están dentro del tablero
                    if (ny * 9 + nx) in self.bombas:  # Verifica si la casilla vecina contiene una bomba
                        count += 1  # Incrementa el contador si hay una bomba en la casilla vecina
        return count  # Devuelve el número total de bombas cercanas a la casilla

    def slotPulsado(self, index):
        if self.listaBotones[index]['text'] == '' and self.listaBotones[index]['bg'] == 'grey':
            bombas_cercanas = self.contarBombasCercanas(index)  # Cuenta las bombas cercanas al botón pulsado
            self.listaBotones[index].config(bg='SystemButtonFace', text=str(bombas_cercanas) if bombas_cercanas > 0 else '')  # Cambia el color de fondo del botón y muestra el número de bombas cercanas
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = index % 9 + dx, index // 9 + dy
                    if 0 <= nx < 9 and 0 <= ny < 9:
                        adj_index = ny * 9 + nx
                        if adj_index not in self.bombas and self.listaBotones[adj_index]['text'] == '' and self.listaBotones[adj_index]['bg'] == 'grey':
                            bombas_cercanas = self.contarBombasCercanas(adj_index)
                            if bombas_cercanas == 0:  # Solo activa los botones adyacentes si no tienen bombas cercanas
                                self.listaBotones[adj_index].config(bg='SystemButtonFace', text=str(bombas_cercanas) if bombas_cercanas > 0 else '')
                                self.slotPulsado(adj_index)
            self.tiempoHabilitado = True  # Habilita el tiempo de juego
            if not self.inicio:
                self.tiempoInicio = time.time()  # Inicia el contador de tiempo al comenzar el juego
                self.tiempoHabilitado = True
                self.tiempo()  # Comienza a contar el tiempo
                self.inicio = True

    def colocarBandera(self, index):
        if self.listaBotones[index]['bg'] == 'grey':
            if self.banderasDisponibles > 0:
                self.listaBotones[index].config(bg='orange', image=self.bandera, width=64, height=65)  # Cambia el color de fondo del botón a naranja y muestra una "F" para indicar una bandera
                self.banderasDisponibles -= 1  # Decrementa la cantidad de banderas disponibles
                self.actualizarContadorBanderas()  # Actualiza el contador de banderas disponibles
        elif self.listaBotones[index]['text'] == 'F':
            self.listaBotones[index].config(bg='grey', text='')  # Restaura el color de fondo del botón a gris y elimina el texto de la bandera
            self.banderasDisponibles += 1  # Incrementa la cantidad de banderas disponibles
            self.actualizarContadorBanderas()  # Actualiza el contador de banderas disponibles

    def actualizarContadorBanderas(self):
        self.contadorBanderas.config(text="Banderas disponibles: " + str(self.banderasDisponibles))  # Actualiza el texto del contador de banderas disponibles

    def resetGame(self):
        self.listaBotones.clear()  # Borra la lista de botones
        self.generarBotones()  # Genera nuevamente los botones del tablero
        self.bombasRandom()  # Coloca las bombas en posiciones aleatorias
        self.inicio = False  # Restablece la bandera de inicio del juego
        self.banderasDisponibles = 10  # Restablece la cantidad de banderas disponibles
        self.actualizarContadorBanderas()  # Actualiza el contador de banderas disponibles

if __name__ == "__main__":
    root = Tk()  # Crea una ventana principal
    app = Minesweeper(root)  # Inicia la aplicación del buscaminas
    root.mainloop()  # Inicia el bucle principal de la interfaz gráfica
