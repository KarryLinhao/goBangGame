from dataclasses import dataclass
from pathlib import Path

import pygame

from .constants import ASSETS_DIR, PIECE_SIZE


@dataclass
class Assets:
    background: pygame.Surface
    black_piece: pygame.Surface
    white_piece: pygame.Surface
    sound_icon: pygame.Surface
    sound_off_icon: pygame.Surface
    click_sound: pygame.mixer.Sound | None


def load_scaled_image(path: Path, size: tuple[int, int] | None = None) -> pygame.Surface:
    image = pygame.image.load(str(path)).convert_alpha()
    if size is not None:
        return pygame.transform.smoothscale(image, size)
    return image


def build_sound_off_icon(sound_icon: pygame.Surface) -> pygame.Surface:
    muted = sound_icon.copy()
    width, height = muted.get_size()
    pygame.draw.line(muted, (215, 45, 45), (6, height - 6), (width - 6, 6), 5)
    return muted


def load_assets() -> Assets:
    background = load_scaled_image(ASSETS_DIR / "background.jpg", (1100, 700))
    black_piece = load_scaled_image(ASSETS_DIR / "black.png", (PIECE_SIZE, PIECE_SIZE))
    white_piece = load_scaled_image(ASSETS_DIR / "white.png", (PIECE_SIZE, PIECE_SIZE))
    sound_icon = load_scaled_image(ASSETS_DIR / "sound.png", (40, 40))
    sound_off_icon = build_sound_off_icon(sound_icon)

    click_sound = None
    audio_path = ASSETS_DIR / "bgm.mp3"
    if pygame.mixer.get_init() and audio_path.exists():
        try:
            click_sound = pygame.mixer.Sound(str(audio_path))
        except pygame.error:
            click_sound = None

    return Assets(
        background=background,
        black_piece=black_piece,
        white_piece=white_piece,
        sound_icon=sound_icon,
        sound_off_icon=sound_off_icon,
        click_sound=click_sound,
    )
