from pygromacs.gmxfiles import *

path = 'pygromacs/tests/grompp.mdp'

def test_init():
    mdp = MdpFile()
    assert (mdp.path == None)

def test_read():
    mdp = MdpFile(path)
    assert (type(mdp) == MdpFile)
    assert (mdp.path == path)

def test_get_option():
    mdp = MdpFile(path)
    assert (mdp.get_option('nsteps') == '10000')
    assert (mdp.get_option('Tcoupl') == 'v-rescale')

def test_set_option():
    mdp = MdpFile(path)
    mdp.set_option('nsteps', 25000)
    assert (mdp.get_option('nsteps') == '25000')
    mdp.set_option('verlet-buffer-drift', 0.15)
    assert (mdp.get_option('verlet-buffer-drift') == '0.15')
    assert (mdp.lines[-1] == mdp.options['verlet-buffer-drift'])
