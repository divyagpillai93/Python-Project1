


def display_board(board):
    """Show the current 3 by 3 game board."""
    # print()
    for row in range(3):
        start = row * 3
        print(" " + " | ".join(board[start:start + 3]))
        if row < 2:
            print(" ")
    print()


def check_winner(board, symbol):
    """Return True if the symbol completes a winning line."""
    winning_lines = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    for a, b, c in winning_lines:
        if board[a] == board[b] == board[c] == symbol:
            return True
    return False


def get_move(board, player, symbol):
    """Ask for a valid empty position, retrying when necessary."""
    while True:
        entry = input(f"Player {player} ({symbol}), enter position (1-9): ").strip()
        if not entry:
            print("Please enter a position. Empty input is not allowed.")
            continue
        try:
            position = int(entry)
        except ValueError:
            print("Invalid input! Enter a whole number from 1 to 9.")
            continue
        if position < 1 or position > 9:
            print("Position must be between 1 and 9.")
        elif board[position - 1] in ("X", "O"):
            print("That position is already occupied. Choose another.")
        else:
            return position - 1


def play_game():
    """Run one round of Tic-Tac-Toe."""
    board = [str(number) for number in range(1, 10)]
    player = 1
    symbol = "X"
    print("\nNew game! Player 1 = X, Player 2 = O")
    display_board(board)

    while True:
        position = get_move(board, player, symbol)
        board[position] = symbol
        display_board(board)

        if check_winner(board, symbol):
            print(f"Congratulations! Player {player} ({symbol}) wins!")
            break
        if all(cell in ("X", "O") for cell in board):
            print("It's a draw! All nine positions are filled.")
            break

        if player == 1:
            player, symbol = 2, "O"
        else:
            player, symbol = 1, "X"


def main():
    """Run games until the players choose to stop."""
    print("WELCOME TO TIC-TAC-TOE")
    while True:
        play_game()
        while True:
            answer = input("Play again? (yes/no): ").strip().lower()
            if answer in ("yes", "y", "no", "n"):
                break
            print("Please type yes or no.")
        if answer in ("no", "n"):
            print("Thanks for playing Tic-Tac-Toe. Goodbye!")
            break


if __name__ == "__main__":
    main()



