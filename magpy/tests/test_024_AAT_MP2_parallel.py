import psi4
import magpy
import pytest
from ..data.molecules import *
import numpy as np
import os
from ..utils import make_np_array

np.set_printoptions(precision=15, linewidth=200, threshold=200, suppress=True)

def test_AAT_MP2_H2DIMER():
    psi4.core.clean_options()
    psi4.set_memory('2 GB')
    psi4.set_output_file('output.dat', False)
    psi4.set_options({'scf_type': 'pk',
                      'e_convergence': 1e-13,
                      'd_convergence': 1e-13,
                      'r_convergence': 1e-13})

    psi4.set_options({'basis': 'STO-6G'})
    mol = psi4.geometry(moldict["(H2)_2"])
    rhf_e, rhf_wfn = psi4.energy('SCF', return_wfn=True)
    print(f"  SCF Energy from Psi4: {rhf_e}")

    AAT = magpy.AAT(mol, 0, 1)

    r_disp = 0.0001
    b_disp = 0.0001
    e_conv = 1e-12
    r_conv = 1e-12
    I_00, I_0D, I_D0, I_DD = AAT.compute('MP2', r_disp, b_disp, e_conv=e_conv, r_conv=r_conv, normalization='intermediate', parallel=True)
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

    I_00_ref = make_np_array("""
[[-0.097856900360615 -0.024464664951138  0.069232106541966]
 [ 0.024686227422983  0.005879922586945 -0.003819266089423]
 [-0.209265694313652 -0.051803561259253  0.093935959595289]
 [-0.088710310616063 -0.022263494739757  0.060278744166398]
 [-0.016456264690831 -0.004056816513517  0.020292183723423]
 [-0.215140025600313 -0.05317143139671   0.089029423759874]
 [-0.088710310631667 -0.022263494743767 -0.060278744172876]
 [-0.016456264697269 -0.004056816515104 -0.020292184243793]
 [ 0.215140025582485  0.053171431392279  0.089029423753599]
 [-0.097856900385283 -0.02446466495731  -0.069232106543105]
 [ 0.024686227444831  0.005879922592439  0.00381926608413 ]
 [ 0.209265694510914  0.051803561307904  0.093935959578609]]
 """)

    I_0D_ref = make_np_array("""
[[ 0.006808740805464  0.001695403965524 -0.005130119220599]
 [-0.000871959182927 -0.00021540761311  -0.000115195855897]
 [ 0.013071058381498  0.003251728200012 -0.008080999183209]
 [ 0.006420223678521  0.001599163975967 -0.004808528656272]
 [ 0.00097884078409   0.00024339858343  -0.00054627260451 ]
 [ 0.013187776617029  0.003280199759361 -0.007966306041871]
 [ 0.006420223679836  0.001599163976289  0.004808528656924]
 [ 0.000978840784731  0.0002433985836    0.000546272620396]
 [-0.013187776615873 -0.003280199759082 -0.007966306041163]
 [ 0.006808740806848  0.001695403965874  0.005130119220869]
 [-0.000871959184344 -0.000215407613452  0.000115195856348]
 [-0.013071058393264 -0.003251728202942 -0.008080999183206]]
 """)

    I_D0_ref = make_np_array("""
[[-0.006808740892117 -0.001695403973672  0.005130119233505]
 [ 0.0008719591981    0.000215407614326  0.000115195854473]
 [-0.013071058531117 -0.003251728212792  0.008080999226863]
 [-0.006420223760504 -0.001599163986204  0.004808528668143]
 [-0.000978840803084 -0.000243398587652  0.000546272606263]
 [-0.01318777676535  -0.003280199772866  0.007966306084481]
 [-0.006420223761249 -0.001599163986388 -0.004808528668831]
 [-0.000978840803297 -0.000243398587705 -0.000546272622777]
 [ 0.013187776763665  0.003280199772445  0.007966306084511]
 [-0.006808740893785 -0.001695403974086 -0.005130119232304]
 [ 0.000871959199832  0.000215407614753 -0.000115195854557]
 [ 0.013071058542963  0.003251728215738  0.008080999227038]]
 """)

    I_DD_ref = make_np_array("""
[[ 0.000030731202513  0.000025700510925 -0.000056151104364]
 [-0.000014926915508 -0.000001173748787 -0.000005567152441]
 [ 0.000200327181323  0.000027280454078 -0.000071478160397]
 [ 0.000006267830815 -0.000012114425716  0.000026462669104]
 [ 0.000055984628475 -0.00000823375262  -0.000005967671436]
 [ 0.000036781365687  0.000042606324025  0.00004963055636 ]
 [ 0.000006267830783 -0.000012114425726 -0.000026462669094]
 [ 0.00005598462845  -0.000008233752626  0.000005967681539]
 [-0.00003678136564  -0.000042606324015  0.00004963055628 ]
 [ 0.000030731202553  0.00002570051094   0.000056151104244]
 [-0.000014926915547 -0.000001173748799  0.000005567152414]
 [-0.000200327181475 -0.000027280454112 -0.000071478160437]]
""")

    assert(np.max(np.abs(I_00_ref-I_00)) < 1e-9)
    assert(np.max(np.abs(I_0D_ref-I_0D)) < 1e-9)
    assert(np.max(np.abs(I_D0_ref-I_D0)) < 1e-9)
    assert(np.max(np.abs(I_DD_ref-I_DD)) < 1e-9)

def test_AAT_MP2_H2DIMER_NORM():
    psi4.core.clean_options()
    psi4.set_memory('2 GB')
    psi4.set_output_file('output.dat', False)
    psi4.set_options({'scf_type': 'pk',
                      'e_convergence': 1e-13,
                      'd_convergence': 1e-13,
                      'r_convergence': 1e-13})

    psi4.set_options({'basis': 'STO-6G'})
    mol = psi4.geometry(moldict["(H2)_2"])
    rhf_e, rhf_wfn = psi4.energy('SCF', return_wfn=True)
    print(f"  SCF Energy from Psi4: {rhf_e}")

    AAT = magpy.AAT(mol, 0, 1)

    r_disp = 0.0001
    b_disp = 0.0001
    e_conv = 1e-12
    r_conv = 1e-12
    I_00, I_0D, I_D0, I_DD = AAT.compute('MP2', r_disp, b_disp, e_conv=e_conv, r_conv=r_conv, normalization='full', parallel=True)

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

    I_00_ref = make_np_array("""
[[-0.096723351176647 -0.024181272559026  0.068430139624694]
 [ 0.02440026853828   0.005811811081961 -0.00377502469012 ]
 [-0.206841614525112 -0.05120348217461   0.092847829558901]
 [-0.087682713190163 -0.022005600141307  0.059580490685184]
 [-0.016265639556674 -0.004009823395063  0.02005712427525 ]
 [-0.212647898835307 -0.052555507198603  0.087998129804366]
 [-0.087682713189233 -0.022005600140938 -0.059580490681089]
 [-0.016265639573135 -0.004009823398961 -0.02005712428386 ]
 [ 0.212647898839365  0.052555507199591  0.087998129794764]
 [-0.096723351213789 -0.024181272568481 -0.068430139622883]
 [ 0.024400268460648  0.005811811062735  0.003775024581204]
 [ 0.206841614521018  0.051203482173443  0.092847829566123]]
 """)

    I_0D_ref = make_np_array("""
[[ 0.006729870102103  0.001675764841709 -0.005070693238922]
 [-0.000861858633735 -0.000212912387148 -0.000113861456894]
 [ 0.012919646614914  0.003214061019705 -0.007987390964472]
 [ 0.006345853458475  0.001580639671651 -0.004752827896155]
 [ 0.000967502144395  0.000240579116881 -0.000539944722178]
 [ 0.013035012801975  0.003242202768246 -0.00787402640068 ]
 [ 0.006345853458529  0.001580639671666  0.004752827895969]
 [ 0.000967502145657  0.000240579117194  0.000539944722927]
 [-0.013035012802303 -0.003242202768324 -0.007874026399958]
 [ 0.006729870104109  0.001675764842218  0.005070693238991]
 [-0.000861858628602 -0.000212912385862  0.000113861470701]
 [-0.012919646614301 -0.003214061019542 -0.007987390965115]]
 """)

    I_D0_ref = make_np_array("""
[[-0.006729870187304 -0.001675764849652  0.005070693251512]
 [ 0.000861858648603  0.000212912388307  0.000113861455361]
 [-0.012919646761546 -0.003214061032019  0.007987391007058]
 [-0.006345853539045 -0.001580639681657  0.004752827907825]
 [-0.000967502162469 -0.000240579120877  0.000539944723795]
 [-0.013035012947752 -0.003242202781376  0.007874026442289]
 [-0.006345853537955 -0.001580639681385 -0.004752827907489]
 [-0.000967502164103 -0.000240579121288 -0.000539944725327]
 [ 0.013035012947641  0.00324220278135   0.00787402644207 ]
 [-0.00672987018937  -0.001675764850167 -0.005070693250025]
 [ 0.000861858644177  0.000212912387211 -0.000113861468837]
 [ 0.012919646761641  0.003214061032042  0.007987391007655]]
 """)

    I_DD_ref = make_np_array("""
[[ 0.000030375220123  0.000025402802803 -0.000055133014035]
 [-0.000014754005958 -0.000001160152387 -0.000005441973293]
 [ 0.000198006642816  0.00002696444432  -0.000069951395404]
 [ 0.000006195225855 -0.000011974095329  0.000025758136646]
 [ 0.000055336116895 -0.000008138374957 -0.00000586253615 ]
 [ 0.000036355299728  0.000042112783301  0.000048356868496]
 [ 0.000006195225771 -0.000011974095351 -0.000025758136644]
 [ 0.000055336116907 -0.000008138374951  0.000005862536224]
 [-0.0000363552997   -0.000042112783298  0.000048356868446]
 [ 0.000030375220166  0.000025402802814  0.000055133013892]
 [-0.000014754005978 -0.000001160152386  0.000005441973575]
 [-0.000198006642872 -0.000026964444336 -0.000069951395413]]
 """)

    assert(np.max(np.abs(I_00_ref-I_00)) < 1e-9)
    assert(np.max(np.abs(I_0D_ref-I_0D)) < 1e-9)
    assert(np.max(np.abs(I_D0_ref-I_D0)) < 1e-9)
    assert(np.max(np.abs(I_DD_ref-I_DD)) < 1e-9)

def test_AAT_MP2_H2O():
    psi4.core.clean_options()
    psi4.set_memory('2 GB')
    psi4.set_output_file('output.dat', False)
    psi4.set_options({'scf_type': 'pk',
                      'e_convergence': 1e-12,
                      'd_convergence': 1e-12,
                      'r_convergence': 1e-12})

    psi4.set_options({'basis': 'STO-6G'})
    mol = psi4.geometry(moldict["H2O"])
    rhf_e, rhf_wfn = psi4.energy('SCF', return_wfn=True)
    print(f"  SCF Energy from Psi4: {rhf_e}")

    AAT = magpy.AAT(mol, 0, 1)

    r_disp = 0.0001
    b_disp = 0.0001
    e_conv = 1e-12
    r_conv = 1e-12
    I_00, I_0D, I_D0, I_DD = AAT.compute('MP2', r_disp, b_disp, e_conv=e_conv, r_conv=r_conv, normalization='intermediate', parallel=True)
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

    I_00_ref = make_np_array("""
[[-0.000000000002406  0.000000000001876 -0.226306484072463]
 [-0.000000000006755 -0.000000000025377  0.000000000014559]
 [ 0.329611190274868  0.000000000001123 -0.000000000000121]
 [ 0.000000000001081  0.000000000001413  0.059895496713927]
 [-0.000000000000801 -0.000000000000127 -0.13650378161221 ]
 [-0.229202569423865  0.215872630813217  0.000000000000268]
 [-0.000000000002056  0.000000000000205  0.059895496713195]
 [ 0.000000000001551 -0.000000000001169  0.136503781610848]
 [-0.22920256942768  -0.215872630812974 -0.000000000000161]]
 """)

    I_0D_ref = make_np_array("""
[[ 0.000000000000048 -0.000000000000024  0.007752185486049]
 [ 0.00000000000014   0.000000000000325 -0.00000000000047 ]
 [-0.006567805640442 -0.000000000000014  0.               ]
 [-0.000000000000018 -0.000000000000018 -0.001777052652742]
 [ 0.000000000000019  0.000000000000002  0.00424931513158 ]
 [ 0.004567071505769 -0.002765917049957  0.000000000000004]
 [ 0.000000000000037 -0.000000000000003 -0.001777052652901]
 [-0.000000000000028  0.000000000000015 -0.004249315131465]
 [ 0.004567071505856  0.002765917049954 -0.000000000000004]]
 """)

    I_D0_ref = make_np_array("""
[[-0.000000000000067 -0.000000000000032 -0.007752185395964]
 [-0.000000000000143 -0.000000000000311  0.000000000000497]
 [ 0.006567805572086 -0.000000000000012 -0.               ]
 [ 0.000000000000063  0.00000000000005   0.001777052707724]
 [ 0.00000000000002   0.000000000000028 -0.004249315203936]
 [-0.004567071924703  0.002765917367314 -0.000000000000003]
 [ 0.000000000000033  0.000000000000043  0.001777052707826]
 [-0.000000000000015 -0.000000000000061  0.004249315203952]
 [-0.004567071924689 -0.002765917367298  0.000000000000003]]
 """)

    I_DD_ref = make_np_array("""
[[-0.000000000000036  0.000000000000037 -0.0031546813841  ]
 [-0.000000000000034 -0.000000000000786  0.000000000000332]
 [ 0.014272447944736 -0.000000000000024 -0.000000000000002]
 [ 0.000000000000037  0.000000000000028  0.000473603610662]
 [-0.000000000000048 -0.000000000000025 -0.003196493501572]
 [-0.008371749310594  0.006594071484124 -0.000000000000008]
 [-0.000000000000013  0.000000000000008  0.000473603610694]
 [ 0.000000000000033 -0.000000000000046  0.003196493501584]
 [-0.00837174931061  -0.006594071484041  0.000000000000002]]
 """)

    assert(np.max(np.abs(I_00_ref-I_00)) < 1e-9)
    assert(np.max(np.abs(I_0D_ref-I_0D)) < 1e-9)
    assert(np.max(np.abs(I_D0_ref-I_D0)) < 1e-9)
    assert(np.max(np.abs(I_DD_ref-I_DD)) < 1e-9)

def test_AAT_MP2_H2O_NORM():
    psi4.core.clean_options()
    psi4.set_memory('2 GB')
    psi4.set_output_file('output.dat', False)
    psi4.set_options({'scf_type': 'pk',
                      'e_convergence': 1e-12,
                      'd_convergence': 1e-12,
                      'r_convergence': 1e-12})

    psi4.set_options({'basis': 'STO-6G'})
    mol = psi4.geometry(moldict["H2O"])
    rhf_e, rhf_wfn = psi4.energy('SCF', return_wfn=True)
    print(f"  SCF Energy from Psi4: {rhf_e}")

    AAT = magpy.AAT(mol, 0, 1)

    r_disp = 0.0001
    b_disp = 0.0001
    e_conv = 1e-12
    r_conv = 1e-12
    I_00, I_0D, I_D0, I_DD = AAT.compute('MP2', r_disp, b_disp, e_conv=e_conv, r_conv=r_conv, normalization='full', parallel=True)

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

    I_00_ref = make_np_array("""
[[ 0.000000000001721 -0.000000000000068 -0.221387317524535]
 [ 0.000000000007316 -0.000000000004428 -0.000000000016614]
 [ 0.322446515529638  0.000000000006536  0.00000000000002 ]
 [ 0.000000000001097 -0.000000000000148  0.058593563521845]
 [ 0.000000000000973 -0.000000000000117 -0.133536633594051]
 [-0.224220451385701  0.211180262272626 -0.000000000000717]
 [ 0.000000000000027 -0.000000000000412  0.058593563527749]
 [-0.000000000002782  0.000000000000299  0.133536633596992]
 [-0.224220451389707 -0.211180262278781  0.0000000000007  ]]
 """)

    I_0D_ref = make_np_array("""
[[-0.000000000000034  0.000000000000001  0.007583678199686]
 [-0.000000000000114  0.000000000000057  0.000000000000593]
 [-0.006425042916997 -0.000000000000084 -0.               ]
 [ 0.                 0.000000000000002 -0.00173842531093 ]
 [ 0.000000000000002  0.000000000000001  0.004156948848138]
 [ 0.004467798232422 -0.002705795013633  0.000000000000006]
 [-0.000000000000022  0.000000000000005 -0.001738425311044]
 [ 0.000000000000076 -0.000000000000004 -0.004156948848125]
 [ 0.004467798232474  0.002705795013711 -0.000000000000006]]
 """)

    I_D0_ref = make_np_array("""
[[ 0.000000000000065 -0.000000000000053 -0.007583678111357]
 [ 0.000000000000168 -0.000000000000045 -0.000000000000575]
 [ 0.006425042850052  0.000000000000033 -0.               ]
 [ 0.000000000000014  0.000000000000024  0.001738425364858]
 [-0.000000000000049  0.000000000000053 -0.004156948918668]
 [-0.004467798642237  0.002705795324085 -0.000000000000004]
 [-0.000000000000062  0.000000000000033  0.001738425364843]
 [ 0.000000000000065 -0.000000000000031  0.004156948918642]
 [-0.004467798642258 -0.002705795324132  0.000000000000004]]
 """)

    I_DD_ref = make_np_array("""
[[ 0.000000000000034 -0.000000000000001 -0.003086108876351]
 [ 0.000000000000277 -0.000000000000149 -0.000000000000402]
 [ 0.013962211367954  0.000000000000081  0.               ]
 [ 0.000000000000021 -0.000000000000018  0.000463309009422]
 [-0.000000000000024  0.000000000000016 -0.003127012134506]
 [-0.008189774722132  0.006450737827319 -0.000000000000021]
 [ 0.000000000000008 -0.000000000000001  0.000463309009462]
 [-0.000000000000024  0.000000000000003  0.003127012134507]
 [-0.00818977472214  -0.006450737827457  0.000000000000013]]
 """)

    assert(np.max(np.abs(I_00_ref-I_00)) < 1e-9)
    assert(np.max(np.abs(I_0D_ref-I_0D)) < 1e-9)
    assert(np.max(np.abs(I_D0_ref-I_D0)) < 1e-9)
    assert(np.max(np.abs(I_DD_ref-I_DD)) < 1e-9)

