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

import numpy as np

import gt4py as gt
from gt4py import gtscript
from gt4py import ir as gt_ir
from gt4py import analysis as gt_analysis
from gt4py import backend as gt_backend
from gt4py import storage as gt_storage
from gt4py import utils as gt_utils
from gt4py.definitions import Extent, StencilID

REGISTRY = gt_utils.Registry()
EXTERNALS_REGISTRY = gt_utils.Registry()


def register(externals):
    if callable(externals):
        func = externals  # wacky hacky!
        EXTERNALS_REGISTRY.setdefault(func.__name__, {})
        REGISTRY.register(func.__name__, func)
        return func
    else:

        def register_inner(arg_inner):
            EXTERNALS_REGISTRY.register(arg_inner.__name__, externals)
            REGISTRY.register(arg_inner.__name__, arg_inner)
            return arg_inner

        return register_inner


Field0D = gtscript.Field[np.float_, ()]
Field3D = gtscript.Field[np.float_]


@register
def copy_stencil(field_a: Field3D, field_b: Field3D):
    with computation(PARALLEL), interval(...):
        field_b = field_a[0, 0, 0]


@register
def copy_stencil_plus_one(field_a: Field3D, field_b: Field3D):
    with computation(PARALLEL), interval(...):
        field_b = field_a[0, 0, 0] + 1


@register
def runtime_if(field_a: Field3D, field_b: Field3D):
    with computation(BACKWARD), interval(...):
        if field_a > 0.0:
            field_b = -1
            field_a = -field_a
        else:
            field_b = 1
            field_a = field_a


@register
def simple_horizontal_diffusion(in_field: Field3D, coeff: Field3D, out_field: Field3D):
    with computation(PARALLEL), interval(...):
        lap_field = 4.0 * in_field[0, 0, 0] - (
            in_field[1, 0, 0] + in_field[-1, 0, 0] + in_field[0, 1, 0] + in_field[0, -1, 0]
        )
        flx_field = lap_field[1, 0, 0] - lap_field[0, 0, 0]
        fly_field = lap_field[0, 1, 0] - lap_field[0, 0, 0]
        out_field = in_field[0, 0, 0] - coeff[0, 0, 0] * (
            flx_field[0, 0, 0] - flx_field[-1, 0, 0] + fly_field[0, 0, 0] - fly_field[0, -1, 0]
        )


@register
def tridiagonal_solver(inf: Field3D, diag: Field3D, sup: Field3D, rhs: Field3D, out: Field3D):
    with computation(FORWARD), interval(0, 1):
        sup = sup / diag
        rhs = rhs / diag
    with computation(FORWARD), interval(1, None):
        sup = sup / (diag - sup[0, 0, -1] * inf)
        rhs = (rhs - inf * rhs[0, 0, -1]) / (diag - sup[0, 0, -1] * inf)
    with computation(BACKWARD), interval(0, -1):
        out = rhs - sup * out[0, 0, 1]
    with computation(BACKWARD), interval(-1, None):
        out = rhs


@register(externals={"BET_M": 0.5, "BET_P": 0.5})
def vertical_advection_dycore(
    utens_stage: Field3D,
    u_stage: Field3D,
    wcon: Field3D,
    u_pos: Field3D,
    utens: Field3D,
    *,
    dtr_stage: float,
):
    from __externals__ import BET_M, BET_P

    with computation(FORWARD), interval(0, 1):
        gcv = 0.25 * (wcon[1, 0, 1] + wcon[0, 0, 1])
        cs = gcv * BET_M

        ccol = gcv * BET_P
        bcol = dtr_stage - ccol[0, 0, 0]

        # update the d column
        correction_term = -cs * (u_stage[0, 0, 1] - u_stage[0, 0, 0])
        dcol = dtr_stage * u_pos[0, 0, 0] + utens[0, 0, 0] + utens_stage[0, 0, 0] + correction_term

        # Thomas forward
        divided = 1.0 / bcol[0, 0, 0]
        ccol = ccol[0, 0, 0] * divided
        dcol = dcol[0, 0, 0] * divided

    with computation(FORWARD), interval(1, -1):
        gav = -0.25 * (wcon[1, 0, 0] + wcon[0, 0, 0])
        gcv = 0.25 * (wcon[1, 0, 1] + wcon[0, 0, 1])

        as_ = gav * BET_M
        cs = gcv * BET_M

        acol = gav * BET_P
        ccol = gcv * BET_P
        bcol = dtr_stage - acol[0, 0, 0] - ccol[0, 0, 0]

        # update the d column
        correction_term = -as_ * (u_stage[0, 0, -1] - u_stage[0, 0, 0]) - cs * (
            u_stage[0, 0, 1] - u_stage[0, 0, 0]
        )
        dcol = dtr_stage * u_pos[0, 0, 0] + utens[0, 0, 0] + utens_stage[0, 0, 0] + correction_term

        # Thomas forward
        divided = 1.0 / (bcol[0, 0, 0] - ccol[0, 0, -1] * acol[0, 0, 0])
        ccol = ccol[0, 0, 0] * divided
        dcol = (dcol[0, 0, 0] - (dcol[0, 0, -1]) * acol[0, 0, 0]) * divided

    with computation(FORWARD), interval(-1, None):
        gav = -0.25 * (wcon[1, 0, 0] + wcon[0, 0, 0])
        as_ = gav * BET_M
        acol = gav * BET_P
        bcol = dtr_stage - acol[0, 0, 0]

        # update the d column
        correction_term = -as_ * (u_stage[0, 0, -1] - u_stage[0, 0, 0])
        dcol = dtr_stage * u_pos[0, 0, 0] + utens[0, 0, 0] + utens_stage[0, 0, 0] + correction_term

        # Thomas forward
        divided = 1.0 / (bcol[0, 0, 0] - ccol[0, 0, -1] * acol[0, 0, 0])
        dcol = (dcol[0, 0, 0] - (dcol[0, 0, -1]) * acol[0, 0, 0]) * divided
    # with computation(BACKWARD), interval(0, -1):
    #     datacol = dcol[0, 0, 0] - ccol[0, 0, 0] * data_col[0, 0, 1]
    #     data_col = datacol
    #     utens_stage = dtr_stage * (datacol) - u_pos[0, 0, 0]

    with computation(BACKWARD), interval(-1, None):
        datacol = dcol[0, 0, 0]
        data_col = datacol
        utens_stage = dtr_stage * (datacol - u_pos[0, 0, 0])
    with computation(BACKWARD), interval(0, -1):
        datacol = dcol[0, 0, 0] - ccol[0, 0, 0] * data_col[0, 0, 1]
        data_col = datacol
        utens_stage = dtr_stage * (datacol - u_pos[0, 0, 0])


@register
def horizontal_diffusion(in_field: Field3D, out_field: Field3D, coeff: Field3D):
    with computation(PARALLEL), interval(...):
        lap_field = 4.0 * in_field[0, 0, 0] - (
            in_field[1, 0, 0] + in_field[-1, 0, 0] + in_field[0, 1, 0] + in_field[0, -1, 0]
        )
        res = lap_field[1, 0, 0] - lap_field[0, 0, 0]
        flx_field = 0 if (res * (in_field[1, 0, 0] - in_field[0, 0, 0])) > 0 else res
        res = lap_field[0, 1, 0] - lap_field[0, 0, 0]
        fly_field = 0 if (res * (in_field[0, 1, 0] - in_field[0, 0, 0])) > 0 else res
        out_field = in_field[0, 0, 0] - coeff[0, 0, 0] * (
            flx_field[0, 0, 0] - flx_field[-1, 0, 0] + fly_field[0, 0, 0] - fly_field[0, -1, 0]
        )
