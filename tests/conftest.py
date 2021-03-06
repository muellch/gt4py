# -*- coding: utf-8 -*-
#
# GT4Py - GridTools4Py - GridTools for Python
#
# Copyright (c) 2014-2019, ETH Zurich
# All rights reserved.
#
# This file is part the GT4Py project and the GridTools framework.
# GT4Py is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or any later
# version. See the LICENSE.txt file at the top-level directory of this
# distribution for a copy of the license or check <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""GlobalDecl configuration of test generation and execution (with Hypothesis and pytest)
"""

import hypothesis as hyp
import pytest

collect_ignore_glob = [".*", "_disabled*"]  # ignore hidden folders and disabled tests


def pytest_configure(config):
    # HealthCheck.too_slow causes more trouble than good -- especially in CIs.
    hyp.settings.register_profile(
        "slow", hyp.settings(suppress_health_check=[hyp.HealthCheck.too_slow], deadline=None)
    )
    config.addinivalue_line(
        "markers",
        "requires_cudatoolkit: mark tests that require compilation of CUDA stencils (assume cupy is installed)",
    )
    config.addinivalue_line(
        "markers",
        "requires_gpu: mark tests that require a Nvidia GPU (assume cupy and cudatoolkit are installed)",
    )
    hyp.settings.load_profile("slow")
