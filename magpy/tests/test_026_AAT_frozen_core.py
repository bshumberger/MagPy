import psi4
import magpy
import pytest
from ..data.molecules import *
import numpy as np
import os
from ..utils import make_np_array

np.set_printoptions(precision=15, linewidth=200, threshold=200, suppress=True)

def test_AAT_MP2_H2O():
    psi4.core.clean_options()
    psi4.set_memory('2 GB')
    psi4.set_output_file('output.dat', False)
    psi4.set_options({'scf_type': 'pk',
                      'e_convergence': 1e-12,
                      'd_convergence': 1e-12,
                      'r_convergence': 1e-12})

    psi4.set_options({'basis': 'STO-6G'})
    psi4.set_options({'freeze_core': 'true'})
    mol = psi4.geometry(moldict["H2O"])
    rhf_e, rhf_wfn = psi4.energy('SCF', return_wfn=True)
    print(f"  SCF Energy from Psi4: {rhf_e}")

    AAT = magpy.AAT(mol, 0, 1)
    I_00, I_0D, I_D0, I_DD = AAT.compute('MP2', print_level=1, parallel=True, num_proc=os.cpu_count())
    print("\nElectronic Contribution to Atomic Axial Tensor (a.u.):")
    print("Hartree-Fock component:")
    print(I_00)
    print("<0|D> Component\n")
    print(I_0D)
    print("<D|0> Component\n")
    print(I_D0)
    print("<0|D>+<D|0>\n")
    print(I_0D+I_D0)
    print("<D|D> Component\n")
    print(I_DD)

    return

    I_00_ref = make_np_array("""
 """)

    I_0D_ref = make_np_array("""
 """)

    I_D0_ref = make_np_array("""
 """)

    I_DD_ref = make_np_array("""
 """)

    assert(np.max(np.abs(I_00_ref-I_00)) < 1e-9)
    assert(np.max(np.abs(I_0D_ref-I_0D)) < 1e-9)
    assert(np.max(np.abs(I_D0_ref-I_D0)) < 1e-9)
    assert(np.max(np.abs(I_DD_ref-I_DD)) < 1e-9)


def test_AAT_CID_H2O():
    psi4.core.clean_options()
    psi4.set_memory('2 GB')
    psi4.set_output_file('output.dat', False)
    psi4.set_options({'scf_type': 'pk',
                      'e_convergence': 1e-12,
                      'd_convergence': 1e-12,
                      'r_convergence': 1e-12})

    psi4.set_options({'basis': 'STO-6G'})
    psi4.set_options({'freeze_core': 'true'})
    mol = psi4.geometry(moldict["H2O"])
    rhf_e, rhf_wfn = psi4.energy('SCF', return_wfn=True)
    print(f"  SCF Energy from Psi4: {rhf_e}")

    AAT = magpy.AAT(mol, 0, 1)
    I_00, I_0D, I_D0, I_DD = AAT.compute('CID', print_level=1, parallel=True, num_proc=os.cpu_count())
    print("\nElectronic Contribution to Atomic Axial Tensor (a.u.):")
    print("Hartree-Fock component:")
    print(I_00)
    print("<0|D> Component\n")
    print(I_0D)
    print("<D|0> Component\n")
    print(I_D0)
    print("<0|D>+<D|0>\n")
    print(I_0D+I_D0)
    print("<D|D> Component\n")
    print(I_DD)

    return

    I_00_ref = make_np_array("""
 """)

    I_0D_ref = make_np_array("""
 """)

    I_D0_ref = make_np_array("""
 """)

    I_DD_ref = make_np_array("""
 """)

    assert(np.max(np.abs(I_00_ref-I_00)) < 1e-9)
    assert(np.max(np.abs(I_0D_ref-I_0D)) < 1e-9)
    assert(np.max(np.abs(I_D0_ref-I_D0)) < 1e-9)
    assert(np.max(np.abs(I_DD_ref-I_DD)) < 1e-9)


