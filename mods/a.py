import time
import random
def apply_mod(game):
    # Save the reference of the original function
    original_slotPulsado = game.slotPressed

    # Define a new version of the function
    def slotPressed(c):
        filas, columnas = game.find_dimensions(game.current_difficulty)
        fila, columna = c
        if random.randint(1, 2) == 1:
            current_geometry = game.root.winfo_geometry()
            current_x = int(current_geometry.split('+')[1])
            current_y = int(current_geometry.split('+')[2])
            new_x = current_x + 50 if random.choice([True, False]) else current_x - 50
            game.root.geometry(f'+{new_x}+{current_y}')
        if not game.inicio:
            if fila * columnas + columna in game.bombas and game.current_difficulty in [game.difficulty["Easy"], game.difficulty["Normal"]]:
                # Reassign bomb
                game.reassignBomb(fila, columna)

            game.tiempoInicio = time.time()
            game.tiempoHabilitado = True
            game.tiempo()
            game.inicio = True
        
        if game.listaBotones[fila][columna]['text'] == '' and game.listaBotones[fila][columna]['bg'] == 'grey':
            bombas_cercanas = game.contarBombasCercanas(c)
            game.listaBotones[fila][columna].config(bg='SystemButtonFace', text=str(bombas_cercanas) if bombas_cercanas > 0 else '', fg=game.coloration(bombas_cercanas))
            if bombas_cercanas == 0:
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = columna + dx, fila + dy
                        if 0 <= nx < columnas and 0 <= ny < filas:
                            adj_index = (ny, nx)
                            if adj_index not in game.bombas and game.listaBotones[ny][nx]['text'] == '' and game.listaBotones[ny][nx]['bg'] == 'grey':
                                slotPulsado(adj_index)
            game.checkWin()
    
    # Sobrescribir la función en el objeto del juego
    #game.slotPulsado = slotPulsado