"""Unit tests for OpenDRIVE spiral geometry behavior."""

import numpy as np

from odrviewer.pyxodr.geometries.spiral import Spiral


class _RecordingStandardSpiral:
    """Simple stand-in that records queried s values."""

    def __init__(self):
        self.calls = []

    def __call__(self, s: float):
        self.calls.append(s)
        return (s, 0.0, 0.0)


def test_spiral_uses_absolute_arc_length_samples_in_meters():
    """Regression test for accidental double scaling of spiral length."""
    spiral = Spiral(
        curv_start=0.1,
        curv_end=0.3,
        x_offset=0.0,
        y_offset=0.0,
        heading_offset=0.0,
        length=10.0,
    )

    recorder = _RecordingStandardSpiral()
    spiral.standard_spiral = recorder

    p_array = np.array([0.0, 2.5, 10.0])
    spiral(p_array)

    s_offset = spiral.curvStart / spiral.curvature_rate_of_change
    expected_s = p_array + s_offset

    assert np.allclose(np.array(recorder.calls), expected_s)
