import csv

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
            print(f"El archivo {file_path} no fue encontrado.")
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
            print(f"El archivo {file_path} no fue encontrado.")
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
            print(f"El archivo {file_path} no fue encontrado.")
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
            print("El parámetro 'order' debe ser 'asc' o 'desc'.")

        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['username', 'score', 'difficulty'])
                # Escribe las estadísticas ordenadas en el archivo CSV
                for stat in stats:
                    writer.writerow(stat)
        except FileNotFoundError:
            print(f"El archivo {file_path} no fue encontrado.")
            
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
            print(f"El archivo {file_path} no fue encontrado.")
