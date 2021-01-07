#!/usr/bin/env python

"""
Numerical solver for non-linear time-dependent Schrodinger's equation.

author: Daniel Scheiermann
email: daniel.scheiermann@stud.uni-hannover.de
license: MIT
Please feel free to use and modify this, but keep the above information. Thanks!
"""
import sys

import functools
import numpy as np
from typing import Callable

from supersolids import functions


class Schroedinger(object):
    """
    Implements a numerical solution of the time-dependent
    non-linear Schrodinger equation for an arbitrary potential:
    i \hbar \frac{\partial}{\partial t} \psi(r,t) = \left(\frac{-\hbar^{2}}{2 m} \nabla^{2}
                                                    + V(r) + g |\psi(x,t)|^{2} \right) \psi(x,t)

    For the moment we aim to solve:
    \mu \phi_{0}(x) = \left(\frac{-1}{2} \frac{\partial^{2}}{\partial x^{2}}
                      + \frac{1}{2} x^{2} + \tilde{g} |\phi_{0}(x)|^{2} \right) \phi_{0}(x)

    We will first implement the split operator without commutator relation ($H = H_{pot} + H_{kin}$)
    WARNING: We don't use Baker-Campell-Hausdorff formula, hence the accuracy is small. This is just a draft.
    """

    def __init__(self, resolution: int, timesteps: int, L: float, dt: float, g: float = 0.0,
                 imag_time: bool = True, s: float = 1.1, E: float = 1.0,
                 dim: int = 3,
                 psi_0: Callable = functions.psi_gauss_3d,
                 V: Callable = functions.v_harmonic_3d,
                 psi_sol: Callable = functions.thomas_fermi_3d,
                 mu_sol: Callable = functions.mu_3d,
                 alpha_psi: float = 0.8,
                 alpha_V: float = 0.3,
                 ):
        """
        Parameters
        ----------
        x: array_like, float
            description

        """
        self.resolution = int(resolution)
        self.timesteps = int(timesteps)

        self.L = float(L)
        self.dt = float(dt)
        self.g = float(g)
        self.imag_time = imag_time
        self.dim = dim

        self.mu_sol = mu_sol(self.g)

        # mu = - ln(N) / (2 * dtau), where N is the norm of the psi
        self.mu = s

        # E = mu - 0.5 * g * int psi_val ** 2
        self.E = E

        self.psi = psi_0
        self.V = V
        self.psi_sol = functools.partial(psi_sol, g=self.g)

        self.x = np.linspace(-self.L, self.L, self.resolution)
        self.dx = float(2.0 * L / self.resolution)
        self.dkx = float(np.pi / self.L)

        self.kx = np.fft.fftfreq(resolution, d=1.0/(self.dkx * self.resolution))
        self.k_squared = self.kx ** 2.0

        if imag_time:
            # Convention: $e^{-iH} = e^{UH}$
            self.U = -1.0
        else:
            self.U = -1.0j

        # Add attributes as soon as they are needed (e.g. for dimension 3, all besides the error are needed)
        if dim >= 2:
            self.y = np.linspace(-self.L, self.L, self.resolution)
            self.dy = float(2.0 * L / self.resolution)
            self.dky = float(np.pi / self.L)
            self.ky = np.fft.fftfreq(resolution, d=1.0 / (self.dky * self.resolution))
            self.k_squared += self.ky ** 2.0
        if dim >= 3:
            self.z = np.linspace(-self.L, self.L, self.resolution)
            self.dz = float(2.0 * L / self.resolution)
            self.dkz = float(np.pi / self.L)
            self.kz = np.fft.fftfreq(resolution, d=1.0 / (self.dkz * self.resolution))
            self.k_squared += self.kz ** 2.0
        if dim > 3:
            print("Spatial dimension over 3. This is not implemented.", file=sys.stderr)
            sys.exit(1)

        if dim == 1:
            self.psi_val = self.psi(self.x)
            self.V_val = self.V(self.x)
            self.psi_sol_val = self.psi_sol(self.x)
            self.H_kin = np.exp(self.U * (0.5 * self.k_squared) * self.dt)
            # Here we use half steps in real space, but will use it before and after H_kin with normal steps
            # self.H_pot = np.exp(self.U * (self.V_val + self.g * np.abs(self.psi_val) ** 2.0) * (0.5 * self.dt))

        elif dim == 2:
            self.x_mesh, self.y_mesh, self.pos = functions.get_meshgrid(self.x, self.y)
            self.psi_val = self.psi(self.pos)
            self.V_val = self.V(self.pos)
            self.psi_sol_val = self.psi_sol(self.pos)

            # here a number (U) is multiplied elementwise with an 1D array (k_squared)
            self.H_kin = np.exp(self.U * (0.5 * self.k_squared) * self.dt)

            # here a number (g, then U) is multiplied elementwise with an 2D array (psi_val, then the sum)
            # Here we use half steps in real space, but will use it before and after H_kin with normal steps
            # self.H_pot = np.exp(self.U * (self.V_val + self.g * np.abs(self.psi_val) ** 2.0) * (0.5 * self.dt))

        elif dim == 3:
            self.x_mesh, self.y_mesh, self.z_mesh = np.mgrid[self.x[0]:self.x[-1]:complex(0, self.resolution),
                                                             self.y[0]:self.y[-1]:complex(0, self.resolution),
                                                             self.z[0]:self.z[-1]:complex(0, self.resolution)
                                                             ]
            self.psi_val = self.psi(self.x_mesh, self.y_mesh, self.z_mesh)
            self.V_val = self.V(self.x_mesh, self.y_mesh, self.z_mesh)
            # self.psi_sol_val = self.psi_sol(self.x_mesh, self.y_mesh, self.z_mesh)

            # here a number (U) is multiplied elementwise with an 1D array (k_squared)
            self.H_kin = np.exp(self.U * (0.5 * self.k_squared) * self.dt)

            # here a number (g, then U) is multiplied elementwise with an 2D array (psi_val, then the sum)
            # Here we use half steps in real space, but will use it before and after H_kin with normal steps
            # self.H_pot = np.exp(self.U * (self.V_val + self.g * np.abs(self.psi_val) ** 2.0) * (0.5 * self.dt))

        # attributes for animation
        self.t = 0.0

        self.alpha_psi = alpha_psi
        self.alpha_V = alpha_V

    def get_norm(self, p: float = 2.0) -> float:
        if self.dim == 1:
            psi_norm = np.sum(np.abs(self.psi_val) ** p) * self.dx
        elif self.dim == 2:
            psi_norm = np.sum(np.abs(self.psi_val) ** p) * self.dx * self.dy
        elif self.dim == 3:
            psi_norm = np.sum(np.abs(self.psi_val) ** p) * self.dx * self.dy * self.dz
        else:
            print("Spatial dimension over 3. This is not implemented.", file=sys.stderr)
            sys.exit(1)

        return psi_norm

    def time_step(self):
        # H_kin is just dependend on U and the gridpoints, which are constants, so it does not need to be recaculated
        # update H_pot before use
        H_pot = np.exp(self.U * (self.V_val + self.g * np.abs(self.psi_val) ** 2.0) * (0.5 * self.dt))
        # multiply element-wise the 2D with each other (not np.multiply)

        self.psi_val = H_pot * self.psi_val

        a = np.abs(self.psi_val[29:35, 29:34]) ** 2.0

        self.psi_val = np.fft.fftn(self.psi_val)

        # TODO: solve H_kin bug (issue 13)
        # multiply element-wise the 1D array (H_kin) with psi_val (1D, 2D or 3D), so for 2D and 3D np.multiply is needed
        # self.H_kin = np.diag(np.exp(self.U * (0.5 * self.k_squared) * self.dt))
        # self.psi_val = np.matmul(self.H_kin, self.psi_val)
        # self.psi_val = np.multiply(self.H_kin, self.psi_val)
        self.psi_val = self.H_kin * self.psi_val
        self.psi_val = np.fft.ifftn(self.psi_val)

        a = np.abs(self.psi_val[29:35, 29:34]) ** 2.0

        # update H_pot before use
        H_pot = np.exp(self.U * (self.V_val + self.g * np.abs(self.psi_val) ** 2.0) * (0.5 * self.dt))
        # multiply element-wise the 2D with each other (not np.multiply)
        self.psi_val = H_pot * self.psi_val

        self.t += self.dt

        # for self.imag_time=False, renormalization should be preserved, but we play safe here (regardless of speedup)
        # if self.imag_time:
        psi_norm_after_evolution = self.get_norm(p=2.0)
        self.psi_val /= np.sqrt(psi_norm_after_evolution)

        psi_quadratic_integral = self.get_norm(p=4.0)

        self.mu = - np.log(psi_norm_after_evolution) / (2.0 * self.dt)
        self.E = self.mu - 0.5 * self.g * psi_quadratic_integral

        print(f"mu: {self.mu}")
        print(f"E: {self.E}, E_sol: {self.mu_sol - 0.5 * self.g * psi_quadratic_integral}")
