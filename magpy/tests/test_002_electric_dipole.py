"""
Test calculation of permanent dipole moment by finite-field method for comparison to Psi4
"""

import psi4
import magpy
import pytest
from ..data.molecules import *
#from .hamiltonian import Hamiltonian
#from .hfwfn import hfwfn
import numpy as np

# Test on HF molecule
def test_ccsd_hf():
    psi4.core.clean_options()
    psi4.set_memory('2 GB')
    psi4.set_output_file('output.dat', False)
    psi4.set_options({'basis': 'cc-pVDZ',
                      'scf_type': 'pk',
                      'e_convergence': 1e-12,
                      'd_convergence': 1e-12,
                      'r_convergence': 1e-12})

    hf = """
    0 1
    F   0.00  0.00 -0.095196019672231
    H   0.00  0.00  1.794530105785769
    units bohr
    no_reorient
    nocom
    symmetry c1
    """
    mol = psi4.geometry(hf)

    # Get MagPy energies and dipole moment
    H = magpy.Hamiltonian(mol)
    scf = magpy.hfwfn(H)
    escf, C = scf.solve(e_conv=1e-13, r_conv=1e-13)

    A = 0.0001
    H.add_field(field='electric-dipole', strength=np.array([0.0, 0.0, A]))
    escf_pos, C_pos = scf.solve(e_conv=1e-13, r_conv=1e-13)

    H.reset_V()
    H.add_field(field='electric-dipole', strength=np.array([0.0, 0.0, -A]))
    escf_neg, C_neg = scf.solve(e_conv=1e-13, r_conv=1e-13)

    mu = -(escf_pos - escf_neg)/(2 * A)

    print("ESCF(0)     = %20.12f" % (escf))
    print("ESCF(+A)    = %20.12f" % (escf_pos))
    print("ESCF(-A)    = %20.12f" % (escf_neg))
    print("Mu(z)       = %20.12f" % (mu))

    ## Grab Psi4 energies and dipole moment for testing
    A = 0.0001
    eps = [0.0, -A, +A]
    psi4_energies = []
    for l in eps:
        psi4.set_options({'perturb_h': True,
                          'perturb_with': 'dipole',
                          'perturb_dipole': [0.0, 0.0, l]})
        psi4_energies.append(psi4.energy('SCF', return_wfn=False))

    psi4_mu = -(psi4_energies[1] - psi4_energies[2])/(2 * A)

    print("Psi4 ESCF(0)     = %20.12f" % (psi4_energies[0]))
    print("Psi4 ESCF(+A)    = %20.12f" % (psi4_energies[1]))
    print("Psi4 ESCF(-A)    = %20.12f" % (psi4_energies[2]))
    print("Psi4 Mu(z)       = %20.12f" % (psi4_mu))

    assert (abs(psi4_energies[0] - escf) < 1e-11)
    assert (abs(psi4_energies[1] - escf_pos) < 1e-11)
    assert (abs(psi4_energies[2] - escf_neg) < 1e-11)
    assert (abs(psi4_mu - mu) < 1e-7)

