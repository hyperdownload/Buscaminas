import time
import random
def apply_mod(game):
    # Save the reference of the original function
    original_slotPulsado = game.slotPressed
    game.root.title("Buscaminas")
