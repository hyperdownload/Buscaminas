import time

def apply_mod(game):

    # Definir una nueva versión de la función Itime
    def Itime():
        # Contador utilizando la función time y que no corte el hilo principal de ejecución
        start_time = time.time()
        while True:
            elapsed_time = time.time() - start_time
            print(f"Tiempo transcurrido: {elapsed_time:.2f} segundos")
            time.sleep(1)  # Pausar por un segundo para evitar una sobrecarga de la consola

    # Sobrescribir la función en el objeto del juego
    game.Itime = Itime
