#!/usr/bin/env python

"""
Functions for Potential and initial wave function psi_0

author: Daniel Scheiermann
email: daniel.scheiermann@stud.uni-hannover.de
license: MIT
Please feel free to use and modify this, but keep the above information. Thanks!
"""

from pathlib import Path

import numpy as np
import ffmpeg
from mayavi import mlab
from typing import Tuple

from supersolids import Animation, functions, Schroedinger


def get_image_path(dir_path: Path, dir_name: str = "movie", counting_format: str = "%03d"):
    """
    Looks up all directories with matching dir_name and counting format in dir_path.
    Gets the highest number and returns a path with dir_name counted one up (prevents colliding with old data).

    Parameters
    ----------
    dir_path : Path
               Path where to look for old directories (movie data)
    dir_name : str
               General name of the directories without the counter
    counting_format : str
                      Format of counter of the directories

    Returns
    -------
    Path for the new directory (not colliding with old data)
    """
    # "movie" and "%03d" strings are hardcoded in mayavi movie_maker _update_subdir
    existing = sorted([x for x in dir_path.glob(dir_name + "*") if x.is_dir()])
    try:
        last_index = int(existing[-1].name.split(dir_name)[1])
    except Exception as e:
        assert last_index is not None, ("Extracting last index from dir_path failed")
    input_path = Path(dir_path, dir_name + counting_format % last_index)

    return input_path


@mlab.animate(delay=10, ui=True)
def animate(System: Schroedinger.Schroedinger, accuracy: float = 10 ** -6,
            x_lim: Tuple[float, float] = (-1, 1),
            y_lim: Tuple[float, float] = (-1, 1),
            z_lim: Tuple[float, float] = (-1, 1),
            slice_x_index: int = 0, slice_y_index: int = 0,
            psi_sol=functions.thomas_fermi_3d):
    """
    Animates solving of the Schroedinger equations of System with mayavi in 3D.
    Animation is limited to System.timesteps or the convergence according to accuracy.

    Parameters
    ----------
    System : Schroedinger.Schoredinger
             Schrödinger equations for the specified system

    accuracy : float
               Convergence is reached when relative error of s ios smaller than accuracy,
               where s is System.s = - np.log(psi_norm_after_evolution) / (2.0 * self.dt)

    x_lim : Tuple[float, float]
    y_lim : Tuple[float, float]
    z_lim : Tuple[float, float]
    slice_x_index : int
                    Index of projection in terms of indexes of System.x
    slice_y_index : int
                    Index of projection in terms of indexes of System.y

    Returns
    -------

    """
    prob_3d = np.abs(System.psi_val) ** 2
    p = mlab.contour3d(System.x_mesh, System.y_mesh, System.z_mesh, prob_3d,
                       colormap="spectral", opacity=0.5, transparent=True)

    slice_x = mlab.volume_slice(System.x_mesh, System.y_mesh, System.z_mesh, prob_3d, colormap="spectral",
                                plane_orientation="x_axes",
                                slice_index=slice_x_index,
                                extent=[*x_lim, *y_lim, *z_lim])
    slice_y = mlab.volume_slice(System.x_mesh, System.y_mesh, System.z_mesh, prob_3d, colormap="spectral",
                                plane_orientation="y_axes",
                                slice_index=slice_y_index,
                                extent=[*x_lim, *y_lim, *z_lim])

    sol = mlab.contour3d(System.x_mesh, System.y_mesh, System.z_mesh, psi_sol,
                         colormap="spectral", opacity=0.5, transparent=True)

    for i in range(0, System.timesteps):
        s_old = System.s
        System.time_step()
        s_rel = np.abs((System.s - s_old) / System.s)
        print(f"s_rel: {s_rel}")
        if s_rel < accuracy:
            print(f"accuracy reached: {s_rel}")
            break
        prob_3d = np.abs(System.psi_val) ** 2
        slice_x.mlab_source.trait_set(scalars=prob_3d)
        slice_y.mlab_source.trait_set(scalars=prob_3d)
        p.mlab_source.trait_set(scalars=prob_3d)
        # sol.mlab_source.trait_set(scalars=psi_sol)
        yield


class MayaviAnimation:
    mayavi_counter: int = 0
    animate = staticmethod(animate)

    def __init__(self, dim=3, dir_path=Path(__file__).parent.joinpath("results")):
        """
        Creates an Animation with mayavi for a Schroedinger equation
        Methods need the object Schroedinger with the parameters of the equation
        """
        if not dir_path.is_dir():
            dir_path.mkdir(parents=True)

        MayaviAnimation.mayavi_counter += 1
        self.dim = dim

        self.fig = mlab.figure()
        mlab.title("")
        self.ax = mlab.axes(line_width=2, nb_labels=5)
        self.ax.axes.visibility = True

        # dir_path need to be saved to access it after the figure closed
        self.dir_path = dir_path

        self.fig.scene.disable_render = False
        # anti_aliasing default is 8, and removes resolution issues when downscaling, but takes longer
        self.fig.scene.anti_aliasing_frames = 8
        self.fig.scene.movie_maker.record = True
        # set dir_path to save images to
        self.fig.scene.movie_maker.directory = dir_path

    def create_movie(self,
                     dir_path: Path = None,
                     input_data_file_pattern: str = "*.png",
                     filename: str = "anim.mp4",
                     delete_input: bool = True):
        """
        Creates movie filename with all matching pictures from input_data_file_pattern.
        By default deletes all input pictures after creation of movie to save disk space.

        Parameters
        ----------
        delete_input : bool
                       Flag to delete input_data after creation of movie
        dir_path : Path
                   Path where to look for old directories (movie data)

        input_data_file_pattern : str
                                  regex pattern to find all input data

        filename : str
                  filename with filetype to save the movie to

        Returns
        -------

        """
        if dir_path is None:
            input_path = get_image_path(self.dir_path)
        else:
            input_path = get_image_path(dir_path)

        input_data = Path(input_path, input_data_file_pattern)
        output_path = Path(input_path, filename)
        print(f"input_data: {input_data}")

        # requires either mencoder or ffmpeg to be installed on your system
        # from command line:
        # ffmpeg -f image2 -r 10 -i anim%05d.png -qscale 0 anim.mp4 -pass 2
        ffmpeg.input(input_data, pattern_type="glob", framerate=25).output(str(output_path)).run()

        if delete_input:
            # remove all input files
            input_data_used = [x for x in input_path.glob(input_data_file_pattern) if x.is_file()]
            for trash_file in input_data_used:
                trash_file.unlink()


# Script runs, if script is run as main script (called by python *.py)
if __name__ == "__main__":
    Harmonic = Schroedinger.Schroedinger(resolution=2 ** 6, timesteps=100, L=3, dt=1.0, g=1.0, imag_time=True, dim=3,
                                         s=1.1, E=1.0,
                                         psi_0=functions.psi_gauss_3d,
                                         V=functions.v_harmonic_3d,
                                         psi_sol=functions.thomas_fermi
                                         )
    may = MayaviAnimation(dim=Harmonic.dim, dir_path=Path(__file__).parent.joinpath("results"))
    may.animate(Harmonic, x_lim=(-10, 5), y_lim=(-1, 1), z_lim=(-1, 1))
    mlab.show()
    may.create_movie(dir_path=None, input_data_file_pattern="*.png", filename="anim.mp4")
