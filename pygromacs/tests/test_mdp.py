from pygromacs.gmxfiles import *

def test_read():
    mdp = MdpFile('pygromacs/tests/grompp.mdp')
    assert (mdp.get_option('nsteps') == '10000')
