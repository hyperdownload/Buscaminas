from tkinter import *
from tkinter import messagebox
import tkinter as tk
import random
import time
import threading
import traceback
import os
import importlib.util
from PIL import Image, ImageTk
import socket
import pickle
from tkinter import simpledialog

class ModManager:
    def __init__(self, mod_directory="mods"):
        try:
            self.mod_directory = mod_directory
            self.mods = []
            self.load_mods()
        except Exception as e:
            messagebox.showerror("Error", f"Error loading mods: {e}. Starting in vanilla mode.")

    def load_mods(self):
        if not os.path.exists(self.mod_directory):
            os.makedirs(self.mod_directory)
        for filename in os.listdir(self.mod_directory):
            if filename.endswith(".py"):
                self.load_mod(filename)
                    
    def load_mod(self, filename):
        mod_path = os.path.join(self.mod_directory, filename)
        spec = importlib.util.spec_from_file_location(filename[:-3], mod_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.mods.append(mod)

    def apply_mods(self, game):
        for mod in self.mods:
            if hasattr(mod, 'apply_mod'):
                mod.apply_mod(game)

class Minesweeper:
    def __init__(self, root, player_name="Player"):
        self.root = root
        self.player_name = player_name

        self.frame = Frame(self.root)
        self.frame.pack()

        self.root.title("Minesweeper")
        self.root.iconbitmap("img/bomba.ico")
        self.root.resizable(False, False)
        self.frame.config(width=400, height=400)

        self.navbar = Menu(self.root)
        self.root.config(menu=self.navbar)
        
        self.transparent_image = PhotoImage(width=1, height=1)

        # Mod Manager
        self.mod_manager = ModManager()
        self.mod_manager.apply_mods(self)

        self.player = tk.StringVar()
        self.player.set(self.player_name)

        self.file_path = 'stats.txt'
        self.file_menu = Menu(self.navbar, tearoff=0)
        self.file_menu.add_command(label="New Game", command=self.resetGame)
        self.file_menu.add_command(label="Stats", command=self.stats)
        self.file_menu.add_command(label="Options", command=self.options)
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        self.navbar.add_cascade(label="File", menu=self.file_menu)

        self.difficulty = {"Easy": 40, "Normal": 64, "Hard": 81, "ELDETONACULOS": 150}
        self.current_difficulty = self.difficulty["Easy"]

        self.buttonsList = []
        self.reset = False
        self.inicio = False
        self.timeInicio = time.time()
        self.flags = 0
        self.bombs = []
        self.contadortime = Label(self.frame)
        self.contadortime.grid(column=1, row=0, columnspan=4)
        self.flags_counter = Label(self.frame, text="Flags available: " + str(self.flags), font=("Arial 15"))
        self.flags_counter.grid(column=5, row=0, columnspan=4)

        img_bomb_original = Image.open("img/bomba3.png")
        img_flag_original = Image.open("img/bandera.png")

        img_bomb_rescaled = img_bomb_original.resize((50, 50), Image.LANCZOS)
        img_flag_rescaled = img_flag_original.resize((50, 50), Image.LANCZOS)

        self.bomb = ImageTk.PhotoImage(img_bomb_rescaled)
        self.flag = ImageTk.PhotoImage(img_flag_rescaled)

        self.isShakeWindowEnabled = tk.BooleanVar()
        self.isShakeWindowEnabled.set(True)

        self.currentAttemps = 3

        self.generateButtons()
        self.bombsRandom()

        self.server = None
        self.client = None
        self.server_thread = None
        self.client_thread = None

        self.is_server = False
        self.is_client = False

        self.connect_menu = Menu(self.navbar, tearoff=0)
        self.connect_menu.add_command(label="Host Game", command=self.hostGame)
        self.connect_menu.add_command(label="Join Game", command=self.joinGame)
        self.navbar.add_cascade(label="Multiplayer", menu=self.connect_menu)

    def hostGame(self):
        if self.is_server or self.is_client:
            messagebox.showerror("Error", "Already hosting or connected to a game.")
            return

        self.server_thread = threading.Thread(target=self.startServer)
        self.server_thread.start()

    def startServer(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('localhost', 12345))
        self.server.listen(1)

        self.is_server = True
        messagebox.showinfo("Host Game", "Waiting for connection...")
        client_socket, client_address = self.server.accept()
        self.client = client_socket
        messagebox.showinfo("Host Game", f"Connected to {client_address}")

        self.receiveThread = threading.Thread(target=self.receiveData)
        self.receiveThread.start()

    def joinGame(self):
        if self.is_server or self.is_client:
            messagebox.showerror("Error", "Already hosting or connected to a game.")
            return

        ip = simpledialog.askstring("Join Game", "Enter IP Address of the host:")
        if ip is None or ip.strip() == '':
            return

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((ip, 12345))
            self.is_client = True
            messagebox.showinfo("Join Game", "Connected to host.")
            self.receiveThread = threading.Thread(target=self.receiveData)
            self.receiveThread.start()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to {ip}: {e}")

    def receiveData(self):
        while True:
            try:
                data = pickle.loads(self.client.recv(1024))
                if data['type'] == 'press':
                    index = data['index']
                    self.slotPressed(index)
                elif data['type'] == 'flag':
                    index = data['index']
                    self.placeFlag(index)
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

    def sendData(self, data):
        try:
            self.client.send(pickle.dumps(data))
        except Exception as e:
            print(f"Error sending data: {e}")

    def difficultyToString(self, difficulty):
        if difficulty == self.difficulty["Easy"]:
            return "Easy"
        elif difficulty == self.difficulty["Normal"]:
            return "Normal"
        elif difficulty == self.difficulty["Hard"]:
            return "Hard"
        elif difficulty == self.difficulty["ELDETONACULOS"]:
            return "ELDETONACULOS"

    def stats(self):
        self.statsWindow = Toplevel(self.root)
        self.statsWindow.title("Statistics")
        self.statsWindow.geometry("300x200")
        
        stats = DataTxt.getStats(self.file_path)

        for i, (username, score, dif) in enumerate(stats):
            Label(self.statsWindow, text=f"Player: {username}").grid(row=i, column=0, padx=10, pady=5)
            Label(self.statsWindow, text=f"Time: {score}s").grid(row=i, column=1, padx=10, pady=5)
            Label(self.statsWindow, text=f"Difficulty: {dif}").grid(row=i, column=2, padx=10, pady=5)

    def options(self):
        self.optionsWindow = Toplevel(self.root)
        self.optionsWindow.title("Options")
        self.optionsWindow.geometry("300x250")

        options = ["Easy", "Normal", "Hard", "ELDETONACULOS"]

        selectedOption = StringVar(self.optionsWindow)
        selectedOption.set(self.difficultyToString(self.current_difficulty))

        def seleccionar_opcion(opcion):
            self.current_difficulty = self.difficulty[opcion]
            self.resetGame()

        self.entry = Entry(self.optionsWindow, width=30, textvariable=self.player)
        self.entry.grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        def applyInput():
            input_text = self.entry.get()
            messagebox.showinfo("Options changed", "Values adjusted correctly!")

        applyButton = Button(self.optionsWindow, text="Apply", command=applyInput)
        applyButton.grid(row=1, column=0, columnspan=2, pady=10)

        difficultyLabel = Label(self.optionsWindow, text="Difficulty:", font=("Arial", 12))
        difficultyLabel.grid(row=2, column=0, padx=10, pady=10, sticky=E)

        option_menu = OptionMenu(self.optionsWindow, selectedOption, *options, command=seleccionar_opcion)
        option_menu.grid(row=2, column=1, padx=10, pady=10, sticky=W)
        
        checkbox = ttk.Checkbutton(self.optionsWindow, text="Shake window on lose", variable=self.isShakeWindowEnabled)
        checkbox.grid(row=3, column=0, padx=10, pady=10)

        exitButton = Button(self.optionsWindow, text="Exit", command=self.optionsWindow.destroy)
        exitButton.grid(row=3, column=1, padx=10, pady=10)

    def generateButtons(self):
        for i in range(1, 9):
            for j in range(1, 9):
                self.buttonsList.append(Button(self.frame, text="", width=3, height=1, bg="gray", command=lambda i=i, j=j: self.slotPressed(i * 10 + j)))
                self.buttonsList[-1].bind("<Button-3>", lambda event, i=i, j=j: self.placeFlag(i * 10 + j))
                self.buttonsList[-1].grid(row=i, column=j)
                self.buttonsList[-1].bind('<Enter>', self.on_enter)
                self.buttonsList[-1].bind('<Leave>', self.on_leave)

    def placeFlag(self, index):
        if self.flags > 0:
            row = index // 10
            column = index % 10

            self.buttonsList[row * 8 + column - 9]['image'] = self.flag
            self.flags -= 1
            self.flags_counter.config(text="Flags available: " + str(self.flags))

            self.sendData({'type': 'flag', 'index': index})
            self.checkVictory()

    def slotPressed(self, index):
        if self.is_server:
            self.sendData({'type': 'press', 'index': index})

        if not self.inicio:
            self.inicio = True
            self.generateBombs(self.current_difficulty, (index // 10) * 8 + (index % 10) - 9)

            for bomb in self.bombs:
                self.buttonsList[bomb].config(bg="gray")
                self.buttonsList[bomb]['image'] = self.bomb

            self.timeInicio = time.time()

        if self.reset:
            self.reset = False
            self.bombsRandom()
            self.timeInicio = time.time()
            self.inicio = False

            for i in self.buttonsList:
                i.config(bg="gray")
                i['image'] = self.transparent_image

        row = index // 10
        column = index % 10

        value = 0
        if index >= 0 and index <= 8:
            self.showAlert("Warning", "You're outside the window!")
            return
        else:
            for bomb in self.bombs:
                if index == bomb:
                    self.buttonsList[bomb]['image'] = self.bomb
                    self.showAlert("RIP", "You clicked on a bomb!")
                    return

            for i in range(-1, 2):
                for j in range(-1, 2):
                    if (row + i) >= 0 and (column + j) >= 0 and (row + i) <= 8 and (column + j) <= 8:
                        index2 = ((row + i) * 8) + (column + j)

                        if index2 in self.bombs:
                            value += 1

            if value == 0:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if (row + i) >= 0 and (column + j) >= 0 and (row + i) <= 8 and (column + j) <= 8:
                            if (row + i) * 8 + column + j not in self.bombs:
                                self.buttonsList[(row + i) * 8 + column + j]['bg'] = "white"
                                self.buttonsList[(row + i) * 8 + column + j].config(
                                    text=str(0), state="disabled")
                                self.openSpace((row + i) * 8 + column + j)

            self.buttonsList[row * 8 + column]['bg'] = "white"
            self.buttonsList[row * 8 + column].config(
                text=str(value), state="disabled")

            self.checkVictory()

    def openSpace(self, index):
        row = index // 8
        column = index % 8

        for i in range(-1, 2):
            for j in range(-1, 2):
                if (row + i) >= 0 and (column + j) >= 0 and (row + i) <= 8 and (column + j) <= 8:
                    if self.buttonsList[(row + i) * 8 + column + j]['bg'] == "gray":
                        value = 0

                        for k in range(-1, 2):
                            for l in range(-1, 2):
                                if (row + i + k) >= 0 and (column + j + l) >= 0 and (row + i + k) <= 8 and (
                                        column + j + l) <= 8:
                                    if ((row + i + k) * 8) + column + j + l in self.bombs:
                                        value += 1

                        if value == 0:
                            for k in range(-1, 2):
                                for l in range(-1, 2):
                                    if (row + i + k) >= 0 and (column + j + l) >= 0 and (row + i + k) <= 8 and (
                                            column + j + l) <= 8:
                                        if ((row + i + k) * 8) + column + j + l not in self.bombs:
                                            self.buttonsList[((row + i + k) * 8) + column + j + l]['bg'] = "white"
                                            self.buttonsList[((row + i + k) * 8) + column + j + l].config(
                                                text=str(0), state="disabled")
                                            self.openSpace(((row + i + k) * 8) + column + j + l)
                        self.buttonsList[(row + i) * 8 + column + j]['bg'] = "white"
                        self.buttonsList[(row + i) * 8 + column + j].config(
                            text=str(value), state="disabled")

    def bombsRandom(self):
        for i in range(1, self.current_difficulty):
            self.bombs.append(random.randint(0, 63))

    def checkVictory(self):
        cont = 0

        for i in self.buttonsList:
            if i['bg'] == "gray" or i['bg'] == "yellow":
                cont += 1

        if cont == self.current_difficulty:
            self.showAlert("Congratulations", "The game is over, well done! Now you should register your score!")
            Data.guardarStats(self.file_path, self.player.get(), int(time.time() - self.timeInicio),
                              self.difficultyToString(self.current_difficulty))

    def resetGame(self):
        self.reset = True
        self.inicio = False
        self.flags = 0
        self.flags_counter.config(text="Flags available: " + str(self.flags))

        for i in self.buttonsList:
            i.config(bg="gray")
            i['image'] = self.transparent_image

    def showAlert(self, title, message):
        messagebox.showinfo(title, message)
        self.resetGame()

    def on_enter(self, event):
        widget = event.widget
        widget.config(bg='yellow')

    def on_leave(self, event):
        widget = event.widget
        widget.config(bg='gray')

if __name__ == "__main__":
    root = Tk()
    game = Minesweeper(root)
    root.mainloop()

