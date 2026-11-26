import os
from forge import Forge

try:
    from game import Game
except ImportError:
    print("Game script does not exists!")
    raise SystemExit(1)


if __name__ == "__main__":
    forge = Forge(Game)
    forge.run()
