MagPy
==============================
[//]: # (Badges)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![GitHub Actions Build Status](https://github.com/CrawfordGroup/MagPy/workflows/CI/badge.svg)](https://github.com/CrawfordGroup/magpy/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/CrawfordGroup/MagPy/graph/badge.svg?token=SN87ODLNBW)](https://codecov.io/gh/CrawfordGroup/MagPy)

A Python reference implementation for including explicit magnetic fields in quantum chemical
calculations. Current capabilities include:
  - Complex Hartree-Fock (HF), Second-Order Møller-Plesset (MP2), and Configuration Interaction Doubles (CID)
  - Atomic axial tensors via numerical derivatives of wave functions
  - Vibrational Circular Dichroism spectra for (very) small molecules using HF, MP2 and CID wave functions

This repository is currently under development. To do a developmental install, download this repository and type `pip install -e .` in the repository directory.

This package requires the following:
  - [psi4](https://psicode.org)
  - [numpy](https://numpy.org/)
  - [opt_einsum](https://optimized-einsum.readthedocs.io/en/stable/)
  - [codetiming](https://pypi.org/project/codetiming/)

### Copyright

Copyright (c) 2024, T. Daniel Crawford


#### Acknowledgements

Project structure based on the
[MolSSI's](https://molssi.org) [Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms)
version 1.1.
