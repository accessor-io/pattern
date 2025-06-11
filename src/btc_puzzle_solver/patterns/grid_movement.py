from typing import Tuple

class GridNavigator:
    def __init__(self):
        self.position = (0, 0)
        self.movement_pattern = [4,5,4,4,5,4,5,4]  # → ↓ → → ↓ → ↓ →
        
    def move(self, step: int) -> Tuple[int, int]:
        move_type = self.movement_pattern[step % len(self.movement_pattern)]
        if move_type == 4:  # Right
            self.position = (self.position[0] + 1, self.position[1])
        else:  # Down
            self.position = (self.position[0], self.position[1] + 1)
        return self.position 