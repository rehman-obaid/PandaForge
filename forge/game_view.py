from enum import Enum
from dataclasses import dataclass


GameViewDefaultSize = 0.3


class GameViewStyle(Enum):
    BOTTOM_LEFT = 1
    BOTTOM_RIGHT = 2
    TOP_LEFT = 3
    TOP_RIGHT = 4
    CENTER = 0


@dataclass
class GameViewSettings:
    size: float = GameViewDefaultSize
    style: GameViewStyle = GameViewStyle.BOTTOM_LEFT
