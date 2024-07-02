import csv
import random
try:
    from colorama import init as colorama_init
    from colorama import Fore
    from colorama import Style
except ModuleNotFoundError as e:
    Adds.warning("Colorama no encontrado\n"
                 "Descargando...")
    os.system("pip install colorama")
    Adds.debug("Colorama instalado!")
    from colorama import init as colorama_init
    from colorama import Fore
    from colorama import Style

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
                    file.write(f"{stat[0]},{stat[1]},{stat[2]}\n")
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