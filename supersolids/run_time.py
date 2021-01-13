#!/usr/bin/env python

"""
Helper-Functions/decorators to compute parallel and profile functions

author: Daniel Scheiermann
email: daniel.scheiermann@stud.uni-hannover.de
license: MIT
Please feel free to use and modify this, but keep the above information. Thanks!
"""

import contextlib
import time

from typing import Iterator


@contextlib.contextmanager
def run_time() -> Iterator:
    start: float = time.perf_counter()
    try:
        yield
    finally:
        time_measured: float = time.perf_counter() - start
        print("Runtime: {:.8f} s".format(time_measured))

    return time_measured
