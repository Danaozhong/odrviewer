"""This file contains helper functions for arrays."""

import numpy as np
from scipy.interpolate import interp1d


def fix_zero_directions(dirs: np.ndarray) -> np.ndarray:
    """Fix any zero rows by filling with adjacent elements.

    Cycles through the array replacing any zero rows by
    non-zero adjacent rows if they are there. Stops
    when all rows are non-zero. If all elements are zero
    then a ValueError is raised.
    """
    dirs = dirs.copy()
    n = dirs.shape[0]
    if (dirs == 0).all(1).sum() == 0:
        return dirs
    if (dirs == 0).all(1).sum() == n:
        raise ValueError("All elements are zero.")
    for _ in range(1, n - 1):  # will run in at most n - 1
        for i in range(1, n - 1):
            if (dirs[i] == 0).all():
                if not (dirs[i - 1] == 0).all():
                    dirs[i] = dirs[i - 1]
                elif not (dirs[i + 1] == 0).all():
                    dirs[i] = dirs[i + 1]
        if (dirs[1:-1] == 0).all(1).sum() == 0:
            break
        for i in reversed(range(1, n - 1)):
            if (dirs[i] == 0).all():
                if not (dirs[i - 1] == 0).all():
                    dirs[i] = dirs[i - 1]
                elif not (dirs[i + 1] == 0).all():
                    dirs[i] = dirs[i + 1]
        if (dirs[1:-1] == 0).all(1).sum() == 0:
            break
    if (dirs[0] == 0).all():
        dirs[0] = dirs[1]
    if (dirs[-1] == 0).all():
        dirs[-1] = dirs[-2]
    return dirs


def interpolate_path(path_vertices: np.ndarray, resolution: float = 0.1) -> np.ndarray:
    """Interpolate a path at the given resolution."""
    # Remove duplicated points
    _, idxs = np.unique(path_vertices, axis=0, return_index=True)
    path_vertices = path_vertices[sorted(idxs)]
    ss = np.hstack([[0.0], np.linalg.norm(np.diff(path_vertices, axis=0), axis=1).cumsum()])
    interp_func = interp1d(
        ss,
        path_vertices,
        axis=0,
        fill_value="extrapolate",
    )

    new_distance = np.arange(0, ss[-1], resolution)
    if len(new_distance) < 2:
        new_distance = np.array([0.0, ss[-1]])
    return interp_func(new_distance)
