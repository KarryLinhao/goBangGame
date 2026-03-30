from dataclasses import dataclass

import pygame


@dataclass
class Button:
    rect: pygame.Rect
    text: str
    bg_color: tuple[int, int, int]
    text_color: tuple[int, int, int]
    font: pygame.font.Font
    border_radius: int = 24

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        label = self.font.render(self.text, True, self.text_color)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

    def contains(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


class InputBox:
    def __init__(self, rect: pygame.Rect, font: pygame.font.Font, max_length: int = 8) -> None:
        self.rect = rect
        self.font = font
        self.max_length = max_length
        self.text = ""
        self.active = False
        self.color_inactive = pygame.Color(211, 211, 211)
        self.color_active = pygame.Color(65, 105, 225)

    def handle_mouse(self, pos: tuple[int, int]) -> None:
        self.active = self.rect.collidepoint(pos)

    def handle_key(self, event: pygame.event.Event) -> None:
        if not self.active:
            return
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
            return
        if len(self.text) >= self.max_length:
            return
        if event.unicode.isprintable() and not event.unicode.isspace():
            self.text += event.unicode

    def draw(self, surface: pygame.Surface) -> None:
        color = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=8)
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=8)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        surface.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))
        if self.active and (pygame.time.get_ticks() // 500) % 2 == 0:
            caret_x = self.rect.x + 14 + text_surface.get_width()
            caret_top = self.rect.y + 11
            caret_bottom = self.rect.y + self.rect.height - 11
            pygame.draw.line(surface, (0, 0, 0), (caret_x, caret_top), (caret_x, caret_bottom), 2)


class TextBlock:
    def __init__(
        self,
        text: str,
        color: tuple[int, int, int],
        font_size: int,
        position: tuple[int, int],
        bold: bool = True,
    ) -> None:
        self.text = text
        self.color = color
        self.position = position
        self.font_size = font_size
        self.font = pygame.font.SysFont("Arial", font_size, bold=bold)

    def draw(self, surface: pygame.Surface) -> None:
        for index, line in enumerate(self.text.splitlines()):
            rendered = self.font.render(line, True, self.color)
            top_left = (self.position[0], self.position[1] + index * self.font_size)
            surface.blit(rendered, top_left)
