#!/usr/bin/env python

"""
Functions for Potential and initial wave function psi_0

author: Daniel Scheiermann
email: daniel.scheiermann@stud.uni-hannover.de
license: MIT
Please feel free to use and modify this, but keep the above information. Thanks!
"""

import functools

import numpy as np
from scipy import stats
from typing import Tuple

from supersolids import Animation
from supersolids import constants


def get_meshgrid(x, y):
    x_mesh, y_mesh = np.meshgrid(x, y)
    pos = np.empty(x_mesh.shape + (2,))
    pos[:, :, 0] = x_mesh
    pos[:, :, 1] = y_mesh

    return x_mesh, y_mesh, pos


def get_meshgrid_3d(x, y, z):
    x_mesh, y_mesh, z_mesh = np.meshgrid(x, y, z)
    pos = np.empty(x_mesh.shape + (3,))
    pos[:, :, :, 0] = x_mesh
    pos[:, :, :, 1] = y_mesh
    pos[:, :, :, 2] = z_mesh

    return x_mesh, y_mesh, z_mesh, pos


def get_parameters(N: int = 10 ** 4,
                   m: float = 164 * constants.u_in_kg,
                   a_s: float = 90.0 * constants.a_0,
                   a_dd: float = 130.0 * constants.a_0,
                   w_x: float = 2.0 * np.pi * 30.0):
    a_s_l_ho_ratio, epsilon_dd = g_qf_helper(m=m, a_s=a_s, a_dd=a_dd, w_x=w_x)
    g_qf = get_g_qf(N, a_s_l_ho_ratio, epsilon_dd)
    g = get_g(N, a_s_l_ho_ratio)

    return g, g_qf, epsilon_dd


def get_g(N: int, a_s_l_ho_ratio: float):
    g = 4.0 * np.pi * a_s_l_ho_ratio * N

    return g


def g_qf_helper(m: float = 164 * constants.u_in_kg,
                a_s: float = 90.0 * constants.a_0,
                a_dd: float = 130.0 * constants.a_0,
                w_x: float = 2.0 * np.pi * 30.0):
    l_ho = get_l_ho(m, w_x)
    epsilon_dd = a_dd / a_s
    a_s_l_ho_ratio = a_s / l_ho

    return a_s_l_ho_ratio, epsilon_dd


def get_g_qf(N: int, a_s_l_ho_ratio: float, epsilon_dd: float):
    g_qf = (32.0 / (3.0 * np.sqrt(np.pi))
            * 4.0 * np.pi * a_s_l_ho_ratio ** (5.0 / 2.0)
            * N ** (3.0 / 2.0)
            * (1.0 + (3.0 / 2.0) * epsilon_dd ** 2.0))

    return g_qf


def get_l_ho(m: float = 164.0 * constants.u_in_kg, w_x: float = 2.0 * np.pi * 30.0):
    l_ho = np.sqrt(constants.hbar / (m * w_x))
    return l_ho


def get_alphas(w_x: float = 2.0 * np.pi * 30.0,
               w_y: float = 2.0 * np.pi * 30.0,
               w_z: float = 2.0 * np.pi * 30.0):
    alpha_y = w_y / w_x
    alpha_z = w_z / w_x

    return alpha_y, alpha_z


def psi_gauss_2d_pdf(pos, mu=np.array([0.0, 0.0]), var=np.array([[1.0, 0.0], [0.0, 1.0]])):
    """
    Gives values according to gaus dirstribution (2D) with meshgrid of x,y as input

    Parameters
    ----------
    pos : np.ndarray 3D
        stacked meshgrid of an x (1D) and y (1D)
    mu : np.ndarray 2D
        Mean of gauss
    var : np.ndarray 2D
        Variance of gauss

    Returns
    -------
    z_mesh : meshgrid, 2D surface values
        values according to gaus dirstribution (2D) with meshgrid of x,y as input

    """
    cov = np.diag(var ** 2)
    rv = stats.multivariate_normal(mean=mu, cov=cov)
    z_mesh = rv.pdf(pos)

    return z_mesh


def psi_gauss_2d(x, y, a: float = 1.0, x_0: float = 0.0, y_0: float = 0.0, k_0: float = 0.0):
    """
    Gaussian wave packet of width a and momentum k_0, centered at x_0

    Parameters
    ----------
    x : sympy.symbol
        mathematical variable

    y : sympy.symbol
        mathematical variable

    a : float
        Amplitude of pulse

    x_0 : float
        Mean spatial x of pulse

    y_0 : float
        Mean spatial y of pulse

    k_0 : float
        Group velocity of pulse
    """

    return ((a * np.sqrt(np.pi)) ** (-0.5)
            * np.exp(-0.5 * (((x - x_0) * 1.0) ** 2
                             + ((y - y_0) * 1.0) ** 2) / (a ** 2) + 1j * x * k_0))


def psi_gauss_3d(x, y, z, a: float = 1.0, x_0: float = 0.0, y_0: float = 0.0, z_0: float = 0.0, k_0: float = 0.0):
    """
    Gaussian wave packet of width a and momentum k_0, centered at x_0

    Parameters
    ----------
    x : sympy.symbol
        mathematical variable

    y : sympy.symbol
        mathematical variable

    z : sympy.symbol
        mathematical variable

    a : float
        Amplitude of pulse

    x_0 : float
        Mean spatial x of pulse

    y_0 : float
        Mean spatial y of pulse

    z_0 : float
        Mean spatial z of pulse

    k_0 : float
        Group velocity of pulse
    """

    return ((a * np.sqrt(np.pi)) ** (-0.5)
            * np.exp(-0.5 * (((x - x_0) * 1.0) ** 2
                             + ((y - y_0) * 1.0) ** 2
                             + ((z - z_0) * 1.0) ** 2) / (a ** 2) + 1j * x * k_0))


def psi_gauss_1d(x, a: float = 1.0, x_0: float = 0.0, k_0: float = 0.0):
    """
    Gaussian wave packet of width a and momentum k_0, centered at x_0

    Parameters
    ----------
    x : sympy.symbol
        mathematical variable

    a : float
        Amplitude of pulse

    x_0 : float
        Mean spatial x of pulse

    k_0 : float
        Group velocity of pulse
    """

    return ((a * np.sqrt(np.pi)) ** (-0.5)
            * np.exp(-0.5 * ((x - x_0) * 1. / a) ** 2 + 1j * x * k_0))


def psi_pdf(x, loc: float = 0.0, scale: float = 1.0):
    """
    Mathematical function of gauss pulse

    Parameters
    ----------
    x: sympy.symbol
        mathematical variable

    loc: float
        Localization of pulse centre

    scale: float
        Scale of pulse
    """
    return stats.norm.pdf(x, loc=loc, scale=scale)


def psi_rect(x, x_min: float = -0.5, x_max: float = 0.5, a: float = 1.0):
    """
    Mathematical function of rectengular pulse between x_min and x_max with amplitude a

    Parameters
    ----------
    x: sympy.symbol
        mathematical variable

    x_min: float
        Minimum x value of pulse (spatial)

    x_max: float
        Maximum x value of pulse (spatial)

    a: float
        Amplitude of pulse
    """

    pulse = np.select([x < x_min, x < x_max, x_max < x], [0, a, 0])
    assert pulse.any(), ("Pulse is completely 0. Resolution is too small. "
                         "Resolution needs to be set as fft is used onto the pulse.")

    return pulse


def psi_gauss_solution(x):
    """
     Mathematical function of solution of non-linear Schroedinger for g=0

     Parameters
     ----------
     x: sympy.symbol
        mathematical variable
    """

    return np.exp(-x ** 2) / np.sqrt(np.pi)


def thomas_fermi_1d(x, g: float = 0.0):
    """
    Mathematical function of Thomas-Fermi distribution with coupling constant g

    Parameters
    ----------
    x : sympy.symbol
        mathematical variable

    g : float
        coupling constant
    """

    if g != 0:
        # mu is the chemical potential
        mu = mu_1d(g)

        # this needs to be >> 1, e.g 5.3
        # print(np.sqrt(2 * mu))

        return mu * (1 - ((x ** 2) / (2 * mu))) / g

    else:
        return None


def thomas_fermi_2d(x, y, g: float = 0.0):
    """
    Mathematical function of Thomas-Fermi distribution with coupling constant g

    Parameters
    ----------
    x : sympy.symbol
        mathematical variable

    g : float
       coupling constant
    """

    if g != 0:
        # mu is the chemical potential
        mu = mu_2d(g)

        # this needs to be >> 1, e.g 5.3
        # print(np.sqrt(2 * mu))

        return mu * (1 - ((x ** 2 + y ** 2) / (2 * mu))) / g

    else:
        return None


def thomas_fermi_2d_pos(pos, g: float = 0.0):
    x = pos[:, :, 0]
    y = pos[:, :, 1]

    return thomas_fermi_2d(x, y, g=g)


def thomas_fermi_3d(x, y, z, g: float = 0.0):
    """
    Mathematical function of Thomas-Fermi distribution with coupling constant g

    Parameters
    ----------
    x : sympy.symbol
        mathematical variable

    g : float
       coupling constant
    """

    if g != 0:
        # mu is the chemical potential
        mu = mu_3d(g)

        # this needs to be >> 1, e.g 5.3
        # print(np.sqrt(2 * mu))

        return mu * (1 - ((x ** 2 + y ** 2 + z ** 2) / (2 * mu))) / g

    else:
        return None


def mu_1d(g: float = 0.0):
    # mu is the chemical potential
    mu = ((3.0 * g) / (4.0 * np.sqrt(2.0))) ** (2.0 / 3.0)

    return mu


def mu_2d(g: float = 0.0):
    # mu is the chemical potential
    mu = np.sqrt(g / np.pi)

    return mu


def mu_3d(g: float = 0.0):
    # mu is the chemical potential
    mu = ((15 * g) / (16 * np.sqrt(2) * np.pi)) ** (2 / 5)

    return mu


def v_harmonic_1d(x):
    return 0.5 * x ** 2


def v_harmonic_2d(pos, alpha_y: float = 1.0):
    x = pos[:, :, 0]
    y = pos[:, :, 1]

    return v_2d(x, y, alpha_y=1.0)


def v_2d(x, y, alpha_y=1.0):
    return 0.5 * (x ** 2 + y ** 2)


def v_harmonic_3d(x, y, z, alpha_y: float = 1.0, alpha_z: float = 1.0):
    return 0.5 * (x ** 2 + (alpha_y * y) ** 2 + (alpha_z * z) ** 2)


def dipol_dipol_interaction(kx_mesh: float, ky_mesh: float, kz_mesh: float):
    k_squared = kx_mesh ** 2.0 + ky_mesh ** 2.0 + kz_mesh ** 2.0
    factor = 3.0 * (kz_mesh ** 2.0)
    # for [0, 0, 0] there is a singularity and factor/k_squared is 0/0, so we arbitrary set the divisor to 1.0
    k_squared_singular_free = np.where(k_squared == 0.0, 1.0, k_squared)
    V_k_val = ((factor / k_squared_singular_free) - 1.0)

    # Remove singularities (at this point there should not be any)
    V_k_val[np.isnan(V_k_val)] = 0.0

    return V_k_val


def camera_func_r(frame: int,
                  r_0: float = 10.0,
                  phi_0: float = 45.0,
                  z_0: float = 20.0,
                  r_per_frame: float = 10.0) -> float:
    r = r_0 + r_per_frame * frame
    return r


def camera_func_phi(frame: int,
                    r_0: float = 10.0,
                    phi_0: float = 45.0,
                    z_0: float = 20.0,
                    phi_per_frame: float = 10.0) -> float:
    phi = phi_0 + (2.0 * np.pi / 360.0) * phi_per_frame * frame
    return phi


def noise_mesh(min: float = 0.8,
               max: float = 1.2,
               shape: Tuple[int, int, int] = (64, 64, 64)) -> np.ndarray:

    noise = min + (max - min) * np.random.rand(*shape)

    return noise

# Script runs, if script is run as main script (called by python *.py)
if __name__ == '__main__':
    # due to fft of the points the resolution needs to be 2 ** datapoints_exponent
    datapoints_exponent: int = 6
    resolution: int = 2 ** datapoints_exponent

    # constants needed for the Schroedinger equation
    max_timesteps = 10
    dt = 0.05

    # functions needed for the Schroedinger equation (e.g. potential: V, initial wave function: psi_0)
    V_1d = v_harmonic_1d
    V_2d = v_harmonic_2d
    V_3d = v_harmonic_3d

    # functools.partial sets all arguments except x, as multiple arguments for Schroedinger aren't implement yet
    # psi_0 = functools.partial(functions.psi_0_rect, x_min=-1.00, x_max=-0.50, a=2)
    psi_0_1d = functools.partial(psi_gauss_1d, a=1, x_0=0, k_0=0)
    psi_0_2d = functools.partial(psi_gauss_2d_pdf, mu=np.array([0.0, 0.0]), var=np.array([1.0, 1.0]))
    psi_0_3d = functools.partial(psi_gauss_3d, a=1, x_0=0, y_0=0, z_0=0, k_0=0)

    # testing for 2d plot
    L = 10
    x = np.linspace(-L, L, resolution)
    y = np.linspace(-L, L, resolution)
    x_mesh, y_mesh, pos = get_meshgrid(x, y)
    Animation.plot_2d(L=L, resolution=resolution,
                      x_lim=(-2, 2), y_lim=(-2, 2), z_lim=(0.0, 0.040),
                      alpha=[0.6, 0.8], pos=[pos, pos], func=[lambda pos: np.abs(psi_0_2d(pos)) ** 2, V_2d])
