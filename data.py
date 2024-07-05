import csv
import random
import os
import json
import tkinter as tk
from tkinter import ttk
from utils import *
from images import *
try:
    from colorama import init as colorama_init
    from colorama import Fore
    from colorama import Style
except ModuleNotFoundError as e:
    #Adds.warning("Colorama no encontrado\n"
                 #"Descargando...")
    os.system("pip install colorama")
    #Adds.debug("Colorama instalado!")
    from colorama import init as colorama_init
    from colorama import Fore
    from colorama import Style

class DataStadistics:
    @staticmethod
    def getStats(file_path):
        """
        Obtiene las estadísticas completas almacenadas en el archivo JSON.
        
        :param file_path: Ruta del archivo JSON.
        :return: Lista de diccionarios de estadísticas.
        """
        try:
            with open(file_path, 'r') as file:
                stats = json.load(file)
                return stats
        except FileNotFoundError:
            Adds.warning(f"El archivo {file_path} no fue encontrado.")
            return []
        except json.JSONDecodeError:
            Adds.warning(f"Error al decodificar el archivo {file_path}.")
            return []

    @staticmethod
    def getStatPerUser(file_path, username):
        """
        Obtiene las estadísticas de un usuario específico.

        :param file_path: Ruta del archivo JSON.
        :param username: Nombre de usuario para buscar.
        :return: Lista con un diccionario de estadísticas del usuario o una lista vacía si no se encuentra.
        """
        stats = DataStadistics.getStats(file_path)
        user_stats = [stat for stat in stats if stat['username'].lower() == username.lower()]
        return user_stats

    @staticmethod
    def addStats(file_path, username, score, difficulty, bombsPressed, winnedGames, gameLosses, flagsUsed):
        """
        Agrega nuevas estadísticas al archivo JSON.

        :param file_path: Ruta del archivo JSON.
        :param username: Nombre de usuario.
        :param score: Tiempo obtenido.
        :param difficulty: Dificultad del juego.
        :param bombsPressed: Bombas presionadas.
        :param winnedGames: Juegos ganados.
        :param gameLosses: Juegos perdidos.
        :param flagsUsed: Banderas usadas.
        """
        stats = DataStadistics.getStats(file_path)
        new_stat = {
            'username': username,
            'score': score,
            'difficulty': difficulty,
            'bombsPressed': bombsPressed,
            'winnedGames': winnedGames,
            'gameLosses': gameLosses,
            'flagsUsed': flagsUsed
        }
        stats.append(new_stat)
        DataStadistics.saveStats(file_path, stats)
        DataStadistics.orderStats(file_path, "asc")
        DataStadistics.removeRedundancy(file_path)

    @staticmethod
    def saveStats(file_path, stats):
        """
        Guarda las estadísticas en el archivo JSON.

        :param file_path: Ruta del archivo JSON.
        :param stats: Lista de diccionarios de estadísticas.
        """
        try:
            with open(file_path, 'w') as file:
                json.dump(stats, file, indent=4)
        except FileNotFoundError:
            Adds.warning(f"El archivo {file_path} no fue encontrado.")

    @staticmethod
    def orderStats(file_path, order):
        """
        Ordena las estadísticas de usuario y tiempo en el archivo JSON.

        :param file_path: Ruta del archivo JSON.
        :param order: 'asc' para ordenar de menor a mayor, 'desc' para ordenar de mayor a menor.
        """
        stats = DataStadistics.getStats(file_path)
        if order == 'desc':
            # Ordena las estadísticas en orden descendente según el puntaje
            stats.sort(key=lambda x: x['score'], reverse=True)
        elif order == 'asc':
            # Ordena las estadísticas en orden ascendente según el puntaje
            stats.sort(key=lambda x: x['score'])
        else:
            Adds.debug("El parámetro 'order' debe ser 'asc' o 'desc'.")

        DataStadistics.saveStats(file_path, stats)

    @staticmethod
    def removeRedundancy(file_path):
        """
        Elimina la redundancia de datos en el archivo JSON, conservando solo el puntaje más alto para cada jugador.

        :param file_path: Ruta del archivo JSON.
        """
        stats = DataStadistics.getStats(file_path)
        player_scores = {}

        # Encuentra el puntaje más alto para cada jugador
        for stat in stats:
            player = stat['username']
            if player in player_scores:
                existing_stat = player_scores[player]
                # Reemplaza si el nuevo puntaje es mejor
                if stat['score'] < existing_stat['score']:
                    player_scores[player] = stat
                else:
                    # Actualiza solo los campos que no son de puntaje
                    existing_stat.update({
                        'bombsPressed': stat['bombsPressed'],
                        'winnedGames': stat['winnedGames'],
                        'gameLosses': stat['gameLosses'],
                        'flagsUsed': stat['flagsUsed']
                    })
            else:
                player_scores[player] = stat

        unique_stats = list(player_scores.values())

        DataStadistics.saveStats(file_path, unique_stats)
class Data:
    def getStats(file_path):
        """
        Obtiene las estadísticas completas almacenadas en el archivo CSV.
        
        :param file_path: Ruta del archivo CSV.
        :return: Lista de tuplas de estadísticas, donde cada tupla contiene (usuario, tiempo, dificultad).
        """
        stats = []
        try:
            with open(file_path, mode='r', newline='') as file:
                reader = csv.reader(file)
                next(reader)  # Saltar el encabezado
                for row in reader:
                    if len(row) >= 3:  # Verificar si la fila tiene al menos tres elementos
                        stats.append((row[0], int(row[1]), row[2]))
                    else:
                        print(f"La fila {reader.line_num} no tiene suficientes elementos.")
        except FileNotFoundError:
            Adds.warning(f"El archivo {file_path} no fue encontrado.")
        return stats

    def getStatPerUser(file_path, username):
        """
        Obtiene las estadísticas de un usuario específico.

        :param file_path: Ruta del archivo CSV.
        :param username: Nombre de usuario para buscar.
        :return: Tupla de estadísticas del usuario (usuario, tiempo).
        """
        try:
            with open(file_path, mode='r', newline='') as file:
                reader = csv.reader(file)
                next(reader)  # Saltar el encabezado
                for row in reader:
                    if row[0] == username:
                        return (row[0], int(row[1]))
        except FileNotFoundError:
            Adds.warning(f"El archivo {file_path} no fue encontrado.")
        return None

    def addStats(file_path, username, score, difficulty):
        """
        Agrega nuevas estadísticas al archivo CSV.

        :param file_path: Ruta del archivo CSV.
        :param username: Nombre de usuario.
        :param score: Tiempo obtenido.
        :param difficulty: Dificultad del juego.
        """
        try:
            with open(file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([username, score, difficulty])
        except FileNotFoundError:
            Adds.debug(f"El archivo {file_path} no fue encontrado.")
        Data.orderStats(file_path, "asc")
        Data.removeRedundancy(file_path)

    def orderStats(file_path, order):
        """
        Ordena las estadísticas de usuario y tiempo en el archivo CSV.

        :param file_path: Ruta del archivo CSV.
        :param order: 'asc' para ordenar de menor a mayor, 'desc' para ordenar de mayor a menor.
        """
        stats = Data.getStats(file_path)
        if order == 'desc':
            # Ordena las estadísticas en orden descendente según el puntaje
            stats.sort(key=lambda x: x[1], reverse=True)
        elif order == 'asc':
            # Ordena las estadísticas en orden ascendente según el puntaje
            stats.sort(key=lambda x: x[1])
        else:
            Adds.debug("El parámetro 'order' debe ser 'asc' o 'desc'.")

        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['username', 'score', 'difficulty'])
                # Escribe las estadísticas ordenadas en el archivo CSV
                for stat in stats:
                    writer.writerow(stat)
        except FileNotFoundError:
            Adds.warning(f"El archivo {file_path} no fue encontrado.")
            
    def removeRedundancy(file_path):
        """
        Elimina la redundancia de datos en el archivo CSV, conservando solo el puntaje más alto para cada jugador.
        
        :param file_path: Ruta del archivo CSV.
        """
        stats = Data.getStats(file_path)
        player_scores = {}

        # Encuentra el puntaje más alto para cada jugador
        for player, score, dif in stats:
            if player in player_scores:
                if score < player_scores[player][0]:
                    player_scores[player] = (score, dif)  # Actualiza el puntaje y la dificultad
            else:
                player_scores[player] = (score, dif)

        # Genera la lista de estadísticas únicas con puntaje más alto y dificultad
        unique_stats = [(player, score, dif) for player, (score, dif) in player_scores.items()]

        # Escribe las estadísticas únicas en el archivo CSV
        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['username', 'score', 'difficulty'])
                # Escribe las estadísticas únicas en el archivo CSV
                for stat in unique_stats:
                    writer.writerow(stat)
        except FileNotFoundError:
            Adds.warnign(f"El archivo {file_path} no fue encontrado.")
            
class DataTxt:
    def getStats(file_path):
        """
        Obtiene las estadísticas completas almacenadas en el archivo de texto.

        :param file_path: Ruta del archivo de texto.
        :return: Lista de tuplas de estadísticas, donde cada tupla contiene (usuario, tiempo, dificultad).
        """
        stats = []
        try:
            with open(file_path, mode='r') as file:
                next(file)  # Saltar la primera línea (encabezados)
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        try:
                            # Intenta convertir el segundo elemento a entero
                            stats.append((parts[0], int(parts[1]), parts[2]))
                        except ValueError:
                            Adds.warning(f"Error al convertir a entero en la línea: {line}")
                    else:
                        Adds.debug(f"La línea no tiene suficientes elementos: {line}")
        except FileNotFoundError:
            print(f"El archivo {file_path} no fue encontrado.")
        return stats

    def getStatPerUser(file_path, username):
        """
        Obtiene las estadísticas de un usuario específico.

        :param file_path: Ruta del archivo de texto.
        :param username: Nombre de usuario para buscar.
        :return: Tupla de estadísticas del usuario (usuario, tiempo).
        """
        try:
            with open(file_path, mode='r') as file:
                for line in file:
                    parts = line.strip().split(',')
                    if parts[0] == username:
                        try:
                            # Intenta convertir el segundo elemento a entero para el usuario específico
                            return (parts[0], int(parts[1]))
                        except ValueError:
                            print(f"Error al convertir a entero en la línea para usuario {username}: {line}")
        except FileNotFoundError:
            print(f"El archivo {file_path} no fue encontrado.")
        return None

    def addStats(file_path, username, score, difficulty):
        """
        Agrega nuevas estadísticas al archivo de texto.

        :param file_path: Ruta del archivo de texto.
        :param username: Nombre de usuario.
        :param score: Tiempo obtenido.
        :param difficulty: Dificultad del juego.
        """
        try:
            with open(file_path, mode='a') as file:
                # Escribe una nueva línea con el nombre de usuario, puntaje y dificultad
                file.write(f"{username},{score},{difficulty}\n")
        except FileNotFoundError:
            print(f"El archivo {file_path} no fue encontrado.")
        
        # Después de agregar, se ordenan las estadísticas y se elimina la redundancia
        DataTxt.orderStats(file_path, "asc")
        DataTxt.removeRedundancy(file_path)

    def orderStats(file_path, order):
        """
        Ordena las estadísticas de usuario y tiempo en el archivo de texto.

        :param file_path: Ruta del archivo de texto.
        :param order: 'asc' para ordenar de menor a mayor, 'desc' para ordenar de mayor a menor.
        """
        stats = DataTxt.getStats(file_path)
        if order == 'desc':
            stats.sort(key=lambda x: x[1], reverse=True)  # Ordena en orden descendente por el tiempo (segundo elemento)
        elif order == 'asc':
            stats.sort(key=lambda x: x[1])  # Ordena en orden ascendente por el tiempo (segundo elemento)
        else:
            print("El parámetro 'order' debe ser 'asc' o 'desc'.")

        try:
            with open(file_path, mode='w') as file:
                # Escribe la primera línea como encabezados
                file.write("username,score,difficulty\n")
                # Escribe cada estadística ordenada en el archivo
                for stat in stats:
                    file.write(f"{stat[0]},{stat[1]},{stat[2]}\n")
        except FileNotFoundError:
            print(f"El archivo {file_path} no fue encontrado.")

    def removeRedundancy(file_path):
        """
        Elimina la redundancia de datos en el archivo de texto, conservando solo el puntaje más alto para cada jugador.

        :param file_path: Ruta del archivo de texto.
        """
        stats = DataTxt.getStats(file_path)
        player_scores = {}

        # Encuentra y conserva solo el puntaje más alto para cada jugador
        for player, score, dif in stats:
            if player in player_scores:
                if score > player_scores[player][0]:
                    player_scores[player] = (score, dif)  # Actualiza el puntaje y la dificultad si es más alto
            else:
                player_scores[player] = (score, dif)

        # Genera una lista de estadísticas únicas con el puntaje más alto para cada jugador
        unique_stats = [(player, score, dif) for player, (score, dif) in player_scores.items()]

        try:
            with open(file_path, mode='w') as file:
                # Escribe la primera línea como encabezados
                file.write("username,score,difficulty\n")
                # Escribe cada estadística única en el archivo
                for stat in unique_stats:
                    file.write(f"{stat[2]},{stat[1]},{stat[2]}\n")
        except FileNotFoundError:
            print(f"El archivo {file_path} no fue encontrado.")
            
class Adds:
    def randomOverText()->str:
        """Retorna un String seleccionado desde una lista, la cadena de texto es tomada aleatoreamente desde la lista y
        es retornada.

        :return: Cadena de texto
        """
        list = ["JAJAJJAJAAJAJAJAJJAAJAJAJ.", "Capaz este no sea tu juego.", "Sos como adriel pero peor.", "Deberias comprarte unas manos.",
                "Sos mas malo que patear una embarazada.", "Buscate otro juego.", "El que pierde es ga- PARAAA NI TERMINE."]
        return random.choice(list)
    def debug(text)->None:
        """
            Solo es un print pero con un mensaje mas marcado para identificar el tipo de mensaje.
        :param text: String
        """
        colorama_init()
        print(f"{Fore.YELLOW}[DEBUG] {Fore.WHITE}{text}{Style.RESET_ALL}")
    def warning(text)->None:
        """
            Solo es un print pero con un mensaje mas marcado para identificar el tipo de mensaje.
        :param text: String
        """
        colorama_init()
        print(f"{Fore.RED}[WARNING] {Fore.WHITE}{text}{Style.RESET_ALL}")
    def critical(text)->None:
        colorama_init()
        print(f"{Fore.RED}[FATAL] {Fore.WHITE}{text}{Style.RESET_ALL}")
        
class RadialProgressbar(tk.Frame):
    """create radial flat progressbar

    basically this is a ttk horizontal progressbar modified using custom style layout and images

    Example:
        bar = RadialProgressbar(frame1, size=150, fg='green')
        bar.grid(padx=10, pady=10)
        bar.start()
    """

    # class variables to be shared between objects
    styles = []  # hold all style names created for all objects
    imgs = {}  # imgs{"size":{"color": img}}  example: imgs{"100":{"red": img}}

    def __init__(self, parent, size=100, bg=None, fg='cyan', text_fg=None, text_bg=None, font=None, font_size_ratio=0.1,
                 base_img=None, indicator_img=None, parent_bg=None, **extra):
        """initialize progressbar

        Args:
            parent  (tkinter object): tkinter container, i.e. toplevel window or frame
            size (int or 2-tuple(int, int)) size of progressbar in pixels
            bg (str): color of base ring
            fg(str): color of indicator ring
            text_fg (str): percentage text color
            font (str): tkinter font for percentage text, e.g. 'any 20'
            font_size_ratio (float): font size to progressbar width ratio, e.g. for a progressbar size 100 pixels,
                                     a 0.1 ratio means font size 10
            base_img (tk.PhotoImage): base image for progressbar
            indicator_img (tk.PhotoImage): indicator image for progressbar
            parent_bg (str): color of parent container
            extra: any extra kwargs

        """

        self.parent = parent
        self.parent_bg = parent_bg or get_widget_attribute(self.parent, 'background')
        self.bg = bg or calc_contrast_color(self.parent_bg, 30)
        self.fg = fg
        self.text_fg = text_fg or calc_font_color(self.parent_bg)
        self.text_bg = text_bg or self.parent_bg
        self.size = size if isinstance(size, (list, tuple)) else (size, size)
        self.font_size_ratio = font_size_ratio
        self.font = font or f'any {int((sum(self.size) // 2) * self.font_size_ratio)}'

        self.base_img = base_img
        self.indicator_img = indicator_img

        self.var = tk.IntVar()

        # initialize super class
        tk.Frame.__init__(self, master=parent)

        # create custom progressbar style
        self.bar_style = self.create_style()

        # create tk Progressbar
        self.bar = ttk.Progressbar(self, orient='horizontal', mode='determinate', length=self.size[0],
                                   variable=self.var, style=self.bar_style)
        self.bar.pack()

        # percentage Label
        self.percent_label = ttk.Label(self.bar, text='0%')
        self.percent_label.place(relx=0.5, rely=0.5, anchor="center")

        # trace progressbar value to show in label
        self.var.trace_add('write', self.show_percentage)

        # set default attributes
        self.config(**extra)

        self.start = self.bar.start
        self.stop = self.bar.stop

    def set(self, value):
        """set and validate progressbar value"""
        value = self.validate_value(value)
        self.var.set(value)

    def get(self):
        """get validated progressbar value"""
        value = self.var.get()
        return self.validate_value(value)

    def validate_value(self, value):
        """validate progressbar value
        """

        try:
            value = int(value)
            if value < 0:
                value = 0
            elif value > 100:
                value = 100
        except:
            value = 0

        return value

    def create_style(self):
        """create ttk style for progressbar

        style name is unique and will be stored in class variable "styles"
        """

        # create unique style name
        bar_style = f'radial_progressbar_{len(RadialProgressbar.styles)}'

        # add to styles list
        RadialProgressbar.styles.append(bar_style)

        # create style object
        s = ttk.Style()

        RadialProgressbar.imgs.setdefault(self.size, {})
        self.indicator_img = self.indicator_img or RadialProgressbar.imgs[self.size].get(self.fg)
        self.base_img = self.base_img or RadialProgressbar.imgs[self.size].get(self.bg)

        if not self.indicator_img:
            img = create_circle(self.size, color=self.fg)
            self.indicator_img = ImageTk.PhotoImage(img)
            RadialProgressbar.imgs[self.size].update(**{self.fg: self.indicator_img})

        if not self.base_img:
            img = create_circle(self.size, color=self.bg)
            self.base_img = ImageTk.PhotoImage(img)
            RadialProgressbar.imgs[self.size].update(**{self.bg: self.base_img})

        # create elements
        indicator_element = f'top_img_{bar_style}'
        base_element = f'bottom_img_{bar_style}'

        try:
            s.element_create(base_element, 'image', self.base_img, border=0, padding=0)
        except:
            pass

        try:
            s.element_create(indicator_element, 'image', self.indicator_img, border=0, padding=0)
        except:
            pass

        # create style layout
        s.layout(bar_style,
                 [(base_element, {'children':
                        [('pbar', {'side': 'left', 'sticky': 'nsew', 'children':
                                [(indicator_element, {'sticky': 'nswe'})]})]})])

        # configure new style
        s.configure(bar_style, pbarrelief='flat', borderwidth=0, troughrelief='flat')

        return bar_style

    def show_percentage(self, *args):
        """display progressbar percentage in a label"""
        bar_value = self.get()
        self.percent_label.config(text=f'{bar_value}%')

    def config(self, **kwargs):
        """config widgets' parameters"""

        # create style object
        s = ttk.Style()

        kwargs = {k: v for k, v in kwargs.items() if v}
        self.__dict__.update(kwargs)

        # frame bg
        self['bg'] = self.parent_bg

        # bar style configure
        s.configure(self.bar_style, background=self.parent_bg, troughcolor=self.parent_bg)

        # percentage label
        self.percent_label.config(background=self.text_bg, foreground=self.text_fg, font=self.font)