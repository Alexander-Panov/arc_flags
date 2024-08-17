from dataclasses import dataclass

import numpy as np


@dataclass
class GraphGUI:
    pos: np.ndarray  # positions
    adj: np.ndarray  # adjacency
    points_colors: list[tuple[int, int, int] | str]
    symbols: list[str]
    text: list[str]
