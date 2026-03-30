from __future__ import annotations

from dataclasses import dataclass, field

from .constants import BLACK, BOARD_SIZE, EMPTY, PVP, PVAI, WHITE


Board = list[list[int]]
Move = tuple[int, int]


@dataclass
class GameState:
    mode: str = PVP
    players: list[str] = field(default_factory=lambda: ["Black", "White"])
    board: Board = field(default_factory=lambda: [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)])
    history: list[Move] = field(default_factory=list)
    active: bool = True
    result_message: str = ""

    def reset(self, mode: str, players: list[str]) -> None:
        self.mode = mode
        self.players = players
        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.history = []
        self.active = True
        self.result_message = ""

    @property
    def move_count(self) -> int:
        return len(self.history)

    @property
    def current_piece(self) -> int:
        return BLACK if self.move_count % 2 == 0 else WHITE

    def place_move(self, row: int, col: int) -> bool:
        if not self.active:
            return False
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return False
        if self.board[row][col] != EMPTY:
            return False

        self.board[row][col] = self.current_piece
        self.history.append((row, col))
        return True

    def undo(self) -> bool:
        if not self.history:
            return False
        row, col = self.history.pop()
        self.board[row][col] = EMPTY
        self.active = True
        self.result_message = ""
        return True

    def finish(self, draw: bool = False) -> None:
        self.active = False
        if draw:
            self.result_message = "Draw!"
            return
        winner_name = self.players[0] if self.move_count % 2 == 1 else self.players[1]
        self.result_message = f"{winner_name} wins!"


def count_direction(board: Board, row: int, col: int, dr: int, dc: int, piece: int) -> int:
    total = 1
    for direction in (1, -1):
        r = row + dr * direction
        c = col + dc * direction
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == piece:
            total += 1
            r += dr * direction
            c += dc * direction
    return total


def is_winning_move(board: Board, row: int, col: int) -> bool:
    piece = board[row][col]
    if piece == EMPTY:
        return False
    directions = ((1, 0), (0, 1), (1, 1), (1, -1))
    return any(count_direction(board, row, col, dr, dc, piece) >= 5 for dr, dc in directions)


def is_draw(board: Board) -> bool:
    return all(cell != EMPTY for row in board for cell in row)


def line_info(board: Board, row: int, col: int, dr: int, dc: int, piece: int) -> tuple[int, int]:
    stones = 1
    open_ends = 0

    for direction in (1, -1):
        r = row + dr * direction
        c = col + dc * direction
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == piece:
            stones += 1
            r += dr * direction
            c += dc * direction

        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == EMPTY:
            open_ends += 1

    return stones, open_ends


def line_score(stones: int, open_ends: int) -> int:
    if stones >= 5:
        return 1_000_000
    if stones == 4 and open_ends == 2:
        return 100_000
    if stones == 4 and open_ends == 1:
        return 15_000
    if stones == 3 and open_ends == 2:
        return 8_000
    if stones == 3 and open_ends == 1:
        return 1_200
    if stones == 2 and open_ends == 2:
        return 500
    if stones == 2 and open_ends == 1:
        return 120
    if stones == 1 and open_ends == 2:
        return 30
    return 0


def evaluate_move(board: Board, row: int, col: int, piece: int) -> int:
    directions = ((1, 0), (0, 1), (1, 1), (1, -1))
    score = 0

    for dr, dc in directions:
        stones, open_ends = line_info(board, row, col, dr, dc, piece)
        score += line_score(stones, open_ends)

    center = BOARD_SIZE // 2
    score += max(0, 14 - (abs(row - center) + abs(col - center))) * 8
    return score


def generate_candidate_moves(board: Board) -> list[Move]:
    occupied = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] != EMPTY]
    if not occupied:
        center = BOARD_SIZE // 2
        return [(center, center)]

    candidates: set[Move] = set()
    for row, col in occupied:
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                nr = row + dr
                nc = col + dc
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == EMPTY:
                    candidates.add((nr, nc))

    return sorted(candidates)


def would_create_multiple_wins(board: Board, row: int, col: int, piece: int) -> bool:
    winning_lines = 0
    for dr, dc in ((1, 0), (0, 1), (1, 1), (1, -1)):
        stones, _ = line_info(board, row, col, dr, dc, piece)
        if stones >= 5:
            winning_lines += 1
    return winning_lines >= 2


def choose_ai_move(state: GameState) -> Move | None:
    candidates = generate_candidate_moves(state.board)
    if not candidates:
        return None

    best_move: Move | None = None
    best_score = float("-inf")

    for row, col in candidates:
        state.board[row][col] = WHITE
        if is_winning_move(state.board, row, col):
            state.board[row][col] = EMPTY
            return row, col
        white_score = evaluate_move(state.board, row, col, WHITE)
        white_fork_bonus = 50_000 if would_create_multiple_wins(state.board, row, col, WHITE) else 0
        state.board[row][col] = EMPTY

        state.board[row][col] = BLACK
        black_wins = is_winning_move(state.board, row, col)
        black_score = evaluate_move(state.board, row, col, BLACK)
        black_fork_bonus = 60_000 if would_create_multiple_wins(state.board, row, col, BLACK) else 0
        state.board[row][col] = EMPTY

        score = white_score + white_fork_bonus + int(black_score * 0.9) + black_fork_bonus
        if black_wins:
            score += 200_000

        if best_move is None or score > best_score:
            best_move = (row, col)
            best_score = score

    return best_move


def undo_steps_for_mode(mode: str, history_length: int) -> int:
    if mode == PVAI and history_length >= 2:
        return 2
    return 1
