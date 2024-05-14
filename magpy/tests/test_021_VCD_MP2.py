import psi4
import magpy
import pytest
from ..data.molecules import *
import numpy as np
import os

np.set_printoptions(precision=10, linewidth=200, threshold=200, suppress=True)

#@pytest.mark.skip(reason="not ready")
def test_VCD_H2Dimer_STO3G():
    psi4.core.clean_options()
    psi4.set_memory('2 GB')
    psi4.set_output_file('output.dat', False)
    psi4.set_options({'scf_type': 'pk',
                      'e_convergence': 1e-13,
                      'd_convergence': 1e-13,
                      'r_convergence': 1e-13})

    psi4.set_options({'basis': 'STO-6G'})
    # CID/6-31G* optimized geometry from G09
    mol = psi4.geometry("""
    O       0.00000000          1.35909101         -0.103181170
    O       0.00000000         -1.35909101         -0.103181170
    H       1.53994623          1.68647251          0.825449361
    H      -1.53994623         -1.68647251          0.825449361
    symmetry c1
    units bohr
    noreorient
    no_com
    """)
    print(os.getcwd())
    num_procs = os.cpu_count()
    print_level = 1
    magpy.normal(mol, 'MP2', read_hessian=True, fcm_file="fcm_H2O2_CID_631Gd.txt", parallel=True, num_procs=num_procs)


@pytest.mark.skip(reason="not ready")
def test_VCD_H2O2_STO3G():
    psi4.core.clean_options()
    psi4.set_memory('2 GB')
    psi4.set_output_file('output.dat', False)
    psi4.set_options({'scf_type': 'pk',
                      'e_convergence': 1e-13,
                      'd_convergence': 1e-13,
                      'r_convergence': 1e-13})

    psi4.set_options({'basis': 'STO-3G'})
    # HF/STO-3G Optimized geometry from CFOUR
    mol = psi4.geometry("""
H -1.838051419951917   1.472647809969243   0.806472638463773
O -1.312852628446968  -0.129910361247786  -0.050815108044519
O  1.312852628446968   0.129910361247786  -0.050815108044519
H  1.838051419951917  -1.472647809969243   0.806472638463773
no_com
no_reorient
symmetry c1
units bohr
            """)

    magpy.normal(mol, 'CID', read_hessian=True, fcm_file="fcm_H2O2_CID_STO3G.txt")


@pytest.mark.skip(reason="not ready")
def test_VCD_H2O2_STO3G_KP():
    psi4.core.clean_options()
    psi4.set_memory('2 GB')
    psi4.set_output_file('output.dat', False)
    psi4.set_options({'scf_type': 'pk',
                      'e_convergence': 1e-13,
                      'd_convergence': 1e-13,
                      'r_convergence': 1e-13})

    psi4.set_options({'basis': 'STO-3G'})
    # 
    mol = psi4.geometry("""
O       0.0000000000        1.3192641900       -0.0952542913
O      -0.0000000000       -1.3192641900       -0.0952542913
H       1.6464858700        1.6841036400        0.7620343300
H      -1.6464858700       -1.6841036400        0.7620343300
no_com
no_reorient
symmetry c1
units bohr
            """)

    magpy.normal(mol, 'CID')
