#!/usr/bin/env python

# author: Daniel Scheiermann
# email: daniel.scheiermann@stud.uni-hannover.de
# license: MIT
# Please feel free to use and modify this, but keep the above information.

"""
Animation for the numerical solver for the non-linear
time-dependent Schrodinger equation for 1D, 2D and 3D in single-core.

"""
import argparse
import pickle
from pathlib import Path

import numpy as np

from supersolids.Animation.Animation import Animation

from supersolids.Schroedinger import Schroedinger
from supersolids.tools.simulate_case import simulate_case

# Script runs, if script is run as main script (called by python *.py)
if __name__ == "__main__":
    # Use parser to
    parser = argparse.ArgumentParser(description="Load old simulations of Schrödinger system "
                                                 "and continue simulation from there.")
    parser.add_argument("-max_timesteps", metavar="max_timesteps", type=int, default=80001,
                        help="Simulate until accuracy or maximum of steps of length dt is reached")
    parser.add_argument("-dir_path", metavar="dir_path", type=str, default="~/supersolids/results",
                        help="Absolute path to save data to")
    parser.add_argument("-dir_name", metavar="dir_path", type=str, default="movie" + "%03d" % 1,
                        help="Name of directory where the files to load lie. "
                             "For example the standard naming convention is movie001")
    parser.add_argument("-filename_schroedinger", metavar="filename_schroedinger", type=str,
                        default="schroedinger.pkl",
                        help="Name of file, where the Schroedinger object is saved")
    parser.add_argument("-filename_npz", metavar="filename_npz",
                        type=str, default="step_" + "%06d" % 1 + ".npz",
                        help="Name of file, where psi_val is saved. "
                             "For example the standard naming convention is step_000001.npz")
    parser.add_argument("--offscreen", default=False, action="store_true",
                        help="If not used, interactive animation is shown and saved as mp4."
                             "If used, Schroedinger is saved as pkl and allows offscreen usage.")
    args = parser.parse_args()
    print(f"args: {args}")

    try:
        dir_path = Path(args.dir_path).expanduser()
    except Exception:
        dir_path = args.dir_path

    input_path = Path(dir_path, args.dir_name)
    schroedinger_path = Path(input_path, args.filename_schroedinger)
    psi_val_path = Path(input_path, args.filename_npz)

    Anim: Animation = Animation(plot_psi_sol=False,
                                plot_V=False,
                                alpha_psi=0.8,
                                alpha_psi_sol=0.5,
                                alpha_V=0.3,
                                filename="anim.mp4",
                                )

    try:
        print("Load schroedinger")
        with open(schroedinger_path, "rb") as f:
            # WARNING: this is just the input Schroedinger at t=0
            System = pickle.load(file=f)

        print(f"File at {schroedinger_path} loaded.")
        try:
            # get the psi_val of Schroedinger at other timesteps (t!=0)
            with open(psi_val_path, "rb") as f:
                System.psi_val = np.load(file=f)["psi_val"]

            System.max_timesteps = args.max_timesteps
            SystemResult: Schroedinger = simulate_case(
                System=System,
                Anim=Anim,
                accuracy=10 ** -12,
                delete_input=False,
                dir_path=dir_path,
                offscreen=args.offscreen,
                x_lim=(-2.0, 2.0),  # from here just matplotlib
                y_lim=(-2.0, 2.0),
                z_lim=(0, 0.5),
            )

        except FileNotFoundError:
            print(f"File at {psi_val_path} not found.")

    except FileNotFoundError:
        print(f"File at {schroedinger_path} not found.")

