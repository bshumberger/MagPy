if __name__ == "__main__":
    raise Exception("This file cannot be invoked on its own.")

import psi4
import magpy
import numpy as np
from .utils import *


class AAT(object):

    def __init__(self, molecule, charge=0, spin=1):

        # Ensure geometry remains fixed in space
        molecule.fix_orientation(True)
        molecule.fix_com(True)
        molecule.update_geometry()
        molecule.reinterpret_coordentry(False)
        self.molecule = molecule

        self.charge = charge
        self.spin = spin


    def compute(self, method='HF', R_disp=0.001, B_disp=0.001, **kwargs):

        valid_methods = ['HF', 'CID']
        method = method.upper()
        if method not in valid_methods:
            raise Exception(f"{method:s} is not an allowed choice of method.")

        valid_normalizations = ['FULL', 'INTERMEDIATE']
        normalization = kwargs.pop('normalization', 'FULL').upper()
        if normalization not in valid_normalizations:
            raise Exception(f"{normalization:s} is not an allowed choice of normalization.")

        valid_orbitals = ['SPIN', 'SPATIAL']
        orbitals = kwargs.pop('orbitals', 'SPATIAL').upper()
        if orbitals not in valid_orbitals:
            raise Exception(f"{orbitals:s} is not an allowed choice of orbital representation.")

        # Extract kwargs
        e_conv = kwargs.pop('e_conv', 1e-7)
        r_conv = kwargs.pop('r_conv', 1e-7)
        maxiter = kwargs.pop('maxiter', 100)
        max_diis = kwargs.pop('max_diis', 8)
        start_diis = kwargs.pop('start_diis', 1)
        print_level = kwargs.pop('print_level', 0)

        mol = self.molecule

        # Compute the unperturbed HF wfn
        H = magpy.Hamiltonian(mol)
        scf0 = magpy.hfwfn(H, self.charge, self.spin, self.print_level)
        scf0.solve(e_conv=e_conv, r_conv=r_conv, maxiter=maxiter, max_diis=max_diis, start_diis=start_diis)
        if self.print_level > 0:
            print("Psi4 SCF = ", self.run_psi4_scf(H.molecule))
        if method == 'CI':
            if orbitals == 'SPATIAL':
                ci0 = magpy.ciwfn(scf0, normalization=normalization)
            else
                ci0 = magpy.ciwfn_so(scf0, normalization=normalization)

        # Magnetic field displacements
        B_pos = []
        B_neg = []
        for B in range(3):
            strength = np.zeros(3)

            # +B displacement
            if self.print_level > 0:
                print("B(%d)+ Displacement" % (B))
            strength[B] = B_disp
            H = magpy.Hamiltonian(mol)
            H.add_field(field='magnetic-dipole', strength=strength)
            scf = magpy.hfwfn(H, self.charge, self.spin, self.print_level)
            scf.solve(e_conv=e_conv, r_conv=r_conv, maxiter=maxiter, max_diis=max_diis, start_diis=start_diis)
            scf.match_phase(scf0)
            if method == 'CI':
                if orbitals == 'SPATIAL':
                    ci = magpy.ciwfn(scf, normalization=normalization) 
                else
                    ci = magpy.ciwfn_so(scf, normalization=normalization) 
            ci.solve(e_conv=e_conv, r_conv=r_conv, maxiter=maxiter, max_diis=max_diis, start_diis=start_diis, print_level=print_level)
            B_pos.append(ci)

            # -B displacement
            if self.print_level > 0:
                print("B(%d)- Displacement" % (B))
            strength[B] = -B_disp
            H = magpy.Hamiltonian(mol)
            H.add_field(field='magnetic-dipole', strength=strength)
            scf = magpy.hfwfn(H, self.charge, self.spin, self.print_level)
            scf.solve(e_conv=e_conv, r_conv=r_conv, maxiter=maxiter, max_diis=max_diis, start_diis=start_diis)
            scf.match_phase(scf0)
            if method == 'CI':
                if orbitals == 'SPATIAL':
                    ci = magpy.ciwfn(scf, normalization=normalization) 
                else
                    ci = magpy.ciwfn_so(scf, normalization=normalization) 
            ci.solve(e_conv=e_conv, r_conv=r_conv, maxiter=maxiter, max_diis=max_diis, start_diis=start_diis, print_level=print_level)
            B_neg.append(ci)

        # Atomic coordinate displacements
        R_pos = []
        R_neg = []
        for R in range(3*mol.natom()):

            # +R displacement
            if self.print_level > 0:
                print("R(%d)+ Displacement" % (R))
            H = magpy.Hamiltonian(shift_geom(mol, R, R_disp))
            rhf_e, rhf_wfn = psi4.energy('SCF', return_wfn=True)
            scf = magpy.hfwfn(H, self.charge, self.spin, self.print_level)
            scf.solve(e_conv=e_conv, r_conv=r_conv, maxiter=maxiter, max_diis=max_diis, start_diis=start_diis)
            if self.print_level > 0:
                print("Psi4 SCF = ", self.run_psi4_scf(H.molecule))
            scf.match_phase(scf0)
            if method == 'CI':
                if orbitals == 'SPATIAL':
                    ci = magpy.ciwfn(scf, normalization=normalization) 
                else
                    ci = magpy.ciwfn_so(scf, normalization=normalization) 
            ci.solve(e_conv=e_conv, r_conv=r_conv, maxiter=maxiter, max_diis=max_diis, start_diis=start_diis, print_level=print_level)
            R_pos.append(ci)

            # -R displacement
            if self.print_level > 0:
                print("R(%d)- Displacement" % (R))
            H = magpy.Hamiltonian(shift_geom(mol, R, -R_disp))
            scf = magpy.hfwfn(H, self.charge, self.spin, self.print_level)
            scf.solve(e_conv=e_conv, r_conv=r_conv, maxiter=maxiter, max_diis=max_diis, start_diis=start_diis)
            if self.print_level > 0:
                print("Psi4 SCF = ", self.run_psi4_scf(H.molecule))
            scf.match_phase(scf0)
            if method == 'CI':
                if orbitals == 'SPATIAL':
                    ci = magpy.ciwfn(scf, normalization=normalization) 
                else
                    ci = magpy.ciwfn_so(scf, normalization=normalization) 
            ci.solve(e_conv=e_conv, r_conv=r_conv, maxiter=maxiter, max_diis=max_diis, start_diis=start_diis, print_level=print_level)
            R_neg.append(ci)

        # Compute full MO overlap matrix for all combinations of perturbed MOs
        S = [[[0 for k in range(4)] for j in range(3)] for i in range(3*mol.natom())] # list of overlap matrices
        for R in range(3*mol.natom()):
            if method == 'HF':
                R_pos_C = R_pos[R].C
                R_neg_C = R_neg[R].C
                R_pos_H = R_pos[R].H.basisset
                R_neg_H = R_neg[R].H.basisset
            else:
                R_pos_C = R_pos[R].hfwfn.C
                R_neg_C = R_neg[R].hfwfn.C
                R_pos_H = R_pos[R].hfwfn.H.basisset
                R_neg_H = R_neg[R].hfwfn.H.basisset

            for B in range(3):
                if method == 'HF':
                    B_pos_C = B_pos[B].C
                    B_neg_C = B_neg[B].C
                    B_pos_H = B_pos[B].H.basisset
                    B_neg_H = B_neg[B].H.basisset
                else:
                    B_pos_C = B_pos[B].hfwfn.C
                    B_neg_C = B_neg[B].hfwfn.C
                    B_pos_H = B_pos[B].hfwfn.H.basisset
                    B_neg_H = B_neg[B].hfwfn.H.basisset

                S[R][B][0] = self.mo_overlap(R_pos_C, R_pos_H, B_pos_C, B_pos_H)
                S[R][B][1] = self.mo_overlap(R_pos_C, R_pos_H, B_neg_C, B_neg_H)
                S[R][B][2] = self.mo_overlap(R_neg_C, R_neg_H, B_pos_C, B_pos_H)
                S[R][B][3] = self.mo_overlap(R_neg_C, R_neg_H, B_neg_C, B_neg_H)

        # Compute AAT components using finite-difference
        o = slice(0,scf0.ndocc)
        if method == 'CI':
            no = ci0.no
            nv = ci0.nv

        # <d0/dR|d0/dB>
        AAT_00 = np.zeros((3*mol.natom(), 3))
        for R in range(3*mol.natom()):
            if method == 'HF':
                C0_R_pos = C0_R_neg = 1.0
            else:
                C0_R_pos = R_pos[R].C0
                C0_R_neg = R_neg[R].C0

            for B in range(3):
                if method == 'HF':
                    C0_B_pos = C0_B_neg = 1.0
                else:
                    C0_B_pos = B_pos[B].C0
                    C0_B_neg = B_neg[B].C0

                if method == 'HF':
                    pp = np.linalg.det(S[R][B][0][o,o])
                    pm = np.linalg.det(S[R][B][1][o,o])
                    mp = np.linalg.det(S[R][B][2][o,o])
                    mm = np.linalg.det(S[R][B][3][o,o])
                    AAT_00[R,B] = 2*(((pp - pm - mp + mm)/(4*R_disp*B_disp))).imag
                else:
                    pp = self.det_overlap([0], 'AA', [0], 'AA', S[R][B][0], o) * C0_R_pos * C0_B_pos
                    pm = self.det_overlap([0], 'AA', [0], 'AA', S[R][B][1], o) * C0_R_pos * C0_B_neg
                    mp = self.det_overlap([0], 'AA', [0], 'AA', S[R][B][2], o) * C0_R_neg * C0_B_pos
                    mm = self.det_overlap([0], 'AA', [0], 'AA', S[R][B][3], o) * C0_R_neg * C0_B_neg
                    AAT_00[R,B] = (((pp - pm - mp + mm)/(4*R_disp*B_disp))).imag

        if method == 'HF':
            return AAT_00

        AAT_0D = np.zeros((3*mol.natom(), 3))
        AAT_D0 = np.zeros((3*mol.natom(), 3))
        for R in range(3*mol.natom()):
            ci_R_pos = R_pos[R]
            ci_R_neg = R_neg[R]

            for B in range(3):
                ci_B_pos = B_pos[B]
                ci_B_neg = B_neg[B]

                pp = pm = mp = mm = 0.0

                for i in range(no):
                    for a in range(nv):
                        for j in range(no):
                            for b in range(nv):

                                det_AA = self.det_overlap([0], 'AA', [i, a+no, j, b+no], 'AA', S[R][B][0], o)
                                det_AB = self.det_overlap([0], 'AB', [i, a+no, j, b+no], 'AB', S[R][B][0], o)
                                pp += (0.5 * (ci_B_pos.C2[i,j,a,b] - ci_B_pos.C2[i,j,b,a]) * det_AA + ci_B_pos.C2[i,j,a,b] * det_AB) * ci_R_pos.C0

                                det_AA = self.det_overlap([0], 'AA', [i, a+no, j, b+no], 'AA', S[R][B][1], o)
                                det_AB = self.det_overlap([0], 'AB', [i, a+no, j, b+no], 'AB', S[R][B][1], o)
                                pm += (0.5 * (ci_B_neg.C2[i,j,a,b] - ci_B_neg.C2[i,j,b,a]) * det_AA + ci_B_neg.C2[i,j,a,b] * det_AB) * ci_R_pos.C0

                                det_AA = self.det_overlap([0], 'AA', [i, a+no, j, b+no], 'AA', S[R][B][2], o)
                                det_AB = self.det_overlap([0], 'AB', [i, a+no, j, b+no], 'AB', S[R][B][2], o)
                                mp += (0.5 * (ci_B_pos.C2[i,j,a,b] - ci_B_pos.C2[i,j,b,a]) * det_AA + ci_B_pos.C2[i,j,a,b] * det_AB) * ci_R_neg.C0

                                det_AA = self.det_overlap([0], 'AA', [i, a+no, j, b+no], 'AA', S[R][B][3], o)
                                det_AB = self.det_overlap([0], 'AB', [i, a+no, j, b+no], 'AB', S[R][B][3], o)
                                mm += (0.5 * (ci_B_neg.C2[i,j,a,b] - ci_B_neg.C2[i,j,b,a]) * det_AA + ci_B_neg.C2[i,j,a,b] * det_AB) * ci_R_neg.C0

                AAT_0D[R,B] = (((pp - pm - mp + mm)/(4*R_disp*B_disp))).imag

                # <dD/dR|d0/dB>
                pp = pm = mp = mm = 0.0
                for i in range(no):
                    for a in range(nv):
                        for j in range(no):
                            for b in range(nv):

                                det_AA = self.det_overlap([i, a+no, j, b+no], 'AA', [0], 'AA', S[R][B][0], o)
                                det_AB = self.det_overlap([i, a+no, j, b+no], 'AB', [0], 'AB', S[R][B][0], o)
                                pp += (0.5 * (ci_R_pos.C2[i,j,a,b] - ci_R_pos.C2[i,j,b,a]) * det_AA + ci_R_pos.C2[i,j,a,b] * det_AB) * ci_B_pos.C0

                                det_AA = self.det_overlap([i, a+no, j, b+no], 'AA', [0], 'AA', S[R][B][1], o)
                                det_AB = self.det_overlap([i, a+no, j, b+no], 'AB', [0], 'AB', S[R][B][1], o)
                                pm += (0.5 * (ci_R_pos.C2[i,j,a,b] - ci_R_pos.C2[i,j,b,a]) * det_AA + ci_R_pos.C2[i,j,a,b] * det_AB) * ci_B_neg.C0

                                det_AA = self.det_overlap([i, a+no, j, b+no], 'AA', [0], 'AA', S[R][B][2], o)
                                det_AB = self.det_overlap([i, a+no, j, b+no], 'AB', [0], 'AB', S[R][B][2], o)
                                mp += (0.5 * (ci_R_neg.C2[i,j,a,b] - ci_R_neg.C2[i,j,b,a]) * det_AA + ci_R_neg.C2[i,j,a,b] * det_AB) * ci_B_pos.C0

                                det_AA = self.det_overlap([i, a+no, j, b+no], 'AA', [0], 'AA', S[R][B][3], o)
                                det_AB = self.det_overlap([i, a+no, j, b+no], 'AB', [0], 'AB', S[R][B][3], o)
                                mm += (0.5 * (ci_R_neg.C2[i,j,a,b] - ci_R_neg.C2[i,j,b,a]) * det_AA + ci_R_neg.C2[i,j,a,b] * det_AB) * ci_B_neg.C0

                AAT_D0[R,B] = (((pp - pm - mp + mm)/(4*R_disp*B_disp))).imag

        AAT_DD = np.zeros((3*mol.natom(), 3))
        for R in range(3*mol.natom()):
            ci_R_pos = R_pos[R]
            ci_R_neg = R_neg[R]

            for B in range(3):
                ci_B_pos = B_pos[B]
                ci_B_neg = B_neg[B]

                # <d0/dR|dD/dB>
                pp = pm = mp = mm = 0.0
                print(f"R = {R:2d}; B = {B:2d}")
                for i in range(no):
                    for a in range(nv):
                        for j in range(no):
                            for b in range(nv):
                                for k in range(no):
                                    for c in range(nv):
                                        for l in range(no):
                                            for d in range(nv):

                                                ci_R = ci_R_pos; ci_B = ci_B_pos; disp = 0
                                                det_AA_AA = self.det_overlap([i, a+no, j, b+no], 'AA', [k, c+no, l, d+no], 'AA', S[R][B][disp], o)
                                                det_AA_BB = self.det_overlap([i, a+no, j, b+no], 'AA', [k, c+no, l, d+no], 'BB', S[R][B][disp], o)
                                                det_AB_AB = self.det_overlap([i, a+no, j, b+no], 'AB', [k, c+no, l, d+no], 'AB', S[R][B][disp], o)
                                                det_AA_AB = self.det_overlap([i, a+no, j, b+no], 'AA', [k, c+no, l, d+no], 'AB', S[R][B][disp], o)
                                                det_AB_AA = self.det_overlap([i, a+no, j, b+no], 'AB', [k, c+no, l, d+no], 'AA', S[R][B][disp], o)
                                                pp += (1/8) * (ci_R.C2[i,j,a,b] - ci_R.C2[i,j,b,a]) * (ci_B.C2[k,l,c,d] - ci_B.C2[k,l,d,c]) *det_AA_AA
                                                pp += (1/8) * (ci_R.C2[i,j,a,b] - ci_R.C2[i,j,b,a]) * (ci_B.C2[k,l,c,d] - ci_B.C2[k,l,d,c]) *det_AA_BB
                                                pp += (1/2) * (ci_R.C2[i,j,a,b] - ci_R.C2[i,j,b,a]) * ci_B.C2[k,l,c,d] *det_AA_AB
                                                pp += (1/2) * ci_R.C2[i,j,a,b] * (ci_B.C2[k,l,c,d] - ci_B.C2[k,l,d,c]) *det_AB_AA
                                                pp += ci_R.C2[i,j,a,b] * ci_B.C2[k,l,c,d] *det_AB_AB

                                                ci_R = ci_R_pos; ci_B = ci_B_neg; disp = 1
                                                det_AA_AA = self.det_overlap([i, a+no, j, b+no], 'AA', [k, c+no, l, d+no], 'AA', S[R][B][disp], o)
                                                det_AA_BB = self.det_overlap([i, a+no, j, b+no], 'AA', [k, c+no, l, d+no], 'BB', S[R][B][disp], o)
                                                det_AB_AB = self.det_overlap([i, a+no, j, b+no], 'AB', [k, c+no, l, d+no], 'AB', S[R][B][disp], o)
                                                det_AA_AB = self.det_overlap([i, a+no, j, b+no], 'AA', [k, c+no, l, d+no], 'AB', S[R][B][disp], o)
                                                det_AB_AA = self.det_overlap([i, a+no, j, b+no], 'AB', [k, c+no, l, d+no], 'AA', S[R][B][disp], o)
                                                pm += (1/8) * (ci_R.C2[i,j,a,b] - ci_R.C2[i,j,b,a]) * (ci_B.C2[k,l,c,d] - ci_B.C2[k,l,d,c]) *det_AA_AA
                                                pp += (1/8) * (ci_R.C2[i,j,a,b] - ci_R.C2[i,j,b,a]) * (ci_B.C2[k,l,c,d] - ci_B.C2[k,l,d,c]) *det_AA_BB
                                                pm += (1/2) * (ci_R.C2[i,j,a,b] - ci_R.C2[i,j,b,a]) * ci_B.C2[k,l,c,d] *det_AA_AB
                                                pm += (1/2) * ci_R.C2[i,j,a,b] * (ci_B.C2[k,l,c,d] - ci_B.C2[k,l,d,c]) *det_AB_AA
                                                pm += ci_R.C2[i,j,a,b] * ci_B.C2[k,l,c,d] *det_AB_AB

                                                ci_R = ci_R_neg; ci_B = ci_B_pos; disp = 2
                                                det_AA_AA = self.det_overlap([i, a+no, j, b+no], 'AA', [k, c+no, l, d+no], 'AA', S[R][B][disp], o)
                                                det_AA_BB = self.det_overlap([i, a+no, j, b+no], 'AA', [k, c+no, l, d+no], 'BB', S[R][B][disp], o)
                                                det_AB_AB = self.det_overlap([i, a+no, j, b+no], 'AB', [k, c+no, l, d+no], 'AB', S[R][B][disp], o)
                                                det_AA_AB = self.det_overlap([i, a+no, j, b+no], 'AA', [k, c+no, l, d+no], 'AB', S[R][B][disp], o)
                                                det_AB_AA = self.det_overlap([i, a+no, j, b+no], 'AB', [k, c+no, l, d+no], 'AA', S[R][B][disp], o)
                                                mp += (1/8) * (ci_R.C2[i,j,a,b] - ci_R.C2[i,j,b,a]) * (ci_B.C2[k,l,c,d] - ci_B.C2[k,l,d,c]) *det_AA_AA
                                                pp += (1/8) * (ci_R.C2[i,j,a,b] - ci_R.C2[i,j,b,a]) * (ci_B.C2[k,l,c,d] - ci_B.C2[k,l,d,c]) *det_AA_BB
                                                mp += (1/2) * (ci_R.C2[i,j,a,b] - ci_R.C2[i,j,b,a]) * ci_B.C2[k,l,c,d] *det_AA_AB
                                                mp += (1/2) * ci_R.C2[i,j,a,b] * (ci_B.C2[k,l,c,d] - ci_B.C2[k,l,d,c]) *det_AB_AA
                                                mp += ci_R.C2[i,j,a,b] * ci_B.C2[k,l,c,d] *det_AB_AB

                                                ci_R = ci_R_neg; ci_B = ci_B_neg; disp = 3
                                                det_AA_AA = self.det_overlap([i, a+no, j, b+no], 'AA', [k, c+no, l, d+no], 'AA', S[R][B][disp], o)
                                                det_AA_BB = self.det_overlap([i, a+no, j, b+no], 'AA', [k, c+no, l, d+no], 'BB', S[R][B][disp], o)
                                                det_AB_AB = self.det_overlap([i, a+no, j, b+no], 'AB', [k, c+no, l, d+no], 'AB', S[R][B][disp], o)
                                                det_AA_AB = self.det_overlap([i, a+no, j, b+no], 'AA', [k, c+no, l, d+no], 'AB', S[R][B][disp], o)
                                                det_AB_AA = self.det_overlap([i, a+no, j, b+no], 'AB', [k, c+no, l, d+no], 'AA', S[R][B][disp], o)
                                                mm += (1/8) * (ci_R.C2[i,j,a,b] - ci_R.C2[i,j,b,a]) * (ci_B.C2[k,l,c,d] - ci_B.C2[k,l,d,c]) *det_AA_AA
                                                pp += (1/8) * (ci_R.C2[i,j,a,b] - ci_R.C2[i,j,b,a]) * (ci_B.C2[k,l,c,d] - ci_B.C2[k,l,d,c]) *det_AA_BB
                                                mm += (1/2) * (ci_R.C2[i,j,a,b] - ci_R.C2[i,j,b,a]) * ci_B.C2[k,l,c,d] *det_AA_AB
                                                mm += (1/2) * ci_R.C2[i,j,a,b] * (ci_B.C2[k,l,c,d] - ci_B.C2[k,l,d,c]) *det_AB_AA
                                                mm += ci_R.C2[i,j,a,b] * ci_B.C2[k,l,c,d] *det_AB_AB

                AAT_DD[R,B] = (((pp - pm - mp + mm)/(4*R_disp*B_disp))).imag

        return AAT_00, AAT_0D, AAT_D0, AAT_DD

    def mo_overlap(self, bra, bra_basis, ket, ket_basis):
        """
        Compute the MO overlap matrix between two (possibly different) basis sets

        Parameters
        ----------
        bra: MO coefficient matrix for the bra state (NumPy array)
        bra_basis: Psi4 BasisSet object for the bra state
        ket: MO coefficient matrix for the ket state (NumPy array)
        ket_basis: Psi4 BasisSet object for the ket state

        Returns
        -------
        S: MO-basis overlap matrix (NumPy array)
        """
        # Sanity check
        if (bra.shape[0] != ket.shape[0]) or (bra.shape[1] != ket.shape[1]):
            raise Exception("Bra and Ket States do not have the same dimensions: (%d,%d) vs. (%d,%d)." %
                    (bra.shape[0], bra.shape[1], ket.shape[0], ket.shape[1]))

        # Get AO-basis overlap integrals
        mints = psi4.core.MintsHelper(bra_basis)
        if bra_basis == ket_basis:
            S_ao = mints.ao_overlap().np
        else:
            S_ao = mints.ao_overlap(bra_basis, ket_basis).np

        # Transform to MO basis
        S_mo = bra.T @ S_ao @ ket

        # Convert to spin orbitals
        if self.orbitals == 'SPIN':
            n = 2 * bra.shape[1]
            S = np.zeros((n,n), dtype=S_mo.dtype)
            for p in range(n):
                for q in range(n):
                    S[p,q] = S_mo[p//2,q//2] * (p%2 == q%2)
            return S
        else:
             return S_mo



    # Compute overlap between two determinants in (possibly) different bases
    def det_overlap(self, bra_indices, ket_indices, S, o, spins='AAAA'):
        """
        Compute the overlap between two Slater determinants (represented by strings of indices)
        of equal length in (possibly) different basis sets using the determinant of their overlap.

        Parameters
        ----------
        bra_indices: list of substitution indices
        ket_indices: list of substitution indices
        S: MO overlap between bra and ket bases (NumPy array)
        o: Slice of S needed for determinant
        spins: 'AAAA', 'AAAB', 'ABAA', or 'ABAB' (string)
        """

        if orbitals == 'SPIN':
            S = S.copy()

            if len(bra_indices) == 4: # double excitation
                i = bra_indices[0]; a = bra_indices[1]
                j = bra_indices[2]; b = bra_indices[3]
                S[[a,i],:] = S[[i,a],:]
                S[[b,j],:] = S[[j,b],:]

            if len(ket_indices) == 4: # double excitation
                i = ket_indices[0]; a = ket_indices[1]
                j = ket_indices[2]; b = ket_indices[3]
                S[:,[a,i]] = S[:,[i,a]]
                S[:,[b,j]] = S[:,[j,b]]

            return np.linalg.det(S[o,o])
        else:
            S_alpha = S.copy()
            S_beta = S.copy()

            if len(spins) != 4:
                raise Exception("spins must be of length 4: {len(spins):d")

            bra_spin = spins[0] + spins[1]
            key_spin = spins[2] + spins[3]

            if len(bra_indices) == 4: # double excitation
                i = bra_indices[0]; a = bra_indices[1]
                j = bra_indices[2]; b = bra_indices[3]
                if bra_spin == 'AA':
                    S_alpha[[a,i],:] = S_alpha[[i,a],:]
                    S_alpha[[b,j],:] = S_alpha[[j,b],:]
                elif bra_spin == 'AB':
                    S_alpha[[a,i],:] = S_alpha[[i,a],:]
                    S_beta[[b,j],:] = S_beta[[j,b],:]

            if len(ket_indices) == 4: # double excitation
                i = ket_indices[0]; a = ket_indices[1]
                j = ket_indices[2]; b = ket_indices[3]
                if ket_spin == 'AA':
                    S_alpha[:,[a,i]] = S_alpha[:,[i,a]]
                    S_alpha[:,[b,j]] = S_alpha[:,[j,b]]
                elif ket_spin == 'AB':
                    S_alpha[:,[a,i]] = S_alpha[:,[i,a]]
                    S_beta[:,[b,j]] = S_beta[:,[j,b]]

            return np.linalg.det(S_alpha[o,o])*np.linalg.det(S_beta[o,o])

    def AAT_0D(ci_R_pos, ci_R_neg, ci_B_pos, ci_B_neg, orbitals):
        no = ci_R_pos.no
        no = ci_R_pos.nv

        for i in range(no):
            for a in range(nv):
                for j in range(no):
                    for b in range(nv):

                                det_AA = self.det_overlap([0], 'AA', [i, a+no, j, b+no], 'AA', S[R][B][0], o)
                                det_AB = self.det_overlap([0], 'AB', [i, a+no, j, b+no], 'AB', S[R][B][0], o)
                                pp += (0.5 * (ci_B_pos.C2[i,j,a,b] - ci_B_pos.C2[i,j,b,a]) * det_AA + ci_B_pos.C2[i,j,a,b] * det_AB) * ci_R_pos.C0

                                det_AA = self.det_overlap([0], 'AA', [i, a+no, j, b+no], 'AA', S[R][B][1], o)
                                det_AB = self.det_overlap([0], 'AB', [i, a+no, j, b+no], 'AB', S[R][B][1], o)
                                pm += (0.5 * (ci_B_neg.C2[i,j,a,b] - ci_B_neg.C2[i,j,b,a]) * det_AA + ci_B_neg.C2[i,j,a,b] * det_AB) * ci_R_pos.C0

                                det_AA = self.det_overlap([0], 'AA', [i, a+no, j, b+no], 'AA', S[R][B][2], o)
                                det_AB = self.det_overlap([0], 'AB', [i, a+no, j, b+no], 'AB', S[R][B][2], o)
                                mp += (0.5 * (ci_B_pos.C2[i,j,a,b] - ci_B_pos.C2[i,j,b,a]) * det_AA + ci_B_pos.C2[i,j,a,b] * det_AB) * ci_R_neg.C0

                                det_AA = self.det_overlap([0], 'AA', [i, a+no, j, b+no], 'AA', S[R][B][3], o)
                                det_AB = self.det_overlap([0], 'AB', [i, a+no, j, b+no], 'AB', S[R][B][3], o)
                                mm += (0.5 * (ci_B_neg.C2[i,j,a,b] - ci_B_neg.C2[i,j,b,a]) * det_AA + ci_B_neg.C2[i,j,a,b] * det_AB) * ci_R_neg.C0

    def run_psi4_scf(self, molecule):
        geom = molecule.create_psi4_string_from_molecule()
        new_mol = psi4.geometry(geom)
        new_mol.fix_orientation(True)
        new_mol.fix_com(True)
        new_mol.update_geometry()

        return psi4.energy('SCF')

