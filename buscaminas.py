import os
import time 
import json
import random 
import threading
import traceback
import tkinter as tk 
import importlib.util
from tkinter import *  
from tkinter import ttk
from data import Data, DataTxt, Adds
from tkinter import messagebox 
try:
    from PIL import Image, ImageTk
except:
    print("Descargando pillow...")
    os.system("pip install pillow")
    from PIL import Image, ImageTk
class ModManager:
    def __init__(self, mod_directory="mods")->None:
        try:
            Adds.debug("Iniciando ModLoader...")
            self.mod_directory = mod_directory
            self.mods = []
            self.load_mods()
            Adds.debug("Mod loader cargado!")
        except Exception as e:
            Adds.warning("Hubo un error en el constructor de ModLoader, mas informacion:\n"
            f"{e}")
            messagebox.showerror("Error", "Hubo un error cargando los mods debido a un error o incompatibilidad en el mod, se iniciara en vanilla.")

    def load_mods(self)->None:
        Adds.debug("Cargando mods...")
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
        Adds.debug("Aplicando mods...")
        for mod in self.mods:
            if hasattr(mod, 'apply_mod'):
                mod.apply_mod(game)

class Minesweeper:
    def __init__(self, root)->None:
        """
        Esta es la función de inicialización para la clase del juego "Siria Simulator". 
        Configura la ventana principal, carga las imágenes y establece las variables iniciales.

        Parámetros:
        root (Tk): La ventana principal del juego.

        Ejemplo:
        >>> game = Game(root)
        # Inicializa el juego con la ventana principal 'root'.
        """
        # Variables de personalizacion grafica
        self.buttonColor = "#000000"
        self.UIbuttonColor = "#000000"
        self.buttonFgColor = "#FFFFFF"
        self.flagButtonColor = "#FFA500"
        self.pressedButtonColor = "#b4b4b4"
        self.labelColor = "#000000"
        self.labelFgColor = "#FFFFFF"
        self.windowColor = "#000000"
        self.windowFgColor = "#FFFFFF"
        self.entryColor = "#000000"
        self.entryFgColor = "#FFFFFF"
        self.frameColor = "#000000"
        
        self.loadSettings() # Carga a las variables de personalizacion sus datos
        
        self.root = root 
        self.frame = Frame(self.root, bg=self.frameColor)  # Crea un nuevo marco en la ventana principal
        self.frame.pack()  # Empaqueta el marco para que se muestre en la ventana
        self.root.title("Siria Simulator")  # Establece el título de la ventana
        self.root.iconbitmap("img/bomba.ico")  # Establece el ícono de la ventana
        self.root.resizable(False, False)  # Hace que la ventana no sea redimensionable
        self.frame.config(width=400, height=400)  # Configura el tamaño del marco
        self.navbar = Menu(self.root)  # Crea una nueva barra de navegación
        self.root.config(menu=self.navbar)  # Configura la barra de navegación de la ventana
        self.transparent_image = PhotoImage(width=1, height=1)  # Crea una imagen transparente para usarla como imagen predeterminada en los botones
        
        # Mod Manager
        Adds.debug("Cargando mods...")
        self.mod_manager = ModManager()  # Crea un nuevo administrador de mods
        self.mod_manager.apply_mods(self)  # Aplica los mods al juego
        
        self.player=tk.StringVar()  # Crea una variable de cadena para almacenar el nombre del jugador
        self.player.set("Player")  # Establece el nombre del jugador por defecto como "Player"
        #Actualmente existe stats.csv y stats.txt, funcionan en ambos pero debe de ser actualizado en el codigo de DataTxt a Data
        self.file_path = 'stats.txt'  # Establece la ruta del archivo donde se almacenan las estadísticas
        self.file_menu = Menu(self.navbar, tearoff=0)  # Crea un nuevo menú en la barra de navegación
        self.file_menu.add_command(label="Nuevo Juego", command=self.resetGame)  # Agrega un comando para iniciar un nuevo juego
        self.file_menu.add_command(label="Stats", command=self.stats)  # Agrega un comando para mostrar las estadísticas
        self.file_menu.add_command(label="Opciones", command=self.options)  # Agrega un comando para abrir la ventana de opciones
        self.file_menu.add_command(label="Personalizar objetos", command=self.personalization) # Agrega un comando para abrir una ventana para personalizar lo visual
        self.file_menu.add_command(label="Salir", command=self.root.quit)  # Agrega un comando para salir del juego
        self.navbar.add_cascade(label="Archivo", menu=self.file_menu)  # Agrega el menú a la barra de navegación

        self.difficulty = {"Easy": 40, "Normal": 64, "Hard": 81, "Imposible":150}  # Define los niveles de dificultad
        self.current_difficulty = self.difficulty["Easy"]  # Establece la dificultad actual como "Easy"

        self.buttonsList = []  # Crea una lista para almacenar los botones del juego
        self.reset = False  # Establece la variable de reinicio en False
        self.inicio = False  # Establece la variable de inicio en False
        self.timeInicio = time.time()  # Almacena el tiempo de inicio del juego
        self.flags = 0  # Inicializa el contador de banderas en 0
        self.bombs = []  # Crea una lista para almacenar las bombas

        self.contadortime = Label(self.frame)  # Crea una etiqueta para mostrar el tiempo
        self.contadortime.grid(column=1, row=0, columnspan=4)  # Coloca la etiqueta en el marco
        self.contadortime.config(text="Tiempo transcurrido: " + "00", font=("Arial 15"), bg=self.labelColor, fg=self.labelFgColor)
        self.flags_counter = Label(self.frame, text="Banderas disponibles:" + str(self.flags), font=("Arial 15"), bg=self.labelColor, fg=self.labelFgColor)  # Crea una etiqueta para mostrar las banderas disponibles
        self.flags_counter.grid(column=5, row=0, columnspan=4)  # Coloca la etiqueta en el marco
        
        self.root.config(bg=self.windowColor)
        
        #self.contadortime = Label(self.frame)  # Crea una etiqueta para mostrar el tiempo
        #self.contadortime.place(x=0, y=20)  # Coloca la etiqueta en el marco en las coordenadas (50, 20)

        #self.flags_counter = Label(self.frame, text="Banderas disponibles:" + str(self.flags), font=("Arial 15"))  # Crea una etiqueta para mostrar las banderas disponibles
        #self.flags_counter.place(x=0, y=20)  # Coloca la etiqueta en el marco en las coordenadas (200, 20)

        self.timeHabilited = False  # Establece la variable de tiempo habilitado en False
        # Imagenes originales
        img_bomb_original = Image.open("img\\bomba3.png")  # Abre la imagen original de la bomba
        img_flag_original = Image.open("img\\bandera.png")  # Abre la imagen original de la bandera

        # Redimensionamiento de imagenes
        img_bomb_rescaled = img_bomb_original.resize((50, 50), Image.Resampling.LANCZOS)  # Redimensiona la imagen de la bomba
        img_flag_rescaled = img_flag_original.resize((50, 50), Image.Resampling.LANCZOS)  # Redimensiona la imagen de la bandera

        # Conversion a un formato que acepte tk
        self.bomb = ImageTk.PhotoImage(img_bomb_rescaled)  # Convierte la imagen de la bomba a un formato que Tkinter pueda manejar
        self.flag = ImageTk.PhotoImage(img_flag_rescaled)  # Convierte la imagen de la bandera a un formato que Tkinter pueda manejar
        
        #Opciones
        self.isShakeWindowEnabled = tk.BooleanVar()  # Crea una variable booleana para almacenar si la opción de agitar la ventana está habilitada
        self.isShakeWindowEnabled.set(True)  # Establece la opción de agitar la ventana en True
        self.defaultNoInstaLoseAttemps = 2  # Establece el número predeterminado de intentos antes de perder instantáneamente
        
        self.currentAttemps = self.defaultNoInstaLoseAttemps  # Establece los intentos actuales en el número predeterminado de intentos
        
        self.generateButtons()  # Genera los botones del juego
        self.bombsRandom()  # Coloca las bombas de manera aleatoria 
        
    def loadSettings(self) -> None:
        """
        Carga la configuración de colores desde el archivo "config.json".

        No recibe parámetros.

        No retorna ningún valor.
        """
        try:
            Adds.debug("Cargando configuracion...")
            with open('config.json', 'r') as f:
                # Abre el archivo "config.json" en modo lectura ('r').
                # El objeto 'f' representa el archivo abierto.
                data = json.load(f)
                # Carga los datos del archivo JSON en un diccionario llamado 'data'.
                # Si una clave no existe, se utiliza el valor por defecto (segundo argumento).
                self.buttonColor = data.get('buttonColor', self.buttonColor)
                self.UIbuttonColor = data.get('UIbuttonColor', self.UIbuttonColor)
                self.buttonFgColor = data.get('buttonFgColor', self.buttonFgColor)
                self.flagButtonColor = data.get('flagButtonColor', self.flagButtonColor)
                self.pressedButtonColor = data.get('pressedButtonColor', self.pressedButtonColor)
                self.labelColor = data.get('labelColor', self.labelColor)
                self.labelFgColor = data.get('labelFgColor', self.labelFgColor)
                self.windowColor = data.get('windowColor', self.windowColor)
                self.windowFgColor = data.get('windowFgColor', self.windowFgColor)
                self.entryColor = data.get('entryColor', self.entryColor)
                self.entryFgColor = data.get('entryFgColor', self.entryFgColor)
                self.frameColor = data.get('frameColor', self.frameColor)
        except FileNotFoundError:
            Adds.warning("No se encontró el archivo config.json. Usando valores por defecto.")
            # Imprime un mensaje si el archivo no existe.
        except json.JSONDecodeError:
            Adds.warning("Error al decodificar JSON. Usando valores por defecto.")
            # Imprime un mensaje si hay un error al decodificar el JSON.

    def saveSettings(self)->None:
        """
        Guarda la configuración de colores en un archivo JSON llamado "config.json".

        No recibe parámetros.

        No retorna ningún valor.
        """
        result = messagebox.askyesno("Confirmar", "Para aplicar los cambios se reiniciara la aplicacion.")
        if result:
            Adds.debug("Guardando configuracion")

            # Obtener datos de los Entry
            self.buttonColor = self.entryButtonColor.get()
            self.UIbuttonColor = self.entryUIbuttonColor.get()
            self.buttonFgColor = self.entryButtonBgColor.get()
            self.flagButtonColor = self.entryFlagButtonColor.get()
            self.pressedButtonColor = self.entryPressedButtonColor.get()
            self.labelColor = self.entryLabelColor.get()
            self.labelFgColor = self.entryLabelBgColor.get()
            self.windowColor = self.entryWindowColor.get()
            self.windowFgColor = self.entryWindowColor.get()
            self.entryColor = self.entryEntryColor.get()
            self.entryFgColor = self.entryEntryTxColor.get()
            self.frameColor = self.entryFrameColor.get()

            # Guardar datos en JSON
            data = {
                'buttonColor': self.buttonColor,
                'UIbuttonColor': self.UIbuttonColor,
                'buttonFgColor': self.buttonFgColor,
                'flagButtonColor': self.flagButtonColor,
                'pressedButtonColor': self.pressedButtonColor,
                'labelColor': self.labelColor,
                'labelFgColor': self.labelFgColor,
                'windowColor': self.windowColor,
                'windowFgColor': self.windowFgColor,
                'entryColor': self.entryColor,
                'entryFgColor': self.entryFgColor,
                'frameColor': self.frameColor,
            }
            with open('config.json', 'w') as f:
                Adds.debug("Escribiendo json...")
                # Abre el archivo "config.json" en modo escritura ('w').
                # El archivo se crea si no existe o se sobrescribe si ya existe.
                # El objeto 'f' representa el archivo abierto.
                json.dump(data, f, indent=4)
                # Escribe los datos (diccionario 'data') en el archivo en formato JSON.
                # El argumento 'indent=4' agrega sangría para una mejor legibilidad.
            Adds.debug("Configuración guardada correctamente.")
            self.root.destroy()
            hilo_consola = threading.Thread(target=debugConsole, daemon=True)
            hilo_consola.start()
            root = Tk() 
            app = Minesweeper(root)  
            root.mainloop() 
        else:
            pass

    def personalization(self) -> None:
        """
        Crea una ventana emergente para personalizar los colores de los botones y otros elementos de la interfaz.
        """
        self.personalizationWindow = Toplevel(self.root)
        self.personalizationWindow.title("Personalizar objetos")
        self.personalizationWindow.geometry("400x650")
        self.personalizationWindow.config(bg=self.windowColor)

        # Crear un Canvas para contener todo el contenido
        canvas = Canvas(self.personalizationWindow, bg=self.windowColor)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)

        # Añadir un Scrollbar
        scrollbar = Scrollbar(self.personalizationWindow, orient=VERTICAL, command=canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Configurar el Canvas para el Scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Frame interior dentro del Canvas
        interior_frame = Frame(canvas, bg=self.windowColor)
        canvas.create_window((0, 0), window=interior_frame, anchor='nw')

        # Sección de botones
        buttonSectionLabel = Label(interior_frame, text="Botones", font=("Arial", 12, "bold"), bg=self.labelColor, fg=self.labelFgColor)
        buttonSectionLabel.grid(column=0, row=0, pady=10, padx=10, sticky=W)

        buttonColorLabel = Label(interior_frame, text="Color de Fondo:", font=("Arial", 10), bg=self.labelColor, fg=self.labelFgColor)
        buttonColorLabel.grid(column=0, row=1, padx=10, sticky=W)

        self.entryButtonColor = Entry(interior_frame, bg=self.entryColor, fg=self.entryFgColor)
        self.entryButtonColor.insert(0, self.buttonColor)
        self.entryButtonColor.grid(column=1, row=1, padx=10)

        buttonBgColorLabel = Label(interior_frame, text="Color de Texto:", font=("Arial", 10), bg=self.labelColor, fg=self.labelFgColor)
        buttonBgColorLabel.grid(column=0, row=2, padx=10, sticky=W)

        self.entryButtonBgColor = Entry(interior_frame, bg=self.entryColor, fg=self.entryFgColor)
        self.entryButtonBgColor.insert(0, self.buttonFgColor)
        self.entryButtonBgColor.grid(column=1, row=2, padx=10)

        # UI Botones
        UIbuttonSectionLabel = Label(interior_frame, text="Botones UI", font=("Arial", 12, "bold"), bg=self.labelColor, fg=self.labelFgColor)
        UIbuttonSectionLabel.grid(column=0, row=3, pady=10, padx=10, sticky=W)

        UIbuttonColorLabel = Label(interior_frame, text="Color de Fondo:", font=("Arial", 10), bg=self.labelColor, fg=self.labelFgColor)
        UIbuttonColorLabel.grid(column=0, row=4, padx=10, sticky=W)

        self.entryUIbuttonColor = Entry(interior_frame, bg=self.entryColor, fg=self.entryFgColor)
        self.entryUIbuttonColor.insert(0, self.UIbuttonColor)
        self.entryUIbuttonColor.grid(column=1, row=4, padx=10)

        UIbuttonBgColorLabel = Label(interior_frame, text="Color de Texto:", font=("Arial", 10), bg=self.labelColor, fg=self.labelFgColor)
        UIbuttonBgColorLabel.grid(column=0, row=5, padx=10, sticky=W)

        self.entryUIbuttonBgColor = Entry(interior_frame, bg=self.entryColor, fg=self.entryFgColor)
        self.entryUIbuttonBgColor.insert(0, self.buttonFgColor)
        self.entryUIbuttonBgColor.grid(column=1, row=5, padx=10)

        # Más secciones y entradas
        # Color de la bandera de botón
        flagButtonSectionLabel = Label(interior_frame, text="Botón de Bandera", font=("Arial", 12, "bold"), bg=self.labelColor, fg=self.labelFgColor)
        flagButtonSectionLabel.grid(column=0, row=6, pady=10, padx=10, sticky=W)

        flagButtonColorLabel = Label(interior_frame, text="Color de Fondo:", font=("Arial", 10), bg=self.labelColor, fg=self.labelFgColor)
        flagButtonColorLabel.grid(column=0, row=7, padx=10, sticky=W)

        self.entryFlagButtonColor = Entry(interior_frame, bg=self.entryColor, fg=self.entryFgColor)
        self.entryFlagButtonColor.insert(0, self.flagButtonColor)
        self.entryFlagButtonColor.grid(column=1, row=7, padx=10)

        flagButtonBgColorLabel = Label(interior_frame, text="Color de Texto:", font=("Arial", 10), bg=self.labelColor, fg=self.labelFgColor)
        flagButtonBgColorLabel.grid(column=0, row=8, padx=10, sticky=W)

        self.entryFlagButtonBgColor = Entry(interior_frame, bg=self.entryColor, fg=self.entryFgColor)
        self.entryFlagButtonBgColor.insert(0, self.buttonFgColor)
        self.entryFlagButtonBgColor.grid(column=1, row=8, padx=10)

        # Color del botón presionado
        pressedButtonSectionLabel = Label(interior_frame, text="Botón Presionado", font=("Arial", 12, "bold"), bg=self.labelColor, fg=self.labelFgColor)
        pressedButtonSectionLabel.grid(column=0, row=9, pady=10, padx=10, sticky=W)

        pressedButtonColorLabel = Label(interior_frame, text="Color de Fondo:", font=("Arial", 10), bg=self.labelColor, fg=self.labelFgColor)
        pressedButtonColorLabel.grid(column=0, row=10, padx=10, sticky=W)

        self.entryPressedButtonColor = Entry(interior_frame, bg=self.entryColor, fg=self.entryFgColor)
        self.entryPressedButtonColor.insert(0, self.pressedButtonColor)
        self.entryPressedButtonColor.grid(column=1, row=10, padx=10)

        pressedButtonBgColorLabel = Label(interior_frame, text="Color de Texto:", font=("Arial", 10), bg=self.labelColor, fg=self.labelFgColor)
        pressedButtonBgColorLabel.grid(column=0, row=11, padx=10, sticky=W)

        self.entryPressedButtonBgColor = Entry(interior_frame, bg=self.entryColor, fg=self.entryFgColor)
        self.entryPressedButtonBgColor.insert(0, self.buttonFgColor)
        self.entryPressedButtonBgColor.grid(column=1, row=11, padx=10)

        # Color de entry
        entrySectionLabel = Label(interior_frame, text="Entry", font=("Arial", 12, "bold"), bg=self.labelColor, fg=self.labelFgColor)
        entrySectionLabel.grid(column=0, row=12, pady=10, padx=10, sticky=W)

        entryColorLabel = Label(interior_frame, text="Color de Fondo:", font=("Arial", 10), bg=self.labelColor, fg=self.labelFgColor)
        entryColorLabel.grid(column=0, row=13, padx=10, sticky=W)

        self.entryEntryColor = Entry(interior_frame, bg=self.entryColor, fg=self.entryFgColor)
        self.entryEntryColor.insert(0, self.entryColor)
        self.entryEntryColor.grid(column=1, row=13, padx=10)

        entryBgColorLabel = Label(interior_frame, text="Color de Texto:", font=("Arial", 10), bg=self.labelColor, fg=self.labelFgColor)
        entryBgColorLabel.grid(column=0, row=14, padx=10, sticky=W)

        self.entryEntryTxColor = Entry(interior_frame, bg=self.entryColor, fg=self.entryFgColor)
        self.entryEntryTxColor.insert(0, self.entryFgColor)
        self.entryEntryTxColor.grid(column=1, row=14, padx=10)
        
        # Color de label
        labelSectionLabel = Label(interior_frame, text="Label", font=("Arial", 12, "bold"), bg=self.labelColor, fg=self.labelFgColor)
        labelSectionLabel.grid(column=0, row=15, pady=10, padx=10, sticky=W)

        labelColorLabel = Label(interior_frame, text="Color de Fondo:", font=("Arial", 10), bg=self.labelColor, fg=self.labelFgColor)
        labelColorLabel.grid(column=0, row=16, padx=10, sticky=W)

        self.entryLabelColor = Entry(interior_frame, bg=self.entryColor, fg=self.entryFgColor)
        self.entryLabelColor.insert(0, self.labelColor)
        self.entryLabelColor.grid(column=1, row=16, padx=10)

        labelBgColorLabel = Label(interior_frame, text="Color de Texto:", font=("Arial", 10), bg=self.labelColor, fg=self.labelFgColor)
        labelBgColorLabel.grid(column=0, row=17, padx=10, sticky=W)

        self.entryLabelBgColor = Entry(interior_frame, bg=self.entryColor, fg=self.entryFgColor)
        self.entryLabelBgColor.insert(0, self.labelFgColor)
        self.entryLabelBgColor.grid(column=1, row=17, padx=10)
        
        # Color de ventana
        windowSectionLabel = Label(interior_frame, text="Ventana", font=("Arial", 12, "bold"), bg=self.labelColor, fg=self.labelFgColor)
        windowSectionLabel.grid(column=0, row=18, pady=10, padx=10, sticky=W)

        windowColorLabel = Label(interior_frame, text="Color de Fondo:", font=("Arial", 10), bg=self.labelColor, fg=self.labelFgColor)
        windowColorLabel.grid(column=0, row=19, padx=10, sticky=W)

        self.entryWindowColor = Entry(interior_frame, bg=self.entryColor, fg=self.entryFgColor)
        self.entryWindowColor.insert(0, self.windowColor)
        self.entryWindowColor.grid(column=1, row=19, padx=10)
        
        frameSectionLabel = Label(interior_frame, text="Frame", font=("Arial", 12, "bold"), bg=self.labelColor, fg=self.labelFgColor)
        frameSectionLabel.grid(column=0, row=20, pady=10, padx=10, sticky=W)
        
        frameColorLabel = Label(interior_frame, text="Color de Fondo:", font=("Arial", 10), bg=self.labelColor, fg=self.labelFgColor)
        frameColorLabel.grid(column=0, row=21, padx=10, sticky=W)
        
        self.entryFrameColor = Entry(interior_frame, bg=self.entryColor, fg=self.entryFgColor)
        self.entryFrameColor.insert(0, self.labelFgColor)
        self.entryFrameColor.grid(column=1, row=21, padx=10)

        # Botón de guardar configuración
        saveButton = Button(interior_frame, text="Guardar", command=self.saveSettings, font=("Arial", 10), bg=self.UIbuttonColor, fg=self.buttonFgColor)
        saveButton.grid(column=1, row=23, pady=20)

        # Ajustar tamaño del Canvas al contenido
        interior_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def difficultyToString(self, difficulty)->str:
        """
        Esta función convierte un valor de dificultad numérico en una cadena de texto.

        Parámetros:
        difficulty (int): Un valor numérico que representa la dificultad. Este valor debe ser una clave en el diccionario self.difficulty.

        Retorna:
        str: Una cadena de texto que representa la dificultad. Los posibles valores de retorno son "Easy", "Normal", "Hard", y "Imposible".

        Ejemplo:
        >>> difficultyToString(self, self.difficulty["Easy"])
        'Easy'
        """
        if difficulty == self.difficulty["Easy"]:
            return "Easy"
        elif difficulty == self.difficulty["Normal"]:
            return "Normal"
        elif difficulty == self.difficulty["Hard"]:
            return "Hard"
        elif difficulty == self.difficulty["Imposible"]:
            return "Imposible"
        
    def stats(self)->None:
        """
        Esta función muestra una ventana con las estadísticas de los jugadores.

        Crea una nueva ventana (Toplevel) en la que se muestran las estadísticas de los jugadores,
        incluyendo el nombre del jugador, el tiempo y la dificultad.

        Las estadísticas se obtienen a través de la función getStats del módulo Data, que toma como 
        parámetro la ruta del archivo donde se almacenan las estadísticas.

        """
        self.statsWindow = Toplevel(self.root)
        self.statsWindow.title("Estadísticas")
        self.statsWindow.geometry("300x300")
        self.statsWindow.config(bg=self.windowColor)
        
        #Este codigo es para aplicar en csv
        #stats = Data.getStats(self.file_path)
        stats = DataTxt.getStats(self.file_path)

        for i, (username, score, dif) in enumerate(stats):
            Label(self.statsWindow, text=f"Jugador:{username}", bg=self.labelColor, fg=self.labelFgColor).grid(row=i, column=0, padx=10, pady=5)
            Label(self.statsWindow, text=f"Time:{score}s", bg=self.labelColor, fg=self.labelFgColor).grid(row=i, column=1, padx=10, pady=5)
            Label(self.statsWindow, text=f"Dificultad:{dif}", bg=self.labelColor, fg=self.labelFgColor).grid(row=i, column=2, padx=10, pady=5)

    
    def options(self) -> None:
        """
        Esta función abre una ventana de opciones donde el usuario puede cambiar la dificultad del juego,
        ingresar su nombre y habilitar o deshabilitar el movimiento de la ventana al perder.

        La ventana de opciones incluye un menú desplegable para seleccionar la dificultad, un campo de entrada
        para el nombre del jugador, un botón para aplicar los cambios, un checkbox para habilitar o deshabilitar
        el movimiento de la ventana al perder y un botón para cerrar la ventana de opciones.
        """
        self.optionsWindow = Toplevel(self.root)
        self.optionsWindow.title("Opciones")
        self.optionsWindow.geometry("350x250")
        self.optionsWindow.config(bg=self.windowColor)

        options = ["Easy", "Normal", "Hard", "Imposible"]

        selectedOption = StringVar(self.optionsWindow)
        selectedOption.set(self.difficultyToString(self.current_difficulty))

        def seleccionar_opcion(opcion)->None:
            self.current_difficulty = self.difficulty[opcion]
            self.resetGame()

        self.entry = Entry(self.optionsWindow, width=30, textvariable=self.player, bg=self.entryColor, fg=self.entryFgColor)
        self.entry.grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        def applyInput()->None:
            input_text = self.entry.get()
            Adds.debug("Opciones cambiadas")
            messagebox.showinfo("Options changed", "Los valores se ajustaron correctamente.")

        applyButton = Button(self.optionsWindow, text="Aplicar", command=applyInput, bg=self.UIbuttonColor, fg=self.buttonFgColor)
        applyButton.grid(row=1, column=0, columnspan=2, pady=10)

        difficultyLabel = Label(self.optionsWindow, text="Dificultad:", font=("Arial", 12), bg=self.labelColor, fg=self.labelFgColor)
        difficultyLabel.grid(row=2, column=0, pady=10, sticky="W")

        option_menu = OptionMenu(self.optionsWindow, selectedOption, *options, command=seleccionar_opcion)
        option_menu.grid(row=2, column=1, pady=10,sticky="W")
        
        checkbox = ttk.Checkbutton(self.optionsWindow, text="Movimiento de ventana al perder", variable=self.isShakeWindowEnabled)
        checkbox.grid(row=3, column=0, padx=10, pady=10)

        exitButton = Button(self.optionsWindow, text="Cerrar", command=self.optionsWindow.destroy, bg=self.UIbuttonColor, fg=self.buttonFgColor)
        exitButton.grid(row=4, column=1, columnspan=2, pady=20)

    def time(self)->None:
        """
        Esta función actualiza el tiempo transcurrido en el juego cada segundo.

        Si la variable 'timeHabilited' es True, calcula el tiempo actual restando el tiempo de inicio
        al tiempo actual. Luego, actualiza el texto de la etiqueta 'contadortime' con el tiempo transcurrido.
        Despues, llama a sí misma después de 1000 milisegundos (1 segundo).

        """
        if self.timeHabilited:  # Comprueba si el tiempo está habilitado
            self.time_actual = int(time.time() - self.timeInicio)  # Calcula el tiempo actual
            # Actualiza el texto de la etiqueta 'contadortime' con el tiempo transcurrido
            self.contadortime.config(text="Tiempo transcurrido: " + str(self.time_actual).zfill(2), font=("Arial 15"))
            self.root.after(1000, self.time)  # Llama a la función 'time' después de 1 segundo

    def generateButtons(self)->None:
        """
        Esta función genera los botones del juego en función de la dificultad actual.

        Primero, encuentra las dimensiones del tablero de juego en función de la dificultad actual.
        Luego, crea una lista de botones para cada fila del tablero. Cada botón se configura con un 
        ancho, alto, texto, fuente y color de fondo específicos. Además, se vinculan dos eventos a cada 
        botón: un clic izquierdo del mouse que llama a la función 'slotPressed' y un clic derecho del 
        mouse que llama a la función 'placeFlag'. Finalmente, cada botón se coloca en el marco usando 
        la función 'grid'.

        """
        filas, columnas = self.find_dimensions(self.current_difficulty)  # Encuentra las dimensiones del tablero de juego
        self.buttonsList = []  # Crea una lista vacía para almacenar los botones

        for i in range(filas):  # Para cada fila en el tablero de juego
            fila_botones = []  # Crea una lista vacía para almacenar los botones de la fila
            for j in range(columnas):  # Para cada columna en la fila
                # Crea un nuevo botón con las especificaciones dadas
                btn = Button(self.frame, width=3, height=2, text="", font=("Arial 12 bold"), bg=self.buttonColor)
                # Vincula un clic izquierdo del mouse al botón para llamar a la función 'slotPressed'
                btn.bind('<Button-1>', lambda event, c=(i, j): self.slotPressed(c))
                # Vincula un clic derecho del mouse al botón para llamar a la función 'placeFlag'
                btn.bind('<Button-3>', lambda event, c=(i, j): self.placeFlag(c))
                # Coloca el botón en el marco en la posición especificada
                btn.grid(padx=1,pady=1,column=j + 1, row=i + 1, sticky='nsew')  
                fila_botones.append(btn)  # Agrega el botón a la lista de botones de la fila
            self.buttonsList.append(fila_botones)  # Agrega la lista de botones de la fila a la lista de botones del juego  

    def bombsRandom(self)->None:
        """
        Esta función genera las bombas de manera aleatoria en el tablero del juego.

        Primero, calcula el total de casillas en el tablero en función de la dificultad actual.
        Luego, selecciona una muestra aleatoria de casillas para colocar las bombas. El número de bombas
        es un cuarto del total de casillas. Después, establece el número de banderas igual al número de bombas.
        Finalmente, para cada bomba, calcula su posición en el tablero y configura el botón correspondiente
        para revelar las bombas cuando se presiona.

        """
        total_casillas = self.current_difficulty  # Calcula el total de casillas en el tablero
        filas, columnas = self.find_dimensions(total_casillas)  # Encuentra las dimensiones del tablero
        # Selecciona una muestra aleatoria de casillas para colocar las bombas
        self.bombs = random.sample(range(total_casillas), total_casillas // 4)
        self.setFlags(len(self.bombs))  # Establece el número de banderas igual al número de bombas
        for bomba in self.bombs:  # Para cada bomba
            fila, columna = divmod(bomba, columnas)  # Calcula su posición en el tablero
            # Configura el botón correspondiente para revelar las bombas cuando se presiona
            self.buttonsList[fila][columna].config(command=lambda i=bomba: self.revealBombas(self.bombs))
    
    def checkWin(self)->None:
        """
        Esta función verifica si el jugador ha ganado el juego.

        Primero, calcula el número total de botones seguros (es decir, botones que no tienen bombas) restando
        el número de bombas de la dificultad actual. Luego, recorre todos los botones en el tablero. Si un botón
        no tiene una bomba y no es gris (es decir, ha sido presionado), incrementa el contador de botones descubiertos.

        Si el número de botones descubiertos es igual al número total de botones seguros, entonces el jugador ha ganado
        el juego. En este caso, deshabilita el tiempo, agrega las estadísticas del juego al archivo de estadísticas,
        muestra un mensaje de victoria y reinicia el juego.

        Ejemplo:
        >>> checkWin(self)
        # Verifica si el jugador ha ganado el juego.
        """
        buttons_discovered = 0  # Inicializa el contador de botones descubiertos
        total_safe_buttons = self.current_difficulty - len(self.bombs)  # Calcula el número total de botones seguros
        
        for i in range(len(self.buttonsList)):  # Para cada fila en la lista de botones
            for j in range(len(self.buttonsList[i])):  # Para cada botón en la fila
                button = self.buttonsList[i][j]  # Obtiene el botón
                # Si el botón no tiene una bomba y no es gris (ha sido presionado)
                if (i * len(self.buttonsList[i]) + j) not in self.bombs and button['bg'] != self.buttonColor:
                    buttons_discovered += 1  # Incrementa el contador de botones descubiertos

        # Si el número de botones descubiertos es igual al número total de botones seguros
        if buttons_discovered == total_safe_buttons:
            self.timeHabilited = False  # Deshabilita el tiempo
            # Agrega las estadísticas del juego al archivo de estadísticas
            #Data.addStats(self.file_path,self.player.get(), self.time_actual, self.difficultyToString(self.current_difficulty))
            #El codigo de arriba es para guardar en csv
            DataTxt.addStats(self.file_path,self.player.get(), self.time_actual, self.difficultyToString(self.current_difficulty))
            messagebox.showinfo("Victory", "¡Has ganado el juego!")  # Muestra un mensaje de victoria
            self.resetGame()  # Reinicia el juego

    def setFlags(self, flags)->None:
        """
        Esta función establece el número de banderas disponibles y actualiza el contador de banderas.

        Primero, establece el número de banderas disponibles en el valor pasado como argumento.
        Luego, actualiza el texto del contador de banderas para reflejar el número de banderas disponibles.
        Finalmente, llama a la función 'updateFlagsCounter' para actualizar el contador de banderas.

        Parámetros:
        flags (int): El número de banderas disponibles.

        Ejemplo:
        >>> setFlags(self, 10)
        # Establece el número de banderas disponibles en 10 y actualiza el contador de banderas.
        """
        self.flags = flags  # Establece el número de banderas disponibles
        # Actualiza el texto del contador de banderas para reflejar el número de banderas disponibles
        self.flags_counter.config(text="Banderas disponibles: " + ("0" + str(self.flags) if self.flags < 10 else str(self.flags)))
        self.updateFlagsCounter()  # Actualiza el contador de banderas

    def revealBombas(self, index)->None:
        """
        Esta función revela las bombas en el tablero del juego cuando se presiona un botón que contiene una bomba.

        Primero, inicializa la potencia de la explosión en 0. Luego, calcula las dimensiones del tablero de juego
        en función de la dificultad actual. Después, para cada índice en la lista de índices pasada como argumento,
        calcula la posición del botón correspondiente en el tablero. Si el botón no es naranja (es decir, no tiene una bandera),
        cambia el color de fondo del botón a rojo, establece la imagen del botón en la imagen de la bomba e incrementa la potencia de la explosión.

        Si la opción de agitar la ventana está habilitada, llama a la función 'shakeWindow' con la potencia de la explosión como argumento.
        Luego, deshabilita el tiempo, muestra un mensaje de "Game Over" y reinicia el juego.

        Parámetros:
        index (list): Una lista de índices que representan las posiciones de las bombas en el tablero del juego.

        Ejemplo:
        >>> revealBombas(self, [10, 15, 20])
        # Revela las bombas en las posiciones 10, 15 y 20 del tablero del juego.
        """
        explosionPower=0  # Inicializa la potencia de la explosión
        filas, columnas = self.find_dimensions(self.current_difficulty)  # Calcula las dimensiones del tablero de juego
        for i in index:  # Para cada índice en la lista de índices
            fila, columna = divmod(i, columnas)  # Calcula la posición del botón correspondiente en el tablero
            # Si el botón no es naranja (no tiene una bandera)
            if self.buttonsList[fila][columna]['bg'] != 'orange':
                # Cambia el color de fondo del botón a rojo
                self.buttonsList[fila][columna].config(bg='red', image=self.bomb)
                explosionPower+=1  # Incrementa la potencia de la explosión
        # Si la opción de agitar la ventana está habilitada
        if self.isShakeWindowEnabled.get():
            self.shakeWindow(explosionPower)  # Agita la ventana
        self.timeHabilited = False  # Deshabilita el tiempo
        messagebox.showinfo("Game Over", Adds.randomOverText())  # Muestra un mensaje de "Game Over"
        self.resetGame()  # Reinicia el juego

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
        """
        Esta función encuentra todos los factores de un número dado 'n'.

        Genera una lista de tuplas, donde cada tupla contiene dos factores de 'n' que se multiplican para obtener 'n'.
        Solo considera los factores hasta la raíz cuadrada de 'n' para evitar duplicados.

        Parámetros:
        n (int): El número del cual encontrar los factores.

        Retorna:
        list: Una lista de tuplas, donde cada tupla contiene dos factores de 'n'.

        Ejemplo:
        >>> find_factors(self, 10)
        [(1, 10), (2, 5)]
        """
        factors = [(i, n // i) for i in range(1, int(n**0.5) + 1) if n % i == 0]
        return factors

    def find_dimensions(self, n)->int:
        """
        Esta función encuentra las dimensiones que están más cerca de ser cuadradas para un número dado 'n'.

        Primero, encuentra todos los factores de 'n' usando la función 'find_factors'. Luego, de todos los pares de factores,
        selecciona el par que está más cerca de ser un cuadrado. Esto se hace encontrando el par de factores cuya diferencia es mínima.

        Parámetros:
        n (int): El número del cual encontrar las dimensiones.

        Retorna:
        tuple: Una tupla que contiene las dos dimensiones.

        Ejemplo:
        >>> find_dimensions(self, 10)
        (2, 5)
        """
        factors = self.find_factors(n)  # Encuentra todos los factores de 'n'
        # De todos los pares de factores, selecciona el par que está más cerca de ser un cuadrado
        closest_to_square = min(factors, key=lambda x: abs(x[0] - x[1]))
        return closest_to_square

    def countNearbyBombs(self, index)->int:
        """
        Esta función cuenta el número de bombas que están cerca de una casilla dada en el tablero del juego.

        Primero, inicializa un contador de bombas en 0. Luego, calcula las dimensiones del tablero de juego
        en función de la dificultad actual. Después, para cada casilla en un radio de una casilla alrededor
        de la casilla dada (incluyendo las diagonales), si la casilla está dentro del tablero y contiene una bomba,
        incrementa el contador de bombas.

        Parámetros:
        index (tuple): Una tupla que contiene las coordenadas (fila, columna) de la casilla.

        Retorna:
        int: El número de bombas que están cerca de la casilla.

        Ejemplo:
        >>> countNearbyBombs(self, (1, 1))
        # Cuenta el número de bombas que están cerca de la casilla en la fila 1, columna 1.
        """
        count = 0  # Inicializa el contador de bombas
        filas, columnas = self.find_dimensions(self.current_difficulty)  # Calcula las dimensiones del tablero de juego
        fila, columna = index  # Obtiene las coordenadas de la casilla
        for dy in (-1, 0, 1):  # Para cada desplazamiento en las filas
            for dx in (-1, 0, 1):  # Para cada desplazamiento en las columnas
                if dx == 0 and dy == 0:  # Si el desplazamiento es 0 en ambas direcciones (es decir, la casilla misma)
                    continue  # Continúa con la siguiente iteración
                nx, ny = columna + dx, fila + dy  # Calcula las coordenadas de la casilla vecina
                # Si la casilla vecina está dentro del tablero
                if 0 <= nx < columnas and 0 <= ny < filas: 
                    # Si la casilla vecina contiene una bomba
                    if (ny * columnas + nx) in self.bombs:  
                        count += 1  # Incrementa el contador de bombas
        return count  # Retorna el número de bombas

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
        """
        Esta función se ejecuta cuando se presiona un botón en el tablero del juego.

        Primero, verifica si el juego ha comenzado. Si no es así, disminuye el número de intentos actuales,
        verifica si el botón presionado contiene una bomba y, en caso afirmativo, reasigna la bomba.
        Luego, inicia el tiempo y verifica si se han agotado los intentos. Si es así, marca el juego como iniciado.

        Después, si el botón presionado está vacío y es gris (es decir, no ha sido presionado ni marcado con una bandera),
        cuenta el número de bombas cercanas y actualiza el texto y el color del botón en función del número de bombas cercanas.
        Si no hay bombas cercanas, presiona recursivamente todos los botones vecinos que están vacíos y son grises.

        Finalmente, verifica si el jugador ha ganado el juego.

        Parámetros:
        index (tuple): Una tupla que contiene las coordenadas (fila, columna) del botón presionado.

        Ejemplo:
        >>> slotPressed(self, (1, 1))
        # Presiona el botón en la fila 1, columna 1.
        """
        filas, columnas = self.find_dimensions(self.current_difficulty)  # Calcula las dimensiones del tablero de juego
        fila, columna = index  # Obtiene las coordenadas del botón presionado
        
        if self.currentAttemps!=0:  # Si el juego no ha comenzado
            self.currentAttemps -= 1  # Disminuye el número de intentos actuales
            # Si el botón presionado contiene una bomba y la dificultad actual es "Easy" o "Normal"
            if fila * columnas + columna in self.bombs and self.current_difficulty in [self.difficulty["Easy"], self.difficulty["Normal"]]:
                self.reassignBomb(fila, columna)  # Reasigna la bomba
            
        if not self.inicio:  # Si se han agotado los intentos
            self.inicio = True  # Marca el juego como iniciado
            self.timeHabilited = True #Habilita el tiempo
            self.timeInicio = time.time()  # Inicia el tiempo
            self.time()  # Actualiza el tiempo
        
        # Si el botón presionado está vacío y es gris (no ha sido presionado ni marcado con una bandera)
        if self.buttonsList[fila][columna]['text'] == '' and self.buttonsList[fila][columna]['bg'] == self.buttonColor:
            nearbyBombs = self.countNearbyBombs(index)  # Cuenta el número de bombas cercanas
            # Actualiza el texto y el color del botón en función del número de bombas cercanas
            self.buttonsList[fila][columna].config(bg=self.pressedButtonColor, text=str(nearbyBombs) if nearbyBombs > 0 else '', fg=self.coloration(nearbyBombs))
            if nearbyBombs == 0:  # Si no hay bombas cercanas
                for dy in (-1, 0, 1):  # Para cada desplazamiento en las filas
                    for dx in (-1, 0, 1):  # Para cada desplazamiento en las columnas
                        if dx == 0 and dy == 0:  # Si el desplazamiento es 0 en ambas direcciones (es decir, la casilla misma)
                            continue  # Continúa con la siguiente iteración
                        nx, ny = columna + dx, fila + dy  # Calcula las coordenadas de la casilla vecina
                        # Si la casilla vecina está dentro del tablero
                        if 0 <= nx < columnas and 0 <= ny < filas:
                            adj_index = (ny, nx)  # Obtiene el índice de la casilla vecina
                            # Si la casilla vecina no contiene una bomba y está vacía y es gris
                            if adj_index not in self.bombs and self.buttonsList[ny][nx]['text'] == '' and self.buttonsList[ny][nx]['bg'] == self.buttonColor:
                                self.slotPressed(adj_index)  # Presiona la casilla vecina
            self.checkWin()  # Verifica si el jugador ha ganado el juego

    def reassignBomb(self, fila, columna)->None:
        """
        Esta función reasigna una bomba a una nueva ubicación en el tablero del juego.

        Primero, calcula el índice de la bomba en el tablero de juego y la elimina de la lista de bombas.
        Luego, calcula los lugares disponibles en el tablero donde se puede colocar la bomba y selecciona uno al azar.
        Después, agrega la nueva bomba a la lista de bombas y actualiza el comando del botón correspondiente para revelar las bombas cuando se presiona.
        Finalmente, elimina el comando del botón donde se quitó la bomba.

        Parámetros:
        fila (int): La fila del botón donde se quitó la bomba.
        columna (int): La columna del botón donde se quitó la bomba.
        """
        print("Reasigned")  # Imprime un mensaje para indicar que la bomba ha sido reasignada
        filas, columnas = self.find_dimensions(self.current_difficulty)  # Calcula las dimensiones del tablero de juego
        bomb_index = fila * columnas + columna  # Calcula el índice de la bomba en el tablero de juego
        self.bombs.remove(bomb_index)  # Elimina la bomba de la lista de bombas

        # Calcula los lugares disponibles en el tablero donde se puede colocar la bomba
        available_spots = set(range(self.current_difficulty)) - set(self.bombs) - {bomb_index}
        new_bomb = random.choice(list(available_spots))  # Selecciona un lugar al azar
        self.bombs.append(new_bomb)  # Agrega la nueva bomba a la lista de bombas
        
        # Actualizar el comando del nuevo botón de bomba
        new_fila, new_columna = divmod(new_bomb, columnas)  # Calcula las coordenadas del nuevo botón de bomba
        # Configura el botón para revelar las bombas cuando se presiona
        self.buttonsList[new_fila][new_columna].config(command=lambda i=new_bomb: self.revealBombas(self.bombs))
        
        # Eliminar el comando del botón donde se quitó la bomba
        self.buttonsList[fila][columna].config(command=lambda: None)

    def placeFlag(self, index)->None:
        """
        Esta función coloca o quita una bandera en un botón del tablero del juego.

        Primero, obtiene las coordenadas del botón. Luego, si el botón es gris (es decir, no ha sido presionado ni marcado con una bandera)
        y todavía quedan banderas disponibles, coloca una bandera en el botón, disminuye el número de banderas disponibles y actualiza el contador de banderas.

        Si el botón es naranja (es decir, tiene una bandera), quita la bandera del botón, aumenta el número de banderas disponibles y actualiza el contador de banderas.

        Parámetros:
        index (tuple): Una tupla que contiene las coordenadas (fila, columna) del botón.

        """
        fila, columna = index  # Obtiene las coordenadas del botón
        # Si el botón es gris (no ha sido presionado ni marcado con una bandera) y todavía quedan banderas disponibles
        if self.buttonsList[fila][columna]['bg'] == self.buttonColor and self.flags > 0:
            # Coloca una bandera en el botón
            self.buttonsList[fila][columna].config(bg=self.flagButtonColor, image=self.flag)
            self.buttonsList[fila][columna]["state"] = tk.DISABLED # Desactiva el botón
            self.flags -= 1  # Disminuye el número de banderas disponibles
            self.updateFlagsCounter()  # Actualiza el contador de banderas
        # Si el botón es naranja (tiene una bandera)
        elif self.buttonsList[fila][columna]['bg'] == self.flagButtonColor:
            # Quita la bandera del botón
            self.buttonsList[fila][columna].config(bg=self.buttonColor, image=self.transparent_image)
            self.buttonsList[fila][columna]["state"] = tk.NORMAL # Vuelve a activar el boton
            self.flags += 1  # Aumenta el número de banderas disponibles
            self.updateFlagsCounter()  # Actualiza el contador de banderas

    def updateFlagsCounter(self)->None:
        self.flags_counter.config(text="Banderas disponibles: " + ("0" + str(self.flags) if self.flags < 10 else str(self.flags)))

    def resetGame(self)->None:
        self.timeHabilited = False
        self.currentAttemps = self.defaultNoInstaLoseAttemps
        self.contadortime.config(text="Tiempo transcurrido: " + "00", font=("Arial 15"))
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
            if command == "AutoWin":
                Adds.debug(f"Eliminando {len(app.bombs)-1} de la lista.")
                for _ in range(len(app.bombs)-1):app.bombs.pop()
            else:
                exec(command)
        except Exception as e:
            l = traceback.format_exc()
            Adds.warning(f"Error al ejecutar el comando: {e} {l}")

if __name__ == "__main__" and os.path.isfile("img/coconut/coconut.jpeg"):
    try:
        hilo_consola = threading.Thread(target=debugConsole, daemon=True)
        hilo_consola.start()
        root = Tk() 
        app = Minesweeper(root)  
        root.mainloop()  
    except Exception as e:
        # Si se captura un error no manejado en el nivel superior
        traceback_info = traceback.format_exc()
        Adds.debug(f"Error no manejado: {e}")
        Adds.debug(f"Traceback:\n{traceback_info}")
else:
    messagebox.showerror("Error", "Hubo un error fatal debido a la falta de un archivo esencial para la ejecucion.") 