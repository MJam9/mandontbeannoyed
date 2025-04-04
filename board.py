import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import time
import numpy as np
from field import Field
from database import DiceStatistics  # Importiere die Datenbankklasse
from rollstate import RollState

class Board():
    def __init__(self, players, db_instance, cell_size=50, border=10):
       self.players = players
       self.ncels = 11
       self.border = border
       self.screen_width = self.ncels*cell_size + 2*border
       self.screen_height = self.ncels*cell_size + 2*border + 70
       self.bg_color = 'oldlace'
       self.steps = 0
       self.board_fields = {}
       self.font = pygame.font.Font('freesansbold.ttf', 35)
       self.db = db_instance  # Datenbankinstanz speichern

    def init_board(self):
       pygame.display.set_caption("Man, don't be annoyed")
       self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
       self.screen.fill(self.bg_color)

    def add_fields(self):
       grid = [list([] for x in range(0, self.ncels)) for y in range(0, self.ncels)]
       colors = np.genfromtxt("board_colors.csv", delimiter=",", dtype=str)
       track = np.genfromtxt("board.csv", delimiter=",", dtype=str)

       for y in range(0, self.ncels):
           for x in range(0, self.ncels):
               if colors[y][x] != '5':
                   grid[x][y] = Field(x, y, colors[y][x], track[y][x])
                   grid[x][y].draw_field(self.screen)
                   self.board_fields[track[y][x].lstrip()] = grid[x][y]
       return grid

    def get_field(self, field_id):
       return self.board_fields[field_id]    

    def show_pieces(self):
       for player in self.players:
           for piece in player.pieces:
               if piece.is_home():
                   field = self.get_field(f'H{player.player_id}{piece.piece_id}')
                   if piece.movable:
                       field.draw_movable_piece(self.screen, piece.color)
                   else:
                       field.draw_piece(self.screen, piece.color)
               elif piece.is_in_goal():
                   field = self.get_field(f'{player.player_id}{piece.position}')
                   if piece.movable:
                       field.draw_movable_piece(self.screen, piece.color)
                   else:
                       field.draw_piece(self.screen, piece.color)
               else:
                   field = self.get_field(f'{(player.offset + piece.position)%40}')
                   if piece.movable:
                       field.draw_movable_piece(self.screen, piece.color)
                   else:
                       field.draw_piece(self.screen, piece.color)
               piece.x = field.x
               piece.y = field.y

    def current_player(self, player):
       self.player = player

    def show_player(self):
       font = pygame.font.Font('freesansbold.ttf', 35)
       text = font.render(f'Player {self.player+1}', True, pygame.Color("black"))
       textRect = text.get_rect()
       textRect.center = (self.screen_width//4, self.screen_height-20)
       self.screen.blit(text, textRect)

    def show_roll_die(self):
        """Zeigt einen Button zum Würfeln an und wartet auf die Auswahl des Spielers."""
        font = pygame.font.Font('freesansbold.ttf', 35)
        font_small = pygame.font.Font('freesansbold.ttf', 25)

        # Position des ursprünglichen Textes
        text_x = self.screen_width // 4 + self.screen_width // 2
        text_y = self.screen_height - 20

        # Button für "Würfeln"
        roll_button = pygame.Rect(text_x - 75, text_y - 10, 150, 20)  # Position leicht anpassen für Button-Größe

        # Text für den Button rendern
        roll_text = font.render('Würfeln', True, pygame.Color("black"))

        # UI-Elemente für den "Würfeln"-Button zeichnen
        pygame.draw.rect(self.screen, pygame.Color(self.bg_color), roll_button, border_radius=10)

        # Text zentrieren und auf den Button setzen
        roll_text_rect = roll_text.get_rect(center=roll_button.center)
        self.screen.blit(roll_text, roll_text_rect)

        # Abrufen der Würfelstatistiken
        player_name = f'Player {self.players[self.player].player_id}'
        stats = self.db.get_statistics(player_name)  # Statistiken abrufen

        # Falls keine Daten vorhanden sind, ersetze durch 0
        stats = {i: stats.get(i, 0) for i in range(1, 7)}

        # Positionierung der Statistik-Buttons
        button_width = 50
        button_height = 30
        button_x_start = self.screen_width // 2 - 230  # Startpunkt
        button_y = self.screen_height - 70  # Vertikale Position der Buttons

        self.button_rects = []  # Speichert die klickbaren Bereiche

        # Buttons für jede Zahl erstellen
        for i in range(1, 7):
            button_rect = pygame.Rect(button_x_start + (i - 1) * (button_width + 30), button_y, button_width, button_height)
            self.button_rects.append((button_rect, i))  # Speichern der Rechtecke mit der Zahl

            # Text rendern
            button_text = font_small.render(f"{i}x{stats[i]}", True, pygame.Color("black"))

            # Button zeichnen
            pygame.draw.rect(self.screen, pygame.Color("lightgray"), button_rect, border_radius=5)
            text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, text_rect)

        pygame.display.flip()

        # # Events abfragen und verarbeiten
        # events = pygame.event.get()
        # for event in events:
        #     if event.type == pygame.QUIT:
        #         return False
            
        #     # Nur Mausbuttondown-Event berücksichtigen
        #     if event.type == pygame.MOUSEBUTTONDOWN:
        #         mouse_x, mouse_y = pygame.mouse.get_pos()

        #         # Prüfen, ob der "Würfeln"-Button geklickt wurde
        #         if roll_button.collidepoint(mouse_x, mouse_y):
        #             print("Würfeln button geklickt")
        #             return True  # Gib zurück, dass der Würfeln-Button geklickt wurde

        #         # Prüfen, ob einer der Zahl-Buttons geklickt wurde
        #         for button_rect, value in self.button_rects:
        #             if button_rect.collidepoint(mouse_x, mouse_y):
        #                 print(f"Zahl {value} gewählt")  # Ausgabe der gewählten Zahl in der Konsole

        # return False  # Falls kein Button gedrückt wurde

        # Events abfragen und verarbeiten
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return RollState.WAITING  # Das Warten wird angezeigt, wenn das Fenster geschlossen wird
        
            # Nur Mausbuttondown-Event berücksichtigen
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Prüfen, ob der "Würfeln"-Button geklickt wurde
                if roll_button.collidepoint(mouse_x, mouse_y):
                    print("Würfeln button geklickt")
                    return RollState.ROLL  # Zurückgeben, dass "Würfeln" gewählt wurde

                # Prüfen, ob einer der Zahl-Buttons geklickt wurde
                for button_rect, value in self.button_rects:
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        print(f"Zahl {value} gewählt")  # Ausgabe der gewählten Zahl in der Konsole
                        return RollState(value)  # Zurückgeben der entsprechenden Zahl

        return RollState.WAITING  # Wenn kein Button gedrückt wurde, zurückgeben, dass gewartet wird

    def show_die_result(self):
       font = pygame.font.Font('freesansbold.ttf', 35)
       text = font.render(f'Rolled {self.steps}', True, pygame.Color("black"))
       textRect = text.get_rect()
       textRect.center = (self.screen_width//4 + self.screen_width//2, self.screen_height-20)
       self.screen.blit(text, textRect)

    def show_winner(self):
       text_area_rect = pygame.Rect(0, self.screen_height - 50, self.screen_width, 50)
       self.screen.fill((self.bg_color), text_area_rect)
       font = pygame.font.Font('freesansbold.ttf', 35)
       text = font.render(f'Player {self.player+1} wins!', True, pygame.Color("black"))
       textRect = text.get_rect()
       textRect.center = (self.screen_width//2, self.screen_height-20)
       self.screen.blit(text, textRect)
       pygame.display.flip()

    def show_next_move(self):
       text_area_rect = pygame.Rect(0, self.screen_height - 70, self.screen_width, 70)
       self.screen.fill((self.bg_color), text_area_rect)
       self.show_player()

       if self.steps == 0:
           self.show_roll_die()
       else:
           self.show_die_result()
           #self.show_db_status() -> einfache text anzeige umschreiben

    def show_db_status(self):
        """Zeigt die Würfelstatistiken für den aktuellen Spieler an."""
        # Richtigen Spielernamen holen
        player_name = f'Player {self.players[self.player].player_id}'
        stats = self.db.get_statistics(player_name)  # Statistiken abrufen

       # Falls keine Daten vorhanden sind, ersetze durch 0
        stats = {i: stats.get(i, 0) for i in range(1, 7)}

        font = pygame.font.Font('freesansbold.ttf', 25)


        # Positionierung der Buttons
        button_width = 30
        button_height = 30
        button_x_start = self.screen_width // 2 - 200  # Startpunkt
        button_y = self.screen_height - 70  # Vertikale Position der Buttons

        self.button_rects = []  # Speichert die klickbaren Bereiche

        for i in range(1, 7):
            # Button für jede Zahl erstellen
            button_rect = pygame.Rect(button_x_start + (i - 1) * (button_width + 30), button_y, button_width, button_height)
            self.button_rects.append((button_rect, i))  # Speichern der Rechtecke mit der Zahl

            # Text rendern
            button_text = font.render(f"{i}x{stats[i]}", True, pygame.Color("black"))

            # Button zeichnen
            pygame.draw.rect(self.screen, pygame.Color("lightgray"), button_rect, border_radius=5)
            text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, text_rect)

        pygame.display.flip()

        # Überprüfen der Events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False

            # Prüfen, ob einer der Statistik-Buttons geklickt wurde
            result = self.handle_mouse_click_on_button(event, None, self.button_rects)
            if result:
                return result  # Gibt die gewählte Zahl zurück
        return None  # Falls kein Button gedrückt wurde
        
    def handle_button_click(self, pos):
       """Überprüft, ob eine Zahl geklickt wurde und gibt die gewählte Zahl aus."""
       for button_rect, number in self.button_rects:
           if button_rect.collidepoint(pos):
               print(f"Zahl {number} gewählt")
               return number  # Gibt die gewählte Zahl zurück
       return None

    def show_save_buttons(self, dice_value):
       """Zeigt die Buttons 'Speichern' und 'Spielen' an und wartet auf die Auswahl des Spielers."""
       font = pygame.font.Font('freesansbold.ttf', 30)
       
       # UI-Bereich für Buttons löschen
       pygame.draw.rect(self.screen, pygame.Color(self.bg_color), 
                    pygame.Rect(0, self.screen_height - 70, self.screen_width, 70))

       save_button = pygame.Rect(50, self.screen_height - 60, 150, 50)
       no_save_button = pygame.Rect(210, self.screen_height - 60, 150, 50)
       dice_text_rect = pygame.Rect(380, self.screen_height - 60, 150, 50)

       # Texte rendern
       save_text = font.render('Speichern', True, pygame.Color("black"))
       no_save_text = font.render('Spielen', True, pygame.Color("black"))
       dice_text = font.render(f'Wurf: {dice_value}', True, pygame.Color("black"))

       # UI-Elemente zeichnen
       pygame.draw.rect(self.screen, pygame.Color(self.bg_color), save_button, border_radius=20)
       pygame.draw.rect(self.screen, pygame.Color(self.bg_color), no_save_button, border_radius=20)
   
       # Texte zentrieren und auf die Buttons setzen
       save_text_rect = save_text.get_rect(center=save_button.center)
       no_save_text_rect = no_save_text.get_rect(center=no_save_button.center)
       dice_text_rect = dice_text.get_rect(center=(self.screen_width - 90, self.screen_height - 35))

       self.screen.blit(save_text, save_text_rect)
       self.screen.blit(no_save_text, no_save_text_rect)
       self.screen.blit(dice_text, dice_text_rect)

       # Wurfwert anzeigen und zentrieren
       #dice_text_rect = dice_text.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
       #self.screen.blit(dice_text, dice_text_rect)

       pygame.display.flip()

       # Auf Spieleraktion warten
       choice = None
       while choice is None:
           for event in pygame.event.get():
               if event.type == pygame.QUIT:
                   pygame.quit()
                   exit()
               elif event.type == pygame.MOUSEBUTTONDOWN:
                   if save_button.collidepoint(event.pos):
                       choice = "s"  # Speichern
                   elif no_save_button.collidepoint(event.pos):
                       choice = "n"  # Spielen

       return choice

    def refresh_board(self):
       self.add_fields()
       self.show_pieces()
       self.show_next_move()
       pygame.display.flip()

