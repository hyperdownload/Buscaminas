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
from tkinter import messagebox 
from data import *
try:
    from PIL import Image, ImageTk
except ModuleNotFoundError as e:
    Adds.warning("Pillow no encontrado\n"
                 "Descargando...")
    os.system("pip install pillow")
    Adds.debug("Pillow instalado!")
    from PIL import Image, ImageTk
import customtkinter as ctk

commandConsole=True
Adds.debug(os.path.abspath(__file__))

# Cambia al directorio donde se encuentra el archivo
scriptDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(scriptDir)
Adds.debug(f"Directorio cambiado a:{scriptDir}")

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
        self.settings = {
            'buttonColor': '#000000',
            'UIbuttonColor': '#000000',
            'buttonFgColor': '#FFFFFF',
            'flagButtonColor': '#FFA500',
            'pressedButtonColor': '#b4b4b4',
            'labelColor': '#000000',
            'labelFgColor': '#FFFFFF',
            'windowColor': '#000000',
            'windowFgColor': '#FFFFFF',
            'entryColor': '#000000',
            'entryFgColor': '#FFFFFF',
            'frameColor': '#000000',
            'checkBoxColor': '#000000',
            'checkBoxTextColor': '#000000',
        }
        
        self.loadSettings() # Carga a las variables de personalizacion sus datos
        
        self.cacheCoordinateX=[]
        self.cacheCoordinateY=[]
        
        self.root = root 

        self.difficulty = {"Easy": 40, "Normal": 64, "Hard": 81, "Imposible":150}  # Define los niveles de dificultad
        self.current_difficulty = self.difficulty["Easy"]  # Establece la dificultad actual como "Easy"

        self.buttonsList = []  # Crea una lista para almacenar los botones del juego
        self.reset = False  # Establece la variable de reinicio en False
        self.inicio = False  # Establece la variable de inicio en False
        self.timeInicio = time.time()  # Almacena el tiempo de inicio del juego
        self.time_actual = 0
        self.flags = 0  # Inicializa el contador de banderas en 0
        self.bombs = []  # Crea una lista para almacenar las bombas
        
        self.root.config(bg=self.windowColor)

        # Mod Manager
        Adds.debug("Cargando mods...")
        self.mod_manager = ModManager()  # Crea un nuevo administrador de mods
        self.mod_manager.apply_mods(self)  # Aplica los mods al juego
        
        self.player=tk.StringVar()  # Crea una variable de cadena para almacenar el nombre del jugador
        self.player.set("Player")  # Establece el nombre del jugador por defecto como "Player"
        #Actualmente existe stats.csv y stats.txt, funcionan en ambos pero debe de ser actualizado en el codigo de DataStadistics a Data
        
        self.file_path = 'stats.json'  # Establece la ruta del archivo donde se almacenan las estadísticas
        self.usersPath = 'users.json' #
        
        self.logged = False 

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
        self.defaultNoInstaLoseAttemps = 1  # Establece el número predeterminado de intentos antes de perder instantáneamente
        
        self.currentAttemps = self.defaultNoInstaLoseAttemps  # Establece los intentos actuales en el número predeterminado de intentos
        
        #Adds.debug(f"Fila dividida:{row/2}/Fila multiplicada *2:{row*2}")

        self.contadortime = Label(self.root,anchor="w")  # Crea una etiqueta para mostrar el tiempo
        #self.contadortime.grid(column=1, row=0, columnspan=int(row//2),sticky='nwse')  # Coloca la etiqueta en el marco
        self.contadortime.pack(side=tk.TOP)
        self.contadortime.config(text="Tiempo transcurrido: " + "00", font=("Arial 15"), bg=self.labelColor, fg=self.labelFgColor)
        self.flags_counter = Label(self.root, text="Banderas disponibles:" + str(self.flags), font=("Arial 15"), bg=self.labelColor, fg=self.labelFgColor,anchor="w")  # Crea una etiqueta para mostrar las banderas disponibles
        #self.flags_counter.grid(column=int(row//2)+1, row=0, columnspan=int(row//2),sticky='nwse')  # Coloca la etiqueta en el marco

        self.flags_counter.pack(side=tk.TOP)
        self.frame = Frame(self.root, bg=self.frameColor)  # Crea un nuevo marco en la ventana principal
        self.frame.pack(side=tk.BOTTOM)  # Empaqueta el marco para que se muestre en la ventana
        self.root.title("Siria Simulator")  # Establece el título de la ventana
        self.root.iconbitmap("img/bomba.ico")  # Establece el ícono de la ventana
        self.root.resizable(False, False)  # Hace que la ventana no sea redimensionable
        self.frame.config(width=400, height=400)  # Configura el tamaño del marco
        self.navbar = Menu(self.root)  # Crea una nueva barra de navegación
        self.root.config(menu=self.navbar)  # Configura la barra de navegación de la ventana
        self.transparent_image = PhotoImage(width=1, height=1)  # Crea una imagen transparente para usarla como imagen predeterminada en los botones
        
        self.file_menu = Menu(self.navbar, tearoff=0)  # Crea un nuevo menú en la barra de navegación
        self.file_menu.add_command(label="Nuevo Juego", command=self.resetGame)  # Agrega un comando para iniciar un nuevo juego
        self.file_menu.add_command(label="Stats", command=self.stats)  # Agrega un comando para mostrar las estadísticas
        self.file_menu.add_command(label="Opciones", command=self.options)  # Agrega un comando para abrir la ventana de opciones
        self.file_menu.add_command(label="Personalizar objetos", command=self.personalization) # Agrega un comando para abrir una ventana para personalizar lo visual
        self.file_menu.add_command(label="Salir", command=self.root.quit)  # Agrega un comando para salir del juego
        self.navbar.add_cascade(label="Archivo", menu=self.file_menu)  # Agrega el menú a la barra de navegación
        
        self.pressedBombs = 0
        self.winnedGames = 0
        self.losedGames = 0
        self.flagsUsed = 0

        self.generateButtons()  # Genera los botones del juego
        self.bombsRandom()  # Coloca las bombas de manera aleatoria 
        
    def loadSettings(self) -> None:
        """
        Carga la configuración de colores desde el archivo "config.json".

        Este método intenta cargar la configuración de colores desde un archivo JSON llamado "config.json". 
        Si el archivo no se encuentra o hay un error en el formato JSON, se usan valores por defecto 
        que ya están definidos en el atributo `settings` de la clase.

        Proceso detallado:
        1. Intenta abrir y leer el archivo "config.json".
        2. Si el archivo se lee correctamente, actualiza el diccionario `settings` de la clase con los 
        valores obtenidos del archivo JSON. Si alguna clave no está presente en el archivo, se 
        mantiene el valor por defecto de `settings`.
        3. Actualiza los atributos de la clase con los valores del diccionario `settings`.
        4. Si el archivo "config.json" no se encuentra, se registra una advertencia y se usan los 
        valores por defecto.
        5. Si ocurre un error al decodificar el archivo JSON, se registra una advertencia y se usan los 
        valores por defecto.

        Excepciones:
        - FileNotFoundError: Se lanza si el archivo "config.json" no se encuentra.
        - json.JSONDecodeError: Se lanza si hay un error al decodificar el archivo JSON.

        Adds:
        - Se registra un mensaje de depuración al iniciar la carga de la configuración.
        - Se registran advertencias si el archivo no se encuentra o si hay un error de decodificación.

        Returns:
        None
        """
        try:
            Adds.debug("Cargando configuración...")

            # Abre y lee el archivo 'config.json'
            with open('config.json', 'r') as f:
                data = json.load(f)
                
                # Actualiza el diccionario 'settings' con los valores del archivo JSON
                self.settings.update({k: data.get(k, v) for k, v in self.settings.items()})

            # Actualiza los atributos de la clase con los valores del diccionario 'settings'
            for key, value in self.settings.items():
                setattr(self, key, value)

        except FileNotFoundError:
            Adds.warning("No se encontró el archivo config.json. Usando valores por defecto.")
        except json.JSONDecodeError:
            Adds.warning("Error al decodificar JSON. Usando valores por defecto.")

    def saveSettings(self) -> None:
        """
        Guarda la configuración de colores en un archivo JSON llamado "config.json".

        No recibe parámetros.

        No retorna ningún valor.
        """
        result = messagebox.askyesno("Confirmar", "Para aplicar los cambios se reiniciará la aplicación.")
        if result:
            Adds.debug("Guardando configuración")

            # Definir un diccionario con las entradas de color y sus atributos correspondientes
            entries = {
                'buttonColor': self.entryButtonColor,
                'UIbuttonColor': self.entryUIbuttonColor,
                'buttonFgColor': self.entryButtonBgColor,
                'flagButtonColor': self.entryFlagButtonColor,
                'pressedButtonColor': self.entryPressedButtonColor,
                'labelColor': self.entryLabelColor,
                'labelFgColor': self.entryLabelBgColor,
                'windowColor': self.entryWindowColor,
                'windowFgColor': self.entryWindowColor,
                'entryColor': self.entryEntryColor,
                'entryFgColor': self.entryEntryTxColor,
                'frameColor': self.entryFrameColor,
                'checkBoxColor': self.entryCheckBoxColor,
                'checkBoxTextColor': self.entryCheckBoxTextColor,
            }

            # Obtener datos de los Entry y almacenarlos en un diccionario
            data = {key: entry.get() for key, entry in entries.items()}

            # Guardar datos en JSON
            with open('config.json', 'w') as f:
                Adds.debug("Escribiendo json...")
                json.dump(data, f, indent=4)
            
            Adds.debug("Configuración guardada correctamente.")
            self.root.destroy()

            hilo_consola = threading.Thread(target=debugConsole, daemon=True)
            hilo_consola.start()

            root = Tk()
            app = Minesweeper(root)
            root.mainloop()

    def personalization(self) -> None:
        """
        Crea un frame dentro de self.root para personalizar los colores de los botones y otros elementos de la interfaz.
        """
        self.personalizationFrame = Frame(self.root, bg=self.windowColor)
        self.personalizationFrame.place(relwidth=1, relheight=1)

        canvas = Canvas(self.personalizationFrame, bg=self.windowColor)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = Scrollbar(self.personalizationFrame, orient=VERTICAL, command=canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        interiorFrame = Frame(canvas, bg=self.windowColor)
        canvas.create_window((0, 0), window=interiorFrame, anchor='nw')

        # Crear una lista de secciones y sus entradas correspondientes
        sections = [
            ("Botones", [
                ("Color de Fondo:", "entryButtonColor", self.buttonColor),
                ("Color de Texto:", "entryButtonBgColor", self.buttonFgColor),
            ]),
            ("Botones UI", [
                ("Color de Fondo:", "entryUIbuttonColor", self.UIbuttonColor),
                ("Color de Texto:", "entryUIbuttonBgColor", self.buttonFgColor),
            ]),
            ("Botón de Bandera", [
                ("Color de Fondo:", "entryFlagButtonColor", self.flagButtonColor),
                ("Color de Texto:", "entryFlagButtonBgColor", self.buttonFgColor),
            ]),
            ("Botón Presionado", [
                ("Color de Fondo:", "entryPressedButtonColor", self.pressedButtonColor),
                ("Color de Texto:", "entryPressedButtonBgColor", self.buttonFgColor),
            ]),
            ("Entry", [
                ("Color de Fondo:", "entryEntryColor", self.entryColor),
                ("Color de Texto:", "entryEntryTxColor", self.entryFgColor),
            ]),
            ("Label", [
                ("Color de Fondo:", "entryLabelColor", self.labelColor),
                ("Color de Texto:", "entryLabelBgColor", self.labelFgColor),
            ]),
            ("Ventana", [
                ("Color de Fondo:", "entryWindowColor", self.windowColor),
            ]),
            ("Frame", [
                ("Color de Fondo:", "entryFrameColor", self.frameColor),
            ]),
            ("CheckBox", [
                ("Color de Fondo:", "entryCheckBoxColor", self.checkBoxColor),
                ("Color de Texto:", "entryCheckBoxTextColor", self.checkBoxTextColor)
            ]),
        ]

        # Generar las etiquetas y entradas dinámicamente
        row = 0
        for sectionName, entries in sections:
            section_label = Label(interiorFrame, text=sectionName, font=("Arial", 12, "bold"), bg=self.labelColor, fg=self.labelFgColor)
            section_label.grid(column=0, row=row, pady=10, padx=10, sticky=W)
            row += 1

            for labelText, attr_name, value in entries:
                label = Label(interiorFrame, text=labelText, font=("Arial", 10), bg=self.labelColor, fg=self.labelFgColor)
                label.grid(column=0, row=row, padx=10, sticky=W)
                entry = Entry(interiorFrame, bg=self.entryColor, fg=self.entryFgColor)
                entry.insert(0, value)
                entry.grid(column=1, row=row, padx=10)
                setattr(self, attr_name, entry)
                row += 1

        save_button = Button(interiorFrame, text="Guardar", command=self.saveSettings, font=("Arial", 10), bg=self.UIbuttonColor, fg=self.buttonFgColor)
        save_button.grid(column=1, row=row, pady=20)

        interiorFrame.update_idletasks()
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
        
    def stats(self) -> None:
        """
        Esta función muestra una ventana con las estadísticas de los jugadores o una ventana de registro/inicio de sesión.

        Si el usuario está logueado, se muestra una nueva ventana (Toplevel) con las estadísticas de los jugadores,
        incluyendo el nombre del jugador, el tiempo, y la dificultad. 

        Si el usuario no está logueado, se muestra una ventana de registro/inicio de sesión.
        """
        if self.logged:
            self.statsWindow = ctk.CTkToplevel(self.root)
            self.statsWindow.title("Estadísticas")
            self.statsWindow.geometry("400x400")
            self.statsWindow.configure(fg_color=self.windowColor)

            stats = DataStadistics.getStatPerUser(self.file_path, self.player.get())

            if not stats:
                no_stats_label = ctk.CTkLabel(self.statsWindow, text="No se encontraron estadísticas para este usuario.")
                no_stats_label.pack(pady=20)
                return
            
            for i, stat in enumerate(stats):
                username_label = ctk.CTkLabel(self.statsWindow, text=f"Usuario: {stat['username']}", anchor="e", fg_color=self.labelColor, text_color=self.labelFgColor, justify=LEFT, width=12)
                username_label.grid(row=0, column=0, pady=20)

                score_label = ctk.CTkLabel(self.statsWindow, text=f"Tiempo: {stat['score']}",anchor="e", fg_color=self.labelColor, text_color=self.labelFgColor, justify=LEFT, width=12)
                score_label.grid(row=1, column=0, padx=10, pady=20)

                difficulty_label = ctk.CTkLabel(self.statsWindow, text=f"Dificultad: {stat['difficulty']}",anchor="e", fg_color=self.labelColor, text_color=self.labelFgColor, justify=LEFT, width=12)
                difficulty_label.grid(row=2, column=0, padx=10, pady=20)

                bombs_pressed_label = ctk.CTkLabel(self.statsWindow, text=f"Bombas presionadas: {stat['bombsPressed']}",anchor="e", fg_color=self.labelColor, text_color=self.labelFgColor, justify=LEFT, width=12)
                bombs_pressed_label.grid(row=3, column=0, padx=10, pady=20)
                self.pressedBombs = stat['bombsPressed']

                winned_games_label = ctk.CTkLabel(self.statsWindow, text=f"Juegos ganados: {stat['winnedGames']}",anchor="e", fg_color=self.labelColor, text_color=self.labelFgColor, justify=LEFT, width=12)
                winned_games_label.grid(row=4, column=0, padx=10, pady=20)
                self.winnedGames = stat['winnedGames']

                game_losses_label = ctk.CTkLabel(self.statsWindow, text=f"Juegos perdidos: {stat['gameLosses']}",anchor="e", fg_color=self.labelColor, text_color=self.labelFgColor, justify=LEFT, width=12)
                game_losses_label.grid(row=5, column=0, padx=10, pady=20)
                self.losedGames = stat['gameLosses']

                flags_used_label = ctk.CTkLabel(self.statsWindow, text=f"Banderas usadas: {stat['flagsUsed']}",anchor="e", fg_color=self.labelColor, text_color=self.labelFgColor, justify=LEFT, width=12)
                flags_used_label.grid(row=6, column=0, padx=10, pady=20)
                self.flagsUsed = stat['flagsUsed']
            def update():
                stats = DataStadistics.getStatPerUser(self.file_path, self.player.get())
                for i, stat in enumerate(stats):
                    username_label.configure(text=f"Usuario: {stat['username']}")
                    score_label.configure(text=f"Tiempo: {stat['score']}")
                    difficulty_label.configure(text=f"Dificultad: {stat['difficulty']}")
                    bombs_pressed_label.configure(text=f"Bombas presionadas: {stat['bombsPressed']}")
                    winned_games_label.configure(text=f"Juegos ganados: {stat['winnedGames']}")
                    game_losses_label.configure(text=f"Juegos perdidos: {stat['gameLosses']}")
                    flags_used_label.configure(text=f"Banderas usadas: {stat['flagsUsed']}")
                winnedGraph.set((self.winnedGames / (self.losedGames + self.winnedGames)) * 100)
            
            winnedGraph = RadialProgressbar(self.statsWindow, size=75, font_size_ratio=0.2 )
            winnedGraph.place(x = 300,y = 270)

            winnedGraph.set((self.winnedGames / (self.losedGames + self.winnedGames)) * 100)

            self.update_button = ctk.CTkButton(self.statsWindow, text="Actualizar", command=update)
            self.update_button.grid(row=7, column=0, columnspan=7, pady=10)
        else:
            self.loginWindow = ctk.CTkToplevel(self.root)
            self.loginWindow.title("Registro / Inicio de sesión")
            self.loginWindow.geometry("300x300+550+100")
            self.loginWindow.configure(fg_color=self.windowColor)

            def register():
                username = username_entry.get()
                password = password_entry.get()
                if not username or not password:
                    Adds.warning("Usuario y contraseña no pueden estar vacíos.")
                    return
                
                users = {}
                if os.path.exists("users.json"):
                    with open("users.json", 'r') as file:
                        try:
                            users = json.load(file)
                        except json.JSONDecodeError:
                            Adds.warning("Error al decodificar el archivo users.json.")
                
                if username in users:
                    Adds.warning("El usuario ya está registrado.")
                else:
                    users[username] = password
                    with open("users.json", 'w') as file:
                        json.dump(users, file, indent=4)
                    Adds.debug(f"Usuario {username} registrado correctamente.")
                    self.loginWindow.destroy()

            def login():
                username = username_entry.get()
                password = password_entry.get()
                if not username or not password:
                    Adds.warning("Usuario y contraseña no pueden estar vacíos.")
                    return
                
                users = {}
                if os.path.exists("users.json"):
                    with open("users.json", 'r') as file:
                        try:
                            users = json.load(file)
                        except json.JSONDecodeError:
                            Adds.warning("Error al decodificar el archivo users.json.")
                
                if username in users and users[username] == password:
                    Adds.debug(f"Usuario {username} ha iniciado sesión correctamente.")
                    self.logged = True
                    self.player.set(username)  # Guardar el nombre de usuario del jugador actual
                    self.loginWindow.destroy()
                    self.stats()  # Recargar la ventana de estadísticas
                else:
                    Adds.warning("Usuario o contraseña incorrectos.")

            username_label = ctk.CTkLabel(self.loginWindow, text="Usuario:", fg_color=self.labelColor, text_color=self.labelFgColor)
            username_label.pack(pady=5)
            username_entry = ctk.CTkEntry(self.loginWindow, fg_color=self.entryColor, text_color=self.entryFgColor)
            username_entry.pack(pady=5)

            password_label = ctk.CTkLabel(self.loginWindow, text="Contraseña:", fg_color=self.labelColor, text_color=self.labelFgColor)
            password_label.pack(pady=5)
            password_entry = ctk.CTkEntry(self.loginWindow, show="*", fg_color=self.entryColor, text_color=self.entryFgColor)
            password_entry.pack(pady=5)

            register_button = ctk.CTkButton(self.loginWindow, text="Registrarse", command=register, fg_color=self.UIbuttonColor, text_color=self.buttonFgColor)
            register_button.pack(pady=10)

            login_button = ctk.CTkButton(self.loginWindow, text="Iniciar sesión", command=login, fg_color=self.UIbuttonColor, text_color=self.buttonFgColor)
            login_button.pack(pady=10)
    
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
        
        checkbox = tk.Checkbutton(self.optionsWindow, text="Movimiento de ventana al perder", variable=self.isShakeWindowEnabled, fg=self.checkBoxTextColor, bg=self.checkBoxColor)
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
                btn = Button(self.frame, width=4, height=2, text="", font=("Arial 12 bold"), bg=self.buttonColor)
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
            self.winnedGames+=1
            self.timeHabilited = False  # Deshabilita el tiempo
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

    def revealBombas(self, index, cheat=False)->None:
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
        if not cheat:
            if self.isShakeWindowEnabled.get():
                self.shakeWindow(explosionPower)  # Agita la ventana
            self.timeHabilited = False  # Deshabilita el tiempo
            self.pressedBombs += 1
            self.losedGames += 1
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
                        self.cacheCoordinateX.append(nx)
                        self.cacheCoordinateY.append(ny)
        Adds.debug(f"Bomb nearby:{count}")
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
    
    def gameManager(self, nearbyBombs)->None:
        if nearbyBombs>0 and self.currentAttemps!=0:
            for x in self.cacheCoordinateX:
                for y in self.cacheCoordinateY:
                    Adds.debug((x,y))
                    self.reassignBomb(x,y)
    
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
            self.gameManager(nearbyBombs)
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
        Adds.debug("Reasigned bomb")  # Imprime un mensaje para indicar que la bomba ha sido reasignada
        filas, columnas = self.find_dimensions(self.current_difficulty)  # Calcula las dimensiones del tablero de juego
        bomb_index = fila * columnas + columna  # Calcula el índice de la bomba en el tablero de juego
        Adds.debug(bomb_index)
        try:
            self.bombs.remove(bomb_index)  # Elimina la bomba de la lista de bombas
        except Exception as e:
            Adds.warning(f"Hubo un error:{e}")
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
        # Si el botón es de 'x' color (no ha sido presionado ni marcado con una bandera) y todavía quedan banderas disponibles
        if self.buttonsList[fila][columna]['bg'] == self.buttonColor and self.flags > 0:
            # Coloca una bandera en el botón
            self.flagsUsed+=1
            self.buttonsList[fila][columna].config(bg=self.flagButtonColor, image=self.flag)
            self.buttonsList[fila][columna]["state"] = tk.DISABLED # Desactiva el botón
            self.flags -= 1  # Disminuye el número de banderas disponibles
            self.updateFlagsCounter()  # Actualiza el contador de banderas
        # Si el botón es naranja (tiene una bandera)
        elif self.buttonsList[fila][columna]['bg'] == self.flagButtonColor:
            self.flagsUsed-=1
            # Quita la bandera del botón
            self.buttonsList[fila][columna].config(bg=self.buttonColor, image=self.transparent_image, compound="center")
            self.buttonsList[fila][columna]["state"] = tk.NORMAL # Vuelve a activar el boton
            
            self.flags += 1  # Aumenta el número de banderas disponibles
            self.updateFlagsCounter()  # Actualiza el contador de banderas

    def updateFlagsCounter(self)->None:
        self.flags_counter.config(text="Banderas disponibles: " + ("0" + str(self.flags) if self.flags < 10 else str(self.flags)))

    def saveStadistics(self)->None:
        Adds.debug((self.file_path, self.player.get(), self.time_actual,self.current_difficulty,self.pressedBombs,self.winnedGames,self.losedGames,self.flagsUsed))
        DataStadistics.addStats(self.file_path, self.player.get(), self.time_actual,self.current_difficulty,self.pressedBombs,self.winnedGames,self.losedGames,self.flagsUsed)

    def resetGame(self)->None:
        self.saveStadistics()
        Adds.debug("Reiniciando juego...")
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
        Adds.debug("Juego reiniciado!")

def debugConsole() -> None:
    commands = {
        "AutoWin": lambda: autoWin(),
        "BombReveal": lambda: bombReveal(),
    }

    def autoWin():
        Adds.debug(f"Eliminando {len(app.bombs) - 1} de la lista.")
        for _ in range(len(app.bombs) - 1):
            app.bombs.pop()

    def bombReveal():
        Adds.debug(f"Marcando {len(app.bombs) - 1} de la lista.")
        app.revealBombas(app.bombs, cheat=True)

    while True:
        command = input("Introduce un comando: ")
        try:
            if command in commands:
                commands[command]()
            else:
                exec(command)
        except Exception as e:
            l = traceback.format_exc()
            Adds.warning(f"Error al ejecutar el comando: {e} \n{l}")

if __name__ == "__main__" and os.path.isfile("img/coconut/coconut.jpeg"):
    try:
        if commandConsole:
            hilo_consola = threading.Thread(target=debugConsole, daemon=True)
            hilo_consola.start()
        root = Tk() 
        app = Minesweeper(root)  
        root.mainloop()  
    except Exception as e:
        # Si se captura un error no manejado en el nivel superior
        traceback_info = traceback.format_exc()
        Adds.critical(f"Error no manejado: {e}")
        Adds.critical(f"Traceback:\n{traceback_info}")
else:
    messagebox.showerror("Error", "Hubo un error fatal debido a la falta de un archivo esencial para la ejecucion.") 
