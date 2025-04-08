# Man, don't be annoyed!

Implementation of the German game "Mensch ärger dich nicht", similar to the english game Ludo.

![image](https://github.com/user-attachments/assets/cd7fdd22-d5f3-46fc-be18-34d09236e07f)


# Rules
- Need a 6 to leave home
- After a 6 you can go again (if there was a possible move)
- If possible piece on own first field must be moved
- If you land on same field as an opponent piece, it gets send home
- Can't send your own pieces home
- Winner is who first fills hist 4 goal fields

# Store Option
An additional option to save a roll and use it later.

- After each roll, you will be asked whether you want to play or save the roll
- Play: the roll is used normally
- Save: the rolled number is saved for the player, and the current turn ends
- A roll can only be saved if it would be possible to play it
- To use a saved number, it must be selected before rolling
- A selected number is used in the same way as a rolled number

# Run
python dontbeannoyed.py

# Why?
This implementation has modified store rules that I created im my childhood.
For this modification I just wanted a digital version, to play it easier.
