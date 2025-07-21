"""Functions to process OpenDRIVE cubic polynomials geometries."""

from typing import Optional

import numpy as np
from odrviewer.pyxodr.geometries.base import Geometry, GeometryType
from scipy.integrate import solve_ivp


class CubicPolynom(Geometry):
    r"""Class representing the Cubic polynomial from the OpenDRIVE spec (depreciated).

    $$y(x) = a + b*x + c*x2 + d*x^3$$

    Parameters
    ----------
    a : float
        a parameter in the interpolation equation.
    b : float
        b parameter in the interpolation equation.
    c : float
        c parameter in the interpolation equation.
    d : float
        d parameter in the interpolation equation.
    length : float, optional
        Length of the cubic polynomial line, by default None (in which case the call
        method of this class will be unusable)
    """

    def __init__(
        self,
        a: float,
        b: float,
        c: float,
        d: float,
        x_offset: float = 0.0,
        y_offset: float = 0.0,
        heading_offset: float = 0.0,
        length: Optional[float] = None,
    ):
        """Creates a cubic polynomial OpenDRIVE geometry object."""
        Geometry.__init__(self, GeometryType.CUBIC_POLYNOM, x_offset, y_offset, heading_offset, length)
        self.a, self.b, self.c, self.d = a, b, c, d

    def __call__(self, p_array: np.ndarray) -> np.ndarray:
        r"""Return local (p, v) coordinates from an array of parameter $p \in [0.0, 1.0]$.

        (p, v) coordinates are in their own x,y frame: start at origin, and initial
        heading is along the x axis.

        Parameters
        ----------
        p_array : np.ndarray
            p values $\in [0.0, 1.0]$ to compute parametric coordinates.

        Returns:
        -------
        np.ndarray
            Array of local (p, v) coordinate pairs.
        """
        u_array = self._u_array_from_arc_lengths(p_array)
        local_coords = self.u_v_from_u(u_array)
        return local_coords

    def _du_ds_differential_equation(self, _: float, y: np.ndarray) -> np.ndarray:
        r"""Differential equation for use in the solving of u from s.

        Solves the equation
        $$\frac{du}{ds} = \frac{1}{\sqrt{1 + \left ( \frac{dv}{du} \right ) }}$$
        Where for this class
        $$v(u) = a + bu + cu^2 + du^3$$

        Parameters
        ----------
        _ : float
            Present to fit the function signature required by scipy's solve_ivp
        y : np.ndarray
            Array of K 1D y values, [1, K]. Note y here refers to the
            scipy.integrate.solve_ivp spec; for our use case, y == u.

        Returns:
        -------
        np.ndarray
            Array of dy /dt (for our purposes, du / ds) values, [1, K]
        """
        y = y.T.squeeze()
        dv_du = np.ones_like(y) * self.b + 2 * self.c * y + 3 * self.d * np.power(y, 2)
        result = np.power(np.ones_like(y) + np.power(dv_du, 2), -0.5)
        return result.T

    def _u_array_from_arc_lengths(self, s_array: np.ndarray) -> np.ndarray:
        r"""Return an array of u (local coord) from s (distance along geometry).

        Required as OpenDRIVE provides a length value for road reference lines (i.e.
        a max s value) but the cubic polynomial geometry is parameterised by u (see
        7.6.2). Converting between them is done here by solving the initial value
        problem of the equation
        $$\frac{du}{ds} = \frac{1}{\sqrt{1 + \left ( \frac{dv}{du} \right ) }}$$
        with
        $$s_0 = 0$$
        $$u(s_0) = 0$$
        This seems convoluted so it's possible I've misunderstood the spec here;
        please raise an issue if so.

        Parameters
        ----------
        s_array : np.ndarray
            Array of distances along the polynomial curve.

        Returns:
        -------
        np.ndarray
            Array of u values corresponding to these distances.
        """
        if min(s_array) != 0.0:
            raise ValueError(f"s_array contains negative values: {s_array}")
        solution = solve_ivp(
            self._du_ds_differential_equation,
            (0.0, max(s_array)),
            np.array([0.0]),
            t_eval=s_array,
            vectorized=True,
        )
        if not (s_array == solution.t).all():
            raise RuntimeError("failed to solve the differential equation")
        u_array = solution.y.squeeze()
        return u_array

    def u_v_from_p(self, p_array: np.ndarray) -> np.ndarray:
        r"""Return local (p, v) coordinates from an array of parameter $p \in [0.0, 1.0]$.

        (p, v) coordinates are in their own x,y frame: start at origin, and initial
        heading is along the x axis.

        Parameters
        ----------
        p_array : np.ndarray
            p values $\in [0.0, 1.0]$ to compute parametric coordinates.

        Returns:
        -------
        np.ndarray
            Array of local (p, v) coordinate pairs.
        """
        u_array = p_array * self.length
        return self.u_v_from_u(u_array)

    def u_v_from_u(self, u_array: np.ndarray) -> np.ndarray:
        """Return local (u, v) coordinates from an array of local u coordinates.

        (u, v) coordinates are in their own x,y frame: start at origin, and initial
        heading is along the x axis.

        Parameters
        ----------
        u_array : np.ndarray
            u values from which to compute v values.

        Returns:
        -------
        np.ndarray
            Array of local (u, v) coordinate pairs.
        """
        v_array = (
            self.a * np.ones_like(u_array)
            + self.b * u_array
            + self.c * np.power(u_array, 2)
            + self.d * np.power(u_array, 3)
        )

        local_coords = np.stack((u_array, v_array), axis=1)

        return local_coords

    def __str__(self) -> str:
        """Returns a string representation of a cubic polynomial."""
        return f"a={self.a}, b={self.b}, c={self.c}, d={self.d}"


class ParamCubicPolynom(Geometry):
    """Class representing the parametric cubic curve from the OpenDRIVE spec.

    Parameters
    ----------
    a_u : float
        a parameter for the U curve.
    b_u : float
        b parameter for the U curve.
    c_u : float
        c parameter for the U curve.
    d_u : float
        d parameter for the U curve.
    a_v : float
        a parameter for the V curve.
    b_v : float
        b parameter for the V curve.
    c_v : float
        c parameter for the V curve.
    d_v : float
        d parameter for the V curve.
    """

    def __init__(
        self,
        a_u: float,
        b_u: float,
        c_u: float,
        d_u: float,
        a_v: float,
        b_v: float,
        c_v: float,
        d_v: float,
        x_offset: float = 0.0,
        y_offset: float = 0.0,
        heading_offset: float = 0.0,
        length: Optional[float] = None,
    ):
        """Creates a cubic polynomial in u and v directions."""
        Geometry.__init__(self, GeometryType.PARAMERTRIC_CUBIC_CURVE, x_offset, y_offset, heading_offset, length)
        # From the OpenDRIVE spec (7.7.1) we can use the call function from the
        # CubicPolynom class above but parameterized over the range [0,1]. We can
        # achieve this by setting the length of these curves to 1.0.
        self.p_u = CubicPolynom(a_u, b_u, c_u, d_u, length=1.0)
        self.p_v = CubicPolynom(a_v, b_v, c_v, d_v, length=1.0)

    def __call__(self, p_array: np.ndarray) -> np.ndarray:
        r"""Return local (u, v) coordinates from an array of parameter $p \in [0.0, 1.0]$.

        (u, v) coordinates are in their own x,y frame: start at origin, and initial
        heading is along the x axis.

        Parameters
        ----------
        p_array : np.ndarray
            p values $\in [0.0, 1.0]$ to compute parametric coordinates.

        Returns:
        -------
        np.ndarray
            Array of local (u, v) coordinate pairs.
        """
        u_array = self.p_u.u_v_from_p(p_array)[:, 1]
        v_array = self.p_v.u_v_from_p(p_array)[:, 1]

        local_coords = np.stack((u_array, v_array), axis=1)
        return local_coords

    def u_v_from_u(self, u_array: np.ndarray) -> np.ndarray:
        """Raise an error; this geometry is parameteric with no v from u method."""
        raise NotImplementedError("This geometry is only defined parametrically.")

    def __str__(self) -> str:
        """string-readable export of the polynomial."""
        return f"pU=[{str(self.p_u)}], pV=[{str(self.p_v)}]"
