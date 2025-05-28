def clear():
    """
    Clear screen
    """
    print(end="\033[2J")

def home():
    """
    Move cursor to the top left corner of the terminal.
    """
    print(end="\033[H")
