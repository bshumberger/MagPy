import psi4
import magpy
import pytest
from ..data.molecules import *
import numpy as np
import os

np.set_printoptions(precision=10, linewidth=200, threshold=200, suppress=True)

def test_Hessian_H2O_STO3G():
    psi4.core.clean_options()
    psi4.set_memory('2 GB')
    psi4.set_output_file('output.dat', False)
    psi4.set_options({'scf_type': 'pk',
                      'e_convergence': 1e-13,
                      'd_convergence': 1e-13,
                      'r_convergence': 1e-13})

    psi4.set_options({'basis': 'STO-3G'})
    # CFOUR CID/STO-3G optimized geometry
    mol = psi4.geometry("""
O  0.000000000000000  -0.000000000000000   0.143954618947726
H  0.000000000000000  -1.450386234357036  -1.142332131421532
H  0.000000000000000   1.450386234357036  -1.142332131421532
no_com
no_reorient
symmetry c1
units bohr
            """)

    hessian = magpy.Hessian(mol)
    disp = 0.001
    e_conv = 1e-13
    r_conv = 1e-13
    maxiter = 400
    max_diis=8
    start_diis=1
    print_level=1
    hess = hessian.compute('CID', disp, e_conv=e_conv, r_conv=r_conv, maxiter=maxiter, max_diis=max_diis, start_diis=start_diis, print_level=print_level)

    # CFOUR CID/STO-3G finite-difference Hessian
    hess_ref = np.array([
     [  0.0000000000,        0.0000003053,        0.0000002035],
     [ -0.0000002699,       -0.0000003146,        0.0000003301],
     [  0.0000002699,        0.0000000000,       -0.0000005337],
     [  0.0000003053,        0.5894600186,        0.0000004070],
     [ -0.0000004766,       -0.2947303332,       -0.2613836255],
     [  0.0000001713,       -0.2947296854,        0.2613832185],
     [  0.0000002035,        0.0000004070,        0.5172143285],
     [ -0.0000004257,       -0.1557235360,       -0.2586071103],
     [  0.0000002222,        0.1557231290,       -0.2586072182],
     [ -0.0000002699,       -0.0000004766,       -0.0000004257],
     [  0.0000006710,        0.0000001760,       -0.0000001463],
     [ -0.0000004010,        0.0000003005,        0.0000005720],
     [ -0.0000003146,       -0.2947303332,       -0.1557235360],
     [  0.0000001760,        0.3327798576,        0.2085535363],
     [  0.0000001386,       -0.0380495244,       -0.0528300003],
     [  0.0000003301,       -0.2613836255,       -0.2586071103],
     [ -0.0000001463,        0.2085535363,        0.2452085405],
     [ -0.0000001838,        0.0528300892,        0.0133985698],
     [  0.0000002699,        0.0000001713,        0.0000002222],
     [ -0.0000004010,        0.0000001386,       -0.0000001838],
     [  0.0000001311,       -0.0000003098,       -0.0000000384],
     [  0.0000000000,       -0.2947296854,        0.1557231290],
     [  0.0000003005,       -0.0380495244,        0.0528300892],
     [ -0.0000003098,        0.3327792098,       -0.2085532182],
     [ -0.0000005337,        0.2613832185,       -0.2586072182],
     [  0.0000005720,       -0.0528300003,        0.0133985698],
     [ -0.0000000384,       -0.2085532182,        0.2452086484],
    ])

    assert(np.max(np.abs(hess-hess_ref.reshape(9,9))) < 1e-5)

