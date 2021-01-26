#!/usr/bin/env python

# author: Daniel Scheiermann
# email: daniel.scheiermann@stud.uni-hannover.de
# license: MIT
# Please feel free to use and modify this, but keep the above information.

"""
Animation for the numerical solver for the non-linear
time-dependent Schrodinger equation.

"""

import functools
import psutil

import numpy as np

from supersolids import constants
from supersolids import functions
from supersolids import simulate_case

# Script runs, if script is run as main script (called by python *.py)
if __name__ == "__main__":
    # Define constants (needed for the Schroedinger equation)

    # due to fft of the points the res
    # needs to be 2 ** resolution_exponent
    Res = functions.Resolution(x=2 ** 8, y=2 ** 8, z=2 ** 6)

    Box = functions.Box(x0=-15, x1=15,
                        y0=-15, y1=15,
                        z0=-7, z1=7)

    dt: float = 2 * 10 ** -2 # 0.001
    N: int = 3.8 * 10 ** 4 # 38000
    m: float = 164.0 * constants.u_in_kg
    a_dd: float = 130.0 * constants.a_0
    a_s: float = 85.0 * constants.a_0

    w_x: float = 2.0 * np.pi * 30.0
    w_y: float = 2.0 * np.pi * 60.0
    w_z: float = 2.0 * np.pi * 160.0

    alpha_y, alpha_z = functions.get_alphas(w_x=w_x, w_y=w_y, w_z=w_z)
    g, g_qf, e_dd, a_s_l_ho_ratio = functions.get_parameters(
        N=N, m=m, a_s=a_s, a_dd=a_dd, w_x=w_x)
    print(f"g, g_qf, epsilon_dd, alpha_y, alpha_z: "
          f"{g, g_qf, e_dd, alpha_y, alpha_z}")

    # psi_sol_3d = functions.thomas_fermi_3d
    kappa = functions.get_kappa(alpha_z=alpha_z, e_dd=e_dd,
                                x_min=0.1, x_max=5.0, res=1000)
    R_r, R_z = functions.get_R_rz(kappa=kappa, e_dd=e_dd, N=N,
                                  a_s_l_ho_ratio=a_s_l_ho_ratio)
    psi_sol_3d = functools.partial(functions.density_in_trap,
                                   R_r=R_r, R_z=R_z)
    print(f"kappa: {kappa}, R_r: {R_r}, R_z: {R_z}")

    # Define functions (needed for the Schroedinger equation)
    # (e.g. potential: V, initial wave function: psi_0)
    V_1d = functions.v_harmonic_1d
    V_2d = functools.partial(functions.v_harmonic_2d, alpha_y=alpha_y)
    V_3d = functools.partial(
        functions.v_harmonic_3d,
        alpha_y=alpha_y,
        alpha_z=alpha_z)

    V_3d_ddi = functools.partial(functions.dipol_dipol_interaction,
                                 r_cut=1.0 * Box.min_length() / 2.0)

    # functools.partial sets all arguments except x, y, z,
    # psi_0_1d = functools.partial(
    #     functions.psi_0_rect, x_min=-0.25, x_max=-0.25, a=2.0)
    psi_0_1d = functools.partial(
        functions.psi_gauss_1d, a=3.0, x_0=0.0, k_0=0.0)
    psi_0_2d = functools.partial(functions.psi_gauss_2d_pdf,
                                 mu=[0.0, 0.0],
                                 var=np.array([[1.0, 0.0], [0.0, 1.0]])
                                 )

    psi_0_3d = functools.partial(
        functions.psi_gauss_3d,
        a_x=8.0,
        a_y=4.0,
        a_z=2.0,
        x_0=0.0,
        y_0=0.0,
        z_0=0.0,
        k_0=0.0)
    # psi_0_3d = functools.partial(functions.prob_in_trap, R_r=R_r, R_z=R_z)

    psi_0_noise_3d = functions.noise_mesh(
        min=0.8, max=1.4, shape=(Res.x, Res.y, Res.z))

    # Used to remember that 2D need the special pos function (g is set inside
    # of Schroedinger for convenience)
    psi_sol_1d = functions.thomas_fermi_1d
    psi_sol_2d = functions.thomas_fermi_2d_pos

    psi_sol_3d_cut_x = functools.partial(functions.density_in_trap,
                                         y=0, z=0, R_r=R_r, R_z=R_z)

    psi_sol_3d_cut_z = functools.partial(functions.density_in_trap,
                                         x=0, y=0, R_r=R_r, R_z=R_z)

    # TODO: get mayavi lim to work
    # 3D works in single core mode
    simulate_case.simulate_case(Box,
                                Res,
                                max_timesteps=2001,
                                dt=dt,
                                g=g,
                                g_qf=g_qf,
                                e_dd=e_dd,
                                imag_time=True,
                                mu=1.1,
                                E=1.0,
                                psi_0=psi_0_3d,
                                V=V_3d,
                                V_interaction=V_3d_ddi,
                                psi_sol=psi_sol_3d,
                                mu_sol=functions.mu_3d,
                                plot_psi_sol=False,
                                psi_sol_3d_cut_x=psi_sol_3d_cut_x,
                                psi_sol_3d_cut_z=psi_sol_3d_cut_z,
                                plot_V=False,
                                psi_0_noise=psi_0_noise_3d,
                                alpha_psi=0.8,
                                alpha_psi_sol=0.5,
                                alpha_V=0.3,
                                accuracy=10 ** -8,
                                filename="anim.mp4",
                                x_lim=(-2.0, 2.0),
                                y_lim=(-2.0, 2.0),
                                z_lim=(0, 0.5),
                                slice_x_index=int(Res.x / 8),
                                slice_y_index=int(Res.y / 8),
                                slice_z_index=int(Res.z / 2),
                                interactive=True,
                                camera_r_func=functools.partial(
                                    functions.camera_func_r,
                                    r_0=40.0, phi_0=45.0, z_0=50.0, r_per_frame=0.0),
                                camera_phi_func=functools.partial(
                                    functions.camera_func_phi,
                                    r_0=40.0, phi_0=45.0, z_0=50.0, phi_per_frame=5.0),
                                camera_z_func=functools.partial(
                                    functions.camera_func_z,
                                    r_0=40.0, phi_0=45.0, z_0=50.0, z_per_frame=0.0),
                                delete_input=False
                                )
    print("Single core done")
