import sqlite3

class DiceStatistics:
    def __init__(self, db_name="game_stats.db", reset_db=False):
        print("Database: " + db_name)
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        if reset_db:
            self.reset_database()  # Tabelle zurücksetzen
        self._create_table()

    def reset_database(self):
        """Löscht alle Daten und setzt die Tabelle neu auf."""
        self.cursor.execute("DROP TABLE IF EXISTS dice_stats")
        self.conn.commit()

    def _create_table(self):
        """Erstellt die Tabelle für Würfelstatistiken."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dice_stats (
                player TEXT,
                dice_value INTEGER,
                count INTEGER DEFAULT 0,
                PRIMARY KEY (player, dice_value)
            )
        ''')
        self.conn.commit()

    def add_new_player(self, player_name):
        """Fügt einen neuen Spieler mit Einträgen für alle Würfelwerte (1-6) hinzu."""
        self.cursor.execute("SELECT COUNT(*) FROM dice_stats WHERE player = ?", (player_name,))
        if self.cursor.fetchone()[0] == 0:  # Nur hinzufügen, wenn Spieler nicht existiert
            for dice_value in range(1, 7):
                self.cursor.execute("INSERT INTO dice_stats (player, dice_value, count) VALUES (?, ?, 0)",
                                    (player_name, dice_value))
            self.conn.commit()

    def add_wurf(self, player, dice_value):
        """Erhöht den Zähler für eine gewürfelte Zahl des Spielers um +1."""
        self.cursor.execute('''
            UPDATE dice_stats SET count = count + 1 WHERE player = ? AND dice_value = ?
        ''', (player, dice_value))
        self.conn.commit()

    def decrease_wurf(self, player, dice_value):
        """Verringert den Zähler für eine geworfene Zahl des Spielers um -1."""
        self.cursor.execute('''
           UPDATE dice_stats SET count = count - 1 WHERE player = ? AND dice_value = ? AND count > 0
        ''', (player, dice_value))
        self.conn.commit()


    def get_statistics(self, player):
        """Gibt die Würfelstatistik für einen Spieler zurück."""
        self.cursor.execute('SELECT dice_value, count FROM dice_stats WHERE player = ?', (player,))
        return dict(self.cursor.fetchall())

    def close(self):
        self.conn.close()

