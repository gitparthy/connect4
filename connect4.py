import math
import sys

# ─── Board constants ───────────────────────────────────────────────
ROWS = 6
COLS = 7
EMPTY = 0
PLAYER = 1
AI = 2
WINDOW = 4

# ─── Board helpers ─────────────────────────────────────────────────
def create_board():
    return [[EMPTY]*COLS for _ in range(ROWS)]

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid(board, col):
    return 0 <= col < COLS and board[0][col] == EMPTY

def get_next_row(board, col):
    for r in range(ROWS-1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return -1

def get_valid_cols(board):
    return [c for c in range(COLS) if is_valid(board, c)]

# ─── Win detection ─────────────────────────────────────────────────
def winning_move(board, piece):
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS-3):
            if all(board[r][c+i] == piece for i in range(4)):
                return True
    # Vertical
    for r in range(ROWS-3):
        for c in range(COLS):
            if all(board[r+i][c] == piece for i in range(4)):
                return True
    # Diagonal /
    for r in range(3, ROWS):
        for c in range(COLS-3):
            if all(board[r-i][c+i] == piece for i in range(4)):
                return True
    # Diagonal \
    for r in range(ROWS-3):
        for c in range(COLS-3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True
    return False

def is_terminal(board):
    return (winning_move(board, PLAYER) or
            winning_move(board, AI) or
            len(get_valid_cols(board)) == 0)

# ─── Scoring ───────────────────────────────────────────────────────
def score_window(window, piece):
    opp = PLAYER if piece == AI else AI
    score = 0
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    if window.count(opp) == 3 and window.count(EMPTY) == 1:
        score -= 4
    return score

def score_board(board, piece):
    score = 0
    # Centre column bonus
    centre = [board[r][COLS//2] for r in range(ROWS)]
    score += centre.count(piece) * 3
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS-3):
            w = [board[r][c+i] for i in range(4)]
            score += score_window(w, piece)
    # Vertical
    for c in range(COLS):
        for r in range(ROWS-3):
            w = [board[r+i][c] for i in range(4)]
            score += score_window(w, piece)
    # Diagonal /
    for r in range(3, ROWS):
        for c in range(COLS-3):
            w = [board[r-i][c+i] for i in range(4)]
            score += score_window(w, piece)
    # Diagonal \
    for r in range(ROWS-3):
        for c in range(COLS-3):
            w = [board[r+i][c+i] for i in range(4)]
            score += score_window(w, piece)
    return score

# ─── Minimax with alpha-beta pruning ───────────────────────────────
def minimax(board, depth, alpha, beta, maximising):
    valid = get_valid_cols(board)
    terminal = is_terminal(board)

    if terminal:
        if winning_move(board, AI):
            return (None, 1_000_000 + depth)
        elif winning_move(board, PLAYER):
            return (None, -1_000_000 - depth)
        else:
            return (None, 0)
    if depth == 0:
        return (None, score_board(board, AI))

    if maximising:
        best = (valid[0], -math.inf)
        for col in valid:
            row = get_next_row(board, col)
            board[row][col] = AI
            _, sc = minimax(board, depth-1, alpha, beta, False)
            board[row][col] = EMPTY
            if sc > best[1]:
                best = (col, sc)
            alpha = max(alpha, sc)
            if alpha >= beta:
                break
        return best
    else:
        best = (valid[0], math.inf)
        for col in valid:
            row = get_next_row(board, col)
            board[row][col] = PLAYER
            _, sc = minimax(board, depth-1, alpha, beta, True)
            board[row][col] = EMPTY
            if sc < best[1]:
                best = (col, sc)
            beta = min(beta, sc)
            if alpha >= beta:
                break
        return best

AI_DEPTH = 4   # increase for harder AI (slower)

# ─── Display ───────────────────────────────────────────────────────
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

SYMBOLS = {EMPTY: "·", PLAYER: f"{RED}●{RESET}", AI: f"{YELLOW}●{RESET}"}

def print_board(board):
    print()
    print(BOLD + "  " + "  ".join(str(c+1) for c in range(COLS)) + RESET)
    print("  " + "─" * (COLS*3 - 1))
    for row in board:
        print("| " + "  ".join(SYMBOLS[cell] for cell in row) + "  |")
    print("  " + "─" * (COLS*3 - 1))
    print()

# ─── Main game loop ────────────────────────────────────────────────
def main():
    board = create_board()
    game_over = False
    turn = PLAYER   # player goes first

    print(BOLD + "\n╔══════════════════════════════╗")
    print(       "║      CONNECT 4 — vs AI       ║")
    print(       "╚══════════════════════════════╝" + RESET)
    print(f"  You: {RED}●{RESET}   AI: {YELLOW}●{RESET}")
    print("  Enter a column number (1-7) to drop your piece.\n")

    print_board(board)

    while not game_over:
        if turn == PLAYER:
            while True:
                try:
                    raw = input(f"  {RED}Your move{RESET} (col 1-7): ").strip()
                    col = int(raw) - 1
                    if is_valid(board, col):
                        break
                    print("  ⚠  Column is full or invalid. Try again.")
                except (ValueError, EOFError):
                    print("  ⚠  Please enter a number between 1 and 7.")

            row = get_next_row(board, col)
            drop_piece(board, row, col, PLAYER)
            print_board(board)

            if winning_move(board, PLAYER):
                print(BOLD + RED + "  🎉  You win! Well played!\n" + RESET)
                game_over = True
        else:
            print(f"  {YELLOW}AI is thinking...{RESET}")
            col, _ = minimax(board, AI_DEPTH, -math.inf, math.inf, True)
            row = get_next_row(board, col)
            drop_piece(board, row, col, AI)
            print(f"  AI dropped in column {col+1}")
            print_board(board)

            if winning_move(board, AI):
                print(BOLD + YELLOW + "  🤖  AI wins! Better luck next time.\n" + RESET)
                game_over = True

        if not game_over and len(get_valid_cols(board)) == 0:
            print(BOLD + "  🤝  It's a draw!\n" + RESET)
            game_over = True

        turn = AI if turn == PLAYER else PLAYER

    play_again = input("  Play again? (y/n): ").strip().lower()
    if play_again == "y":
        main()
    else:
        print("\n  Thanks for playing! Goodbye.\n")

if __name__ == "__main__":
    main()
