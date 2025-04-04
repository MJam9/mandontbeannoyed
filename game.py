import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import numpy as np
import time
from tkinter import Tk

from board import Board
from player import Player
from database import DiceStatistics
#from diceGUI import DiceDecisionGUI  

class Game:
    def __init__(self, nplayer, fast, autoroll):
        self.nplayer = nplayer
        self.current_player_id = 0
        self.steps = 0
        self.fast = fast
        self.autoroll = autoroll
        self.stats = DiceStatistics(reset_db=True)  # Datenbank für Würfelstatistik
        self.init_players()

        # Pygame GUI initialisieren
        #self.gui = DiceDecisionGUI(self)  # GUI-Instanz erstellen
        pygame.init()
        self.font = pygame.font.Font('freesansbold.ttf', 25)  # Schriftart für Buttons und Text

    def init_players(self):
        if self.nplayer == 2:
            self.players = [Player(1), Player(3)]
        else:
            self.players = [Player(i) for i in range(1, self.nplayer+1)]

        # Jeden Spieler in der Datenbank registrieren
        for player in self.players:
            self.stats.add_new_player(f"Player {player.player_id}") 

    def current_player(self):
        return self.players[self.current_player_id]
    
    def next_player(self, board):
        self.steps = 0
        board.steps = self.steps
        self.current_player_id = (self.current_player_id + 1) % len(self.players)
        board.current_player(self.current_player_id)
        board.refresh_board()

    def roll_dice(self):
        """Würfelt eine Zahl und speichert sie in der Datenbank."""
        dice_value = np.random.randint(1, 7) 
        print("Rolled:", dice_value)
        return dice_value
    
        #3 Fach Würfel -> umgesetzt bei Beginn alle im Haus 
        # nicht umgesetzt bei der zwischen Ziel
        #"""Würfelt für den aktuellen Spieler und berücksichtigt, ob 3 Versuche erlaubt sind."""
        #current_player = self.players[self.current_player_id]

        # Prüfen, ob alle Figuren noch im Haus sind
        #all_pieces_in_house = all(piece.position == -1 for piece in current_player.pieces)

        #max_attempts = 3 if all_pieces_in_house else 1  # 3 Würfe nur, wenn alle Figuren noch im Haus sind

        #for attempt in range(max_attempts):
        #    dice_value = np.random.randint(1, 7)
        #    print(f"Player {current_player.player_id} würfelt {dice_value} (Versuch {attempt + 1}/{max_attempts})")
        #    # pygame.display.flip()
        #    # board.refresh_board()
        #    time.sleep(1)  # Zeigt den Wurf für eine Sekunde, bevor neu gewürfelt wird

        #    # Falls eine 6 geworfen wurde oder der Spieler nicht erneut würfeln darf, beenden wir die Schleife
        #    if dice_value == 6 or max_attempts == 1:
        #        return dice_value

        #return dice_value  # Letzter Wurf wird zurückgegeben, falls keine 6 dabei war
    
    def calculate_distance(self, mouse_pos, piece_pos):
        dx = mouse_pos[0] - piece_pos[0]
        dy = mouse_pos[1] - piece_pos[1]
        return np.sqrt((dx ** 2 + dy ** 2))
    
    def find_clicked_piece(self, mouse_pos, moveable_pieces):
        mouse_pos = [(pos-10)/50-0.5 for pos in pygame.mouse.get_pos()]
        dist = [self.calculate_distance(mouse_pos, [p.x, p.y]) for p in moveable_pieces]
        piece = moveable_pieces[np.argmin(dist)]
        return piece
    
    def undisplay_movable(self, board, pieces):
        for piece in pieces:
            piece.movable = False
        board.refresh_board()

    def display_movable(self, board, pieces):
        for piece in pieces:
            piece.movable = True
        board.refresh_board()

    def find_moveable_pieces(self):
        if self.steps == 0:
            self.moveable_pieces = []
        else:
            self.moveable_pieces = self.current_player().find_moveable_pieces(self.steps)
        self.move_pieces_id = sorted([piece.piece_id for piece in self.moveable_pieces])

    def ask_to_save_roll(self, dice_value, board):
        """Fragt den Spieler, ob er den Wurf speichern möchte, aber nur wenn er ihn auch spielen könnte."""
        print("aufruf von aks_to_save_roll")
        current_player = self.players[self.current_player_id]

        # Prüfen, ob mit dem geworfenen Würfelwert überhaupt ein Zug möglich wäre
        move_possible = False
        for piece in current_player.pieces:
            if piece.position == -1:  
                if dice_value == 6:  # Figur kann nur mit einer 6 rauskommen
                    move_possible = True
                    break
            elif piece.position + dice_value <= 43:  # Bewegung innerhalb des Spielfelds möglich
                move_possible = True
                break

        if not move_possible:
            return "n"  # Kein Zug möglich, sofort abbrechen

        # Buttons anzeigen und auf Spieleraktion warten (Board verwaltet das UI)
        choice = board.show_save_buttons(dice_value)

        # Entscheidung auswerten
        if choice == "s":
            self.stats.add_wurf(f"Player {current_player.player_id}", dice_value)
            print(f"Player {current_player.player_id} hat {dice_value} gespeichert!")
        else:
            print("Zahl wird nicht gespeichert. Spieler zieht normal.")

        return choice
    
    def use_db(self, dice_value):
        current_player = self.players[self.current_player_id]
        self.stats.decrease_wurf(f"Player {current_player.player_id}", dice_value)
        print(f"Player {current_player.player_id} hat {dice_value} eins Abgezogen!")

    def move_roll_dice(self, board, screen):
        if self.fast or self.autoroll:
            self.steps = self.roll_dice()
            choice = self.ask_to_save_roll(self.steps, board)  # GUI nutzen
            if choice == "s":
                self.steps = 0  # Kein Zug, wenn gespeichert wurde
            board.steps = self.steps
            board.refresh_board()
            if self.autoroll:
                time.sleep(0.5)
            return True
        else:
            # Event-Verarbeitung während des Wartens auf den Button
            
            while not board.show_roll_die():
                pygame.event.pump()  # Verarbeitet alle Events, damit der Button-Klick registriert wird
                time.sleep(0.1)  # Kurze Pause zur Entlastung der CPU


            self.steps = self.roll_dice()  # Würfeln
            choice = self.ask_to_save_roll(self.steps, board)  # Frage, ob speichern
            if choice == "s":
                self.steps = 0  # Kein Zug, wenn gespeichert wurde
            board.steps = self.steps
            board.refresh_board()
            time.sleep(0.3)  # Kurze Pause nach dem Wurf
            return True  # Würfeln abgeschlossen, weitermachen

                #elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN] and not self.fast:
                #    self.steps = self.roll_dice()
                #    choice = self.ask_to_save_roll(self.steps, board)  # Spieler muss eine Entscheidung treffen
                #    if choice == "s":
                #        self.steps = 0  # Kein Zug, wenn gespeichert wurde
                #    board.steps = self.steps
                #    board.refresh_board()
                #    time.sleep(0.3)
                #    return True
                
                

    def move_select_piece(self):
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                return -1
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return self.find_clicked_piece(pygame.mouse.get_pos(), self.moveable_pieces)
            
    def check_hit_opponent(self):
        new_pos_abs = (self.current_player().offset + self.new_pos) % 40
        for player in self.players:
            if player.player_id == self.current_player().player_id:
                continue
            for piece in player.pieces:
                if self.new_pos < 40 and piece.position < 40 and (piece.position + player.offset) % 40 == new_pos_abs:
                    piece.return_home()
                    break

    def move_piece(self, board):
        if self.fast:
            self.moveable_pieces = self.moveable_pieces[:1]
        moved = False
        # no moveable pieces
        if len(self.moveable_pieces) == 0:
            if not self.fast: time.sleep(1)
        # only one moveable piece
        elif len(self.moveable_pieces) == 1:
            if not self.fast: time.sleep(0.3)
            self.new_pos = self.moveable_pieces[0].move_piece(self.steps)
            moved = True
        # all moveable pieces are home
        elif all(p == -1 for p in [p.position for p in self.moveable_pieces]):
            if not self.fast: time.sleep(0.3)
            self.new_pos = self.moveable_pieces[-1].move_piece(self.steps)
            moved = True
        # multiple moveable pieces
        else:
            self.display_movable(board, self.moveable_pieces)
            #TODO: Need to have an option to select a piece by number
            piece = self.move_select_piece()
            if piece == -1:
                return False
            self.new_pos = piece.move_piece(self.steps)
            moved = True
            self.undisplay_movable(board, self.moveable_pieces)
        return moved

    def get_state(self):
        pos = [[piece.position for piece in player.pieces] for player in self.players]
        cur_player = self.current_player().player_id
        die = self.steps
        self.find_moveable_pieces()
        return pos, cur_player, die, self.move_pieces_id, self.winner

    def run_game(self):
        pygame.init()
        screen = pygame.display.set_mode((800, 600))  # Größe des Fensters
        board = Board(self.players, self.stats)
        board.init_board()

        running = True
        self.winner = 0
        while running:
            board.current_player(self.current_player_id)
            board.refresh_board()

            #print(f'Roll dice, state: {self.get_state()}')
            if not self.move_roll_dice(board, screen):
                running = False

            self.find_moveable_pieces()

            #print(f'Move piece, state: {self.get_state()}')
            moved = self.move_piece(board)
            if moved:
                self.check_hit_opponent()
                board.refresh_board()

            if not self.current_player().won_game():
                if self.steps != 6 or not moved:
                    self.next_player(board)
                else:
                    self.steps = 0
            board.refresh_board()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if self.current_player().won_game():
                self.winner = self.current_player().player_id
                running = False

        if self.winner != 0:
            board.show_winner()
            game_over = True
            while game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_over = False
            pygame.quit()

    pygame.quit()


