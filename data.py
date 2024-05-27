import csv

class Data:
    def getStats(file_path):
        stats = []
        try:
            with open(file_path, mode='r', newline='') as file:
                reader = csv.reader(file)
                next(reader)  # Saltar el encabezado
                for row in reader:
                    if len(row) >= 2:  # Verificar si la fila tiene al menos dos elementos
                        stats.append((row[0], int(row[1])))
                    else:
                        print(f"La fila {reader.line_num} no tiene suficientes elementos.")
        except FileNotFoundError:
            print(f"El archivo {file_path} no fue encontrado.")
        return stats

    def getStatPerUser(file_path, username):
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

    def addStats(file_path, username, score):
        try:
            with open(file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([username,score])
        except FileNotFoundError:
            print(f"El archivo {file_path} no fue encontrado.")
        Data.orderStats(file_path, "asc")
        Data.removeRedundancy(file_path)

    def orderStats(file_path, order):
        """
        Ordena las estadísticas de usuario y puntaje en el archivo CSV.
        :param file_path: Ruta del archivo CSV
        :param order: 'asc' para ordenar de menor a mayor, 'desc' para ordenar de mayor a menor
        """
        stats = Data.getStats(file_path)
        if order == 'desc':
            stats.sort(key=lambda x: x[1], reverse=True)
        elif order == 'asc':
            stats.sort(key=lambda x: x[1])
        else:
            print("El parámetro 'order' debe ser 'asc' o 'desc'.")

        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['username', 'score'])
                for stat in stats:
                    writer.writerow(stat)
        except FileNotFoundError:
            print(f"El archivo {file_path} no fue encontrado.")
            
    def removeRedundancy(file_path):
        """
        Elimina la redundancia de datos en el archivo CSV, conservando solo el puntaje más alto para cada jugador.
        :param file_path: Ruta del archivo CSV
        """
        stats = Data.getStats(file_path)
        player_scores = {}
        for player, score in stats:
            if player in player_scores:
                player_scores[player] = min(player_scores[player], score)
            else:
                player_scores[player] = score

        unique_stats = [(player, score) for player, score in player_scores.items()]

        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['username', 'score'])
                for stat in unique_stats:
                    writer.writerow(stat)
        except FileNotFoundError:
            print(f"El archivo {file_path} no fue encontrado.")