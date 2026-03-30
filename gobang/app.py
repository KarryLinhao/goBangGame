from __future__ import annotations

import sys

import pygame

from .assets import Assets, load_assets
from .constants import (
    BLACK,
    BOARD_BG_COLOR,
    BOARD_BG_RECT,
    BOARD_SIZE,
    CELL_SIZE,
    GAME,
    GRID_START,
    HOME,
    LINE_COLOR,
    MODE_SELECT,
    PIECE_OFFSET,
    PLAYER_SETUP,
    PVP,
    PVAI,
    RULES,
    STAR_POINTS,
    WHITE,
    WINDOW_SIZE,
)
from .logic import GameState, choose_ai_move, is_draw, is_winning_move, undo_steps_for_mode
from .ui import Button, InputBox, TextBlock


class GoBangApp:
    def __init__(self) -> None:
        pygame.init()
        self.audio_enabled = False
        self._init_audio()
        self.window = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("GoBang")
        self.clock = pygame.time.Clock()

        self.font_small = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_large = pygame.font.SysFont("Arial", 48, bold=True)
        self.assets: Assets = load_assets()
        self.enable_audio_by_default()
        self.page = HOME
        self.state = GameState()
        self.black_input = InputBox(pygame.Rect(300, 210, 220, 58), self.font_medium)
        self.white_input = InputBox(pygame.Rect(300, 390, 220, 58), self.font_medium)
        self.ai_name = "Computer"
        self.sound_button_rect = pygame.Rect(1020, 20, 40, 40)
        self.buttons: dict[str, Button] = {}
        self.show_draw_confirm = False
        self.match_scores = {"Black": 0, "White": 0}

    def _init_audio(self) -> None:
        try:
            pygame.mixer.init()
        except pygame.error:
            self.audio_enabled = False

    def run(self) -> None:
        while True:
            self.render()
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.handle_event(event)
            self.clock.tick(60)

    def enable_audio_by_default(self) -> None:
        if self.assets.click_sound is None:
            self.audio_enabled = False
            return
        self.assets.click_sound.play(loops=-1)
        self.audio_enabled = True

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.page == HOME:
            self.handle_home_event(event)
        elif self.page == MODE_SELECT:
            self.handle_mode_select_event(event)
        elif self.page == PLAYER_SETUP:
            self.handle_player_setup_event(event)
        elif self.page == GAME:
            self.handle_game_event(event)
        elif self.page == RULES:
            self.handle_rules_event(event)

    def handle_home_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        if self.sound_button_rect.collidepoint(event.pos):
            self.toggle_sound()
            return
        if self.buttons["start"].contains(event.pos):
            self.page = MODE_SELECT
        elif self.buttons["rules"].contains(event.pos):
            self.page = RULES

    def handle_mode_select_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        if self.buttons["pvp"].contains(event.pos):
            self.prepare_setup(PVP)
        elif self.buttons["pvai"].contains(event.pos):
            self.prepare_setup(PVAI)
        elif self.buttons["back"].contains(event.pos):
            self.page = HOME

    def handle_player_setup_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.black_input.handle_mouse(event.pos)
            if self.state.mode == PVP:
                self.white_input.handle_mouse(event.pos)
            else:
                self.white_input.active = False

            if self.buttons["back"].contains(event.pos):
                self.page = MODE_SELECT
                return
            if self.buttons["confirm"].contains(event.pos):
                self.start_game_from_inputs()
                return

        if event.type == pygame.KEYDOWN:
            self.black_input.handle_key(event)
            if self.state.mode == PVP:
                self.white_input.handle_key(event)

    def handle_game_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if self.show_draw_confirm:
            if self.buttons["draw_yes"].contains(event.pos):
                self.finish_current_game(draw=True)
                self.show_draw_confirm = False
            elif self.buttons["draw_no"].contains(event.pos):
                self.show_draw_confirm = False
            return

        if self.buttons["replay"].contains(event.pos):
            self.replay_current_game()
            return

        if self.buttons["undo"].contains(event.pos) and self.state.history:
            steps = undo_steps_for_mode(self.state.mode, len(self.state.history))
            for _ in range(steps):
                if not self.state.undo():
                    break
            return

        if self.buttons["draw"].contains(event.pos) and self.state.active:
            self.show_draw_confirm = True
            return

        if self.buttons["back"].contains(event.pos):
            self.show_draw_confirm = False
            self.page = HOME
            return

        grid_pos = self.mouse_to_board(event.pos)
        if grid_pos is None:
            return

        row, col = grid_pos
        if not self.state.place_move(row, col):
            return

        if is_winning_move(self.state.board, row, col):
            self.finish_current_game(draw=False)
            return
        if is_draw(self.state.board):
            self.finish_current_game(draw=True)
            return

        if self.state.mode == PVAI and self.state.active:
            self.play_ai_turn()

    def handle_rules_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and self.buttons["back"].contains(event.pos):
            self.page = HOME

    def prepare_setup(self, mode: str) -> None:
        self.state.mode = mode
        self.page = PLAYER_SETUP
        self.black_input.text = ""
        self.black_input.active = True
        self.white_input.text = "" if mode == PVP else self.ai_name
        self.white_input.active = False

    def start_game_from_inputs(self) -> None:
        black_name = self.black_input.text.strip() or "Black"
        if self.state.mode == PVP:
            white_name = self.white_input.text.strip() or "White"
        else:
            white_name = self.ai_name
        self.state.reset(self.state.mode, [black_name, white_name])
        self.match_scores = {black_name: 0, white_name: 0}
        self.show_draw_confirm = False
        self.page = GAME

    def play_ai_turn(self) -> None:
        move = choose_ai_move(self.state)
        if move is None:
            self.finish_current_game(draw=True)
            return
        row, col = move
        self.state.place_move(row, col)
        if is_winning_move(self.state.board, row, col):
            self.finish_current_game(draw=False)
        elif is_draw(self.state.board):
            self.finish_current_game(draw=True)

    def finish_current_game(self, draw: bool) -> None:
        if not draw:
            winner = self.state.players[0] if self.state.move_count % 2 == 1 else self.state.players[1]
            self.match_scores[winner] = self.match_scores.get(winner, 0) + 1
        self.state.finish(draw=draw)

    def replay_current_game(self) -> None:
        self.state.reset(self.state.mode, self.state.players.copy())
        self.show_draw_confirm = False

    def render(self) -> None:
        self.window.blit(self.assets.background, (0, 0))
        self.buttons = {}

        if self.page == HOME:
            self.render_home()
        elif self.page == MODE_SELECT:
            self.render_mode_select()
        elif self.page == PLAYER_SETUP:
            self.render_player_setup()
        elif self.page == GAME:
            self.render_game()
        elif self.page == RULES:
            self.render_rules()

    def render_home(self) -> None:
        current_sound_icon = self.assets.sound_icon if self.audio_enabled else self.assets.sound_off_icon
        self.window.blit(current_sound_icon, self.sound_button_rect.topleft)
        TextBlock("Go", (0, 0, 0), 180, (140, 95)).draw(self.window)
        TextBlock("Bang", (0, 0, 0), 180, (45, 280)).draw(self.window)
        TextBlock("Five in a row wins.", (20, 20, 20), 34, (90, 525)).draw(self.window)

        self.buttons["start"] = Button(
            pygame.Rect(635, 170, 300, 110), "Start Game", (255, 211, 155), (0, 0, 0), self.font_medium
        )
        self.buttons["rules"] = Button(
            pygame.Rect(635, 330, 300, 110), "Game Rules", (202, 225, 255), (0, 0, 0), self.font_medium
        )

        for button in self.buttons.values():
            button.draw(self.window)

        sound_status = "On" if self.audio_enabled else "Off"
        TextBlock(f"Sound: {sound_status}", (0, 0, 0), 26, (920, 70)).draw(self.window)

    def render_mode_select(self) -> None:
        TextBlock("Choose Mode", (0, 0, 0), 72, (320, 90)).draw(self.window)
        self.buttons["pvp"] = Button(
            pygame.Rect(410, 210, 300, 110), "Player vs Player", (255, 222, 173), (0, 0, 0), self.font_medium
        )
        self.buttons["pvai"] = Button(
            pygame.Rect(410, 370, 300, 110), "Player vs AI", (255, 222, 173), (0, 0, 0), self.font_medium
        )
        self.buttons["back"] = Button(
            pygame.Rect(830, 570, 180, 75), "Back", (255, 222, 173), (0, 0, 0), self.font_small
        )
        for button in self.buttons.values():
            button.draw(self.window)

    def render_player_setup(self) -> None:
        title = "Enter Player Names" if self.state.mode == PVP else "Enter Your Name"
        TextBlock(title, (0, 0, 0), 56, (80, 70)).draw(self.window)
        TextBlock("Black player:", (0, 0, 0), 32, (90, 220)).draw(self.window)
        black_hint = "Black moves first. Up to 8 characters."
        TextBlock(black_hint, (35, 35, 35), 22, (600, 220), bold=False).draw(self.window)
        self.black_input.draw(self.window)

        if self.state.mode == PVP:
            TextBlock("White player:", (0, 0, 0), 32, (90, 400)).draw(self.window)
            TextBlock("Choose any name you like.", (35, 35, 35), 22, (600, 400), bold=False).draw(self.window)
            self.white_input.draw(self.window)
        else:
            TextBlock(f"White player: {self.ai_name}", (0, 0, 0), 32, (90, 400)).draw(self.window)
            TextBlock("You will play black against the computer.", (35, 35, 35), 22, (600, 400), bold=False).draw(
                self.window
            )

        self.buttons["confirm"] = Button(
            pygame.Rect(650, 560, 220, 90), "Start", (255, 222, 173), (0, 0, 0), self.font_medium
        )
        self.buttons["back"] = Button(
            pygame.Rect(380, 560, 220, 90), "Back", (255, 222, 173), (0, 0, 0), self.font_medium
        )
        self.buttons["confirm"].draw(self.window)
        self.buttons["back"].draw(self.window)

    def render_game(self) -> None:
        self.draw_board()
        self.draw_pieces()
        self.draw_sidebar()

        self.buttons["replay"] = Button(
            pygame.Rect(805, 418, 190, 54), "Replay", (255, 222, 173), (0, 0, 0), self.font_small
        )
        self.buttons["undo"] = Button(
            pygame.Rect(805, 484, 190, 54), "Undo", (185, 211, 238), (0, 0, 0), self.font_small
        )
        self.buttons["draw"] = Button(
            pygame.Rect(805, 550, 190, 54), "Draw", (143, 188, 143), (0, 0, 0), self.font_small
        )
        self.buttons["back"] = Button(
            pygame.Rect(805, 616, 190, 54), "Back", (255, 222, 173), (0, 0, 0), self.font_small
        )

        for button in self.buttons.values():
            button.draw(self.window)

        if self.state.result_message:
            self.draw_result_banner()

        if self.show_draw_confirm:
            self.draw_draw_confirmation()

    def render_rules(self) -> None:
        TextBlock("Game Rules", (0, 0, 0), 86, (230, 70)).draw(self.window)
        rules = (
            "Players take turns placing stones on empty intersections.\n"
            "Black always moves first.\n"
            "Make five connected stones in a row to win.\n"
            "Lines can be horizontal, vertical, or diagonal.\n"
            "If the board fills up without a winner, the game is a draw."
        )
        TextBlock(rules, (0, 0, 0), 34, (110, 220), bold=False).draw(self.window)
        self.buttons["back"] = Button(
            pygame.Rect(830, 610, 180, 75), "Back", (255, 222, 173), (0, 0, 0), self.font_small
        )
        self.buttons["back"].draw(self.window)

    def draw_board(self) -> None:
        pygame.draw.rect(self.window, BOARD_BG_COLOR, BOARD_BG_RECT)
        end = GRID_START + CELL_SIZE * (BOARD_SIZE - 1)
        for offset in range(BOARD_SIZE):
            position = GRID_START + offset * CELL_SIZE
            pygame.draw.line(self.window, LINE_COLOR, (GRID_START, position), (end, position), 3)
            pygame.draw.line(self.window, LINE_COLOR, (position, GRID_START), (position, end), 3)
        for point in STAR_POINTS:
            pygame.draw.circle(self.window, LINE_COLOR, point, 5)

    def draw_pieces(self) -> None:
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.state.board[row][col]
                if piece == BLACK:
                    image = self.assets.black_piece
                elif piece == WHITE:
                    image = self.assets.white_piece
                else:
                    continue
                x = PIECE_OFFSET + col * CELL_SIZE
                y = PIECE_OFFSET + row * CELL_SIZE
                self.window.blit(image, (x, y))

    def draw_sidebar(self) -> None:
        panel_rect = pygame.Rect(735, 45, 335, 635)
        pygame.draw.rect(self.window, (255, 255, 255), panel_rect, border_radius=28)
        pygame.draw.rect(self.window, (225, 225, 225), panel_rect, 2, border_radius=28)
        panel_center_x = panel_rect.centerx
        left_x = panel_rect.left + 72
        right_x = panel_rect.right - 72

        turn_name = self.state.players[0] if self.state.current_piece == BLACK else self.state.players[1]
        player_left = self.font_medium.render(self.state.players[0], True, (65, 105, 225))
        player_right = self.font_medium.render(self.state.players[1], True, (65, 105, 225))
        vs_label = pygame.font.SysFont("Arial", 30, bold=True).render("VS", True, (0, 0, 0))
        score_left = self.font_medium.render(str(self.match_scores.get(self.state.players[0], 0)), True, (40, 40, 40))
        score_right = self.font_medium.render(str(self.match_scores.get(self.state.players[1], 0)), True, (40, 40, 40))
        score_vs = pygame.font.SysFont("Arial", 24, bold=True).render("VS", True, (90, 90, 90))
        self.window.blit(player_left, player_left.get_rect(center=(left_x, 118)))
        self.window.blit(vs_label, vs_label.get_rect(center=(panel_center_x, 118)))
        self.window.blit(player_right, player_right.get_rect(center=(right_x, 118)))
        self.window.blit(score_left, score_left.get_rect(center=(left_x, 168)))
        self.window.blit(score_vs, score_vs.get_rect(center=(panel_center_x, 168)))
        self.window.blit(score_right, score_right.get_rect(center=(right_x, 168)))

        status_title = "Game Status"
        status_detail = "Game finished" if not self.state.active else f"Turn: {turn_name}"
        status_title_surface = pygame.font.SysFont("Arial", 20, bold=False).render(status_title, True, (70, 70, 70))
        status_detail_surface = pygame.font.SysFont("Arial", 22, bold=True).render(status_detail, True, (0, 0, 0))
        self.window.blit(status_title_surface, status_title_surface.get_rect(center=(panel_center_x, 238)))
        self.window.blit(status_detail_surface, status_detail_surface.get_rect(center=(panel_center_x, 272)))

    def draw_result_banner(self) -> None:
        banner_rect = pygame.Rect(780, 298, 245, 66)
        pygame.draw.rect(self.window, (255, 244, 238), banner_rect, border_radius=24)
        pygame.draw.rect(self.window, (235, 120, 90), banner_rect, 2, border_radius=24)
        result_font = pygame.font.SysFont("Arial", 26, bold=True)
        result = result_font.render(self.state.result_message, True, (200, 20, 20))
        self.window.blit(result, result.get_rect(center=banner_rect.center))

    def draw_draw_confirmation(self) -> None:
        overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 110))
        self.window.blit(overlay, (0, 0))

        popup_rect = pygame.Rect(305, 190, 490, 235)
        pygame.draw.rect(self.window, (255, 255, 255), popup_rect, border_radius=22)
        pygame.draw.rect(self.window, (210, 210, 210), popup_rect, 2, border_radius=22)
        popup_center_x = popup_rect.centerx
        title_surface = pygame.font.SysFont("Arial", 42, bold=True).render("Offer a draw?", True, (0, 0, 0))
        subtitle_surface = pygame.font.SysFont("Arial", 22, bold=False).render(
            "Do you want to end this game as a draw?", True, (60, 60, 60)
        )
        self.window.blit(title_surface, title_surface.get_rect(center=(popup_center_x, 245)))
        self.window.blit(subtitle_surface, subtitle_surface.get_rect(center=(popup_center_x, 305)))

        button_width = 145
        button_height = 58
        button_gap = 50
        left_x = popup_center_x - button_gap // 2 - button_width
        right_x = popup_center_x + button_gap // 2
        self.buttons["draw_yes"] = Button(
            pygame.Rect(left_x, 340, button_width, button_height), "Yes", (180, 220, 180), (0, 0, 0), self.font_medium
        )
        self.buttons["draw_no"] = Button(
            pygame.Rect(right_x, 340, button_width, button_height), "No", (245, 215, 160), (0, 0, 0), self.font_medium
        )
        self.buttons["draw_yes"].draw(self.window)
        self.buttons["draw_no"].draw(self.window)

    def mouse_to_board(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        x, y = pos
        min_pos = GRID_START - CELL_SIZE // 2
        max_pos = GRID_START + CELL_SIZE * (BOARD_SIZE - 1) + CELL_SIZE // 2
        if not (min_pos <= x <= max_pos and min_pos <= y <= max_pos):
            return None
        col = round((x - GRID_START) / CELL_SIZE)
        row = round((y - GRID_START) / CELL_SIZE)
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return None
        return row, col

    def toggle_sound(self) -> None:
        if self.assets.click_sound is None:
            self.audio_enabled = False
            return
        if self.audio_enabled:
            self.assets.click_sound.stop()
            self.audio_enabled = False
        else:
            self.assets.click_sound.play(loops=-1)
            self.audio_enabled = True


def run() -> None:
    GoBangApp().run()
