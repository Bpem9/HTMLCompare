from enum import Enum


class ResponseEnum(Enum):
    NO_URI = 'This URI is unavailable. Possibly redirecting or proxy failure'
    NO_GAME_TITLE = 'The game page has no GAME_TITLE, or the GAME_TITLE has different className of the HTMLElement'
    NO_RETURN_BUTTON = 'The game page has no RETURN_BUTTON, or the RETURN_BUTTON has different className of the HTMLElement'
    NO_PLAY_BUTTON = 'The game page has no PLAY_FREE button, or the PLAY_FREE button has different className of the HTMLElement'
    OK = 'Ok'