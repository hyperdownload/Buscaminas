def apply_mod(game):
    # Guardar la referencia de la función original
    original_reset_game = game.resetGame

    # Definir una nueva versión de la función
    def new_resetGame():
        print("El juego se está reiniciando con una nueva funcionalidad")
        original_reset_game()  # Llamar a la función original
    
    # Sobrescribir la función en el objeto del juego
    game.resetGame = new_resetGame