---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

+++ {"tags": []}

# Hands on Session of the GT4Py Workshop

## Installation
Please follow the instructions in the README.md

## Import Modules

```{code-cell} ipython3
import numpy as np

from functional.ffront.decorator import program, scan_operator, field_operator
from functional.iterator.embedded import np_as_located_field
from functional.ffront.fbuiltins import Field, Dimension
from functional.common import DimensionKind
```

+++ {"tags": []}

## Connectivities

```{code-cell} ipython3
# TODO delete connectivities that are not needed
@dataclass
class SimpleMeshData:
    e2c2v_table = np.asarray(
        [
            [0, 1, 4, 6],  # 0
            [0, 4, 1, 3],  # 1
            [0, 3, 4, 2],  # 2
            [1, 2, 5, 7],  # 3
            [1, 5, 2, 4],  # 4
            [1, 4, 5, 0],  # 5
            [2, 0, 3, 8],  # 6
            [2, 3, 5, 0],  # 7
            [2, 5, 1, 3],  # 8
            [3, 4, 0, 7],  # 9
            [3, 7, 4, 6],  # 10
            [3, 6, 7, 5],  # 11
            [4, 5, 8, 1],  # 12
            [4, 8, 7, 5],  # 13
            [4, 7, 3, 8],  # 14
            [5, 3, 6, 2],  # 15
            [6, 5, 3, 8],  # 16
            [8, 5, 6, 4],  # 17
            [6, 7, 3, 1],  # 18
            [6, 1, 7, 0],  # 19
            [6, 0, 1, 8],  # 20
            [7, 8, 2, 4],  # 21
            [7, 2, 8, 1],  # 22
            [7, 1, 2, 6],  # 23
            [8, 6, 0, 5],  # 24
            [8, 0, 6, 2],  # 25
            [8, 2, 0, 6],  # 26
        ]
    )

    e2c_table = np.asarray(
        [
            [0, 15],
            [0, 3],
            [3, 2],
            [1, 16],
            [1, 4],
            [0, 4],
            [2, 17],
            [2, 5],
            [1, 5],
            [3, 6],
            [6, 9],
            [9, 8],
            [4, 7],
            [7, 10],
            [6, 10],
            [5, 8],
            [8, 11],
            [7, 11],
            [9, 12],
            [12, 15],
            [15, 14],
            [10, 13],
            [13, 16],
            [12, 16],
            [11, 14],
            [14, 17],
            [13, 17],
        ]
    )

    e2v_table = np.asarray(
        [
            [0, 1],
            [0, 4],
            [0, 3],
            [1, 2],
            [1, 5],
            [1, 4],
            [2, 0],
            [2, 3],
            [2, 5],
            [3, 4],
            [3, 7],
            [3, 6],
            [4, 5],
            [4, 8],
            [4, 7],
            [5, 3],
            [5, 6],
            [5, 8],
            [6, 7],
            [6, 1],
            [6, 0],
            [7, 8],
            [7, 2],
            [7, 1],
            [8, 6],
            [8, 0],
            [8, 2],
        ]
    )

    e2c2e_table = np.asarray(
        [
            [1, 5, 19, 20],
            [0, 5, 2, 9],
            [1, 9, 6, 7],
            [4, 8, 22, 23],
            [3, 8, 5, 12],
            [0, 1, 4, 12],
            [7, 2, 25, 26],
            [6, 2, 8, 15],
            [3, 4, 7, 15],
            [1, 2, 10, 14],
            [9, 14, 11, 18],
            [10, 18, 15, 16],
            [4, 5, 13, 17],
            [12, 17, 14, 21],
            [9, 10, 13, 21],
            [7, 8, 16, 11],
            [15, 11, 17, 24],
            [12, 13, 16, 24],
            [10, 11, 19, 23],
            [18, 23, 20, 0],
            [19, 0, 24, 25],
            [13, 14, 22, 26],
            [21, 26, 23, 3],
            [18, 19, 22, 3],
            [16, 17, 25, 20],
            [24, 20, 26, 6],
            [25, 6, 21, 22],
        ]
    )

    e2c2eO_table = np.asarray(
        [
            [0, 1, 5, 19, 20],
            [0, 1, 5, 2, 9],
            [1, 2, 9, 6, 7],
            [3, 4, 8, 22, 23],
            [3, 4, 8, 5, 12],
            [0, 1, 5, 4, 12],
            [6, 7, 2, 25, 26],
            [6, 7, 2, 8, 15],
            [3, 4, 8, 7, 15],
            [1, 2, 9, 10, 14],
            [9, 10, 14, 11, 18],
            [10, 11, 18, 15, 16],
            [4, 5, 12, 13, 17],
            [12, 13, 17, 14, 21],
            [9, 10, 14, 13, 21],
            [7, 8, 15, 16, 11],
            [15, 16, 11, 17, 24],
            [12, 13, 17, 16, 24],
            [10, 11, 18, 19, 23],
            [18, 19, 23, 20, 0],
            [19, 20, 0, 24, 25],
            [13, 14, 21, 22, 26],
            [21, 22, 26, 23, 3],
            [18, 19, 23, 22, 3],
            [16, 17, 24, 25, 20],
            [24, 25, 20, 26, 6],
            [25, 26, 6, 21, 22],
        ]
    )

    c2e_table = np.asarray(
        [
            [0, 1, 5],  # cell 0
            [3, 4, 8],  # cell 1
            [6, 7, 2],  # cell 2
            [1, 2, 9],  # cell 3
            [4, 5, 12],  # cell 4
            [7, 8, 15],  # cell 5
            [9, 10, 14],  # cell 6
            [12, 13, 17],  # cell 7
            [15, 16, 11],  # cell 8
            [10, 11, 18],  # cell 9
            [13, 14, 21],  # cell 10
            [16, 17, 24],  # cell 11
            [18, 19, 23],  # cell 12
            [21, 22, 26],  # cell 13
            [24, 25, 20],  # cell 14
            [19, 20, 0],  # cell 15
            [22, 23, 3],  # cell 16
            [25, 26, 6],  # cell 17
        ]
    )

    v2c_table = np.asarray(
        [
            [17, 14, 3, 0, 2, 15],
            [0, 4, 1, 12, 16, 15],
            [1, 5, 2, 16, 13, 17],
            [3, 6, 9, 5, 8, 2],
            [6, 10, 7, 4, 0, 3],
            [7, 11, 8, 5, 1, 4],
            [9, 12, 15, 8, 11, 14],
            [12, 16, 13, 10, 6, 9],
            [13, 17, 14, 11, 7, 10],
        ]
    )

    v2e_table = np.asarray(
        [
            [0, 1, 2, 6, 25, 20],
            [3, 4, 5, 0, 23, 19],
            [6, 7, 8, 3, 22, 26],
            [9, 10, 11, 15, 7, 2],
            [12, 13, 14, 9, 1, 5],
            [15, 16, 17, 12, 4, 8],
            [18, 19, 20, 24, 16, 11],
            [21, 22, 23, 18, 10, 14],
            [24, 25, 26, 21, 13, 17],
        ]
    )

    diamond_table = np.asarray(
        [
            [0, 1, 4, 6],  # 0
            [0, 4, 1, 3],
            [0, 3, 4, 2],
            [1, 2, 5, 7],  # 3
            [1, 5, 2, 4],
            [1, 4, 5, 0],
            [2, 0, 3, 8],  # 6
            [2, 3, 0, 5],
            [2, 5, 1, 3],
            [3, 4, 0, 7],  # 9
            [3, 7, 4, 6],
            [3, 6, 5, 7],
            [4, 5, 1, 8],  # 12
            [4, 8, 5, 7],
            [4, 7, 3, 8],
            [5, 3, 2, 6],  # 15
            [5, 6, 3, 8],
            [5, 8, 4, 6],
            [6, 7, 3, 1],  # 18
            [6, 1, 7, 0],
            [6, 0, 1, 8],
            [7, 8, 4, 2],  # 21
            [7, 2, 8, 1],
            [7, 1, 6, 2],
            [8, 6, 5, 0],  # 24
            [8, 0, 6, 2],
            [8, 2, 7, 0],
        ]
    )

    c2e2cO_table = np.asarray(
        [
            [15, 4, 3, 0],
            [16, 5, 4, 1],
            [17, 3, 5, 2],
            [0, 6, 2, 3],
            [1, 7, 0, 4],
            [2, 8, 1, 5],
            [3, 10, 9, 6],
            [4, 11, 10, 7],
            [5, 9, 11, 8],
            [6, 12, 8, 9],
            [7, 13, 6, 10],
            [8, 14, 7, 11],
            [9, 16, 15, 12],
            [10, 17, 16, 13],
            [11, 15, 17, 14],
            [12, 0, 14, 15],
            [13, 1, 12, 16],
            [14, 2, 13, 17],
        ]
    )

    c2e2c_table = np.asarray(
        [
            [15, 4, 3],
            [16, 5, 4],
            [17, 3, 5],
            [0, 6, 2],
            [1, 7, 0],
            [2, 8, 1],
            [3, 10, 9],
            [4, 11, 10],
            [5, 9, 11],
            [6, 12, 8],
            [7, 13, 6],
            [8, 14, 7],
            [9, 16, 15],
            [10, 17, 16],
            [11, 15, 17],
            [12, 0, 14],
            [13, 1, 12],
            [14, 2, 13],
        ]
    )
```

+++ {"tags": []}

# Excercises

## 1. point-wise (Christoph)

```{code-cell} ipython3

```

## 2. reduction: gradient or laplace (Christoph)

```{code-cell} ipython3

```

## 3. neighbor access without reduction (dusk weight) (Hannes - diff 5)

```{code-cell} ipython3

```

## 4. Scan Operator

Configuration: Single column

```{code-cell} ipython3
CellDim = Dimension("Cell")
KDim = Dimension("K", kind=DimensionKind.VERTICAL)

num_cells = 1
num_layers = 6
grid_shape = (num_cells, num_layers)
```

Task: Port the following numpy scheme to a `scan_operator` below:

```{code-cell} ipython3
def graupel_toy_numpy(qc, qr, autoconversion_rate=0.1, sedimentaion_constant=0.05):
    """A toy model of a microphysics scheme contaning autoconversion and scavenging"""

    #Init
    sedimentation_flux = 0.0

    for cell, k in np.ndindex(qc.shape):
        
        # Autoconversion: Cloud Drops -> Rain Drops
        
        ## Obtain autoconversion tendency
        autoconv_t = qc[cell, k] * autoconversion_rate
        
        ## Apply tendency in place
        qc[cell, k] -= autoconv_t
        qr[cell, k] += autoconv_t

        # Sedimentaion
        
        ## Apply sedimentation flux from level above
        qr[cell, k] += sedimentation_flux

        ## Scavenging due to strong precipitation flux
        if qr[cell, k - 1] >= 0.1:
            sedimentation_flux = sedimentaion_constant * qr[cell, k]
        else:
            sedimentation_flux = 0.0

        # Remove mass due to sedimentation flux
        qr[cell, k] -= sedimentation_flux
```

### Template

Caveats of the `scan_operator`:
- Optional arguents are not supported
- `If statments` are currently not supported, use `ternary operator` instead

```{code-cell} ipython3
@scan_operator(axis=KDim, forward=True, init=(0.0, 0.0, 0.0))
def _graupel_toy_scan(
    carry: tuple[float, float, float],
    qc_in: float,
    qr_in: float,
) -> tuple[float, float, float]:

    ### Implement here ###

    return qc, qr, sedimentation_flux
```

Embed the `scan_operator` in a `field_operator`, such that the sedimentation flux is treated as a temporary:

```{code-cell} ipython3
@field_operator
def graupel_toy_scan(qc: Field[[CellDim, KDim], float], qr: Field[[CellDim, KDim], float],
    ) -> tuple[Field[[CellDim, KDim], float], Field[[CellDim, KDim], float]]:
    
    qc, qr, _ = _graupel_toy_scan(qc, qr)

    return qc, qr
```

### Test

You can test your implementaion by executing the following test:

```{code-cell} ipython3
# Initialize GT4Py fields to zero
qc = np_as_located_field(CellDim, KDim)(np.full(shape=grid_shape, fill_value=1.0, dtype=np.float64))
qr = np_as_located_field(CellDim, KDim)(np.full(shape=grid_shape, fill_value=0.0, dtype=np.float64))

#Initialize Numpy fields from GT4Py fields
qc_numpy = np.asarray(qc).copy()
qr_numpy = np.asarray(qr).copy()

#Execute the Numpy version of scheme
graupel_toy_numpy(qc_numpy, qr_numpy)

#Execute the GT4Py version of scheme
graupel_toy_scan(qc, qr, out=(qc, qr), offset_provider={})

# Compare results
assert np.allclose(np.asarray(qc), qc_numpy)
assert np.allclose(np.asarray(qr), qr_numpy)

print("Test successful")
```