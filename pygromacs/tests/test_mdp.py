import filecmp
import os
import random

from pygromacs.gmxfiles import *

path = 'pygromacs/tests/grompp.mdp'

def test_init():
    mdp = MdpFile()
    assert (mdp.path == None)

def test_read():
    mdp = MdpFile(path)
    assert (type(mdp) == MdpFile)
    assert (mdp.path == path)
    assert (mdp.lines[0].comment == ";")
    assert (mdp.lines[1].comment == ";	File 'mdout.mdp' was generated")

    # Try reading bad file name
    mdp = MdpFile(os.urandom(8))
    assert (mdp.path == None)

def test_get_option():
    mdp = MdpFile(path)
    assert (mdp.get_option('nsteps') == '10000')
    assert (mdp.get_option('Tcoupl') == 'v-rescale')
    assert (mdp.get_option('not-a-parameter') == None)

def test_set_option():
    mdp = MdpFile(path)
    mdp.set_option('nsteps', 25000)
    assert (mdp.get_option('nsteps') == '25000')
    mdp.set_option('verlet-buffer-drift', 0.15, 'test-comment')
    assert (mdp.get_option('verlet-buffer-drift') == '0.15')
    assert (mdp.options['verlet-buffer-drift'].comment == '; test-comment')
    assert (mdp.lines[-1] == mdp.options['verlet-buffer-drift'])

def test_remove_option():
    def verify_lines(test_lines, control_lines, index):
        """Verify that indices of MdpFile.lines are adjusted."""

        for test, control in zip(test_lines[index:], control_lines[index+1:]):
            assert (test.parameter == control.parameter)

    mdp = MdpFile(path)
    length = len(mdp.lines)

    num_test = 10
    keys = random.sample(mdp.options.keys(), num_test)
    for parameter in keys:
        index = mdp.options[parameter].index
        copy_lines = mdp.lines.copy()

        # Verify that option is removed
        mdp.remove_option(parameter)
        assert (parameter not in mdp.options)
        verify_lines(mdp.lines, copy_lines, index)

        # Try to remove again
        copy_options = mdp.options.copy()
        copy_lines = mdp.lines.copy()
        mdp.remove_option(parameter)
        assert (copy_options == mdp.options)
        assert (copy_lines == mdp.lines)

    assert (len(mdp.lines) == length-num_test)

def test_comment():
    mdp = MdpFile(path)
    assert (mdp.options['nsteps'].comment == '; 4 ns')
    mdp.set_comment('nsteps', '4 ns run')
    assert (mdp.options['nsteps'].comment == '; 4 ns run')
    mdp.set_comment('nsteps', ' 4 ns with space')
    assert (mdp.options['nsteps'].comment == '; 4 ns with space')
    mdp.set_comment('nsteps', ';4 ns with semicolon')
    assert (mdp.options['nsteps'].comment == ';4 ns with semicolon')
    mdp.set_comment('nsteps', '4 ns ; with several semicolon ;')
    assert (mdp.options['nsteps'].comment == '; 4 ns ; with several semicolon ;')
    mdp.set_comment('not-a-parameter', 'really important parameter')

def test_search():
    mdp = MdpFile(path)
    assert (mdp.search('step', True) != [])
    assert (mdp.search('step', False) != [])
    assert (mdp.search('not-a-parameter') == [])
    assert (mdp.search(10) == [])

def test_print():
    mdp = MdpFile(path)
    mdp.print(True)
    mdp.print(False)

def test_save():
    mdp = MdpFile(path)

    # Save to same path
    backup = mdp.save()
    test_file = MdpFile(path)

    # Control content of copy
    for test, control in zip(test_file.lines, mdp.lines):
        assert (test.parameter == control.parameter)
        assert (test.value == control.value)
        assert (test.comment == control.comment)
        assert (test.index == control.index)

    # Return file to original state
    os.rename(backup, mdp.path)

    # Change options
    num_test = 10
    keys_remove = random.sample(mdp.options.keys(), num_test)
    for parameter in keys_remove:
        mdp.remove_option(parameter)

    # Set options to random float
    keys_change = random.sample(mdp.options.keys(), num_test)
    rand = {}
    for parameter in keys_change:
        rand[parameter] = str(random.random())
        mdp.set_option(parameter, rand[parameter])

    # Save to new path and compare
    newpath = path.rsplit('.mdp')[0] + '-savetest'
    backup = mdp.save(newpath, False)
    control = MdpFile(newpath + '.mdp')
    for remove, change in zip(keys_remove, keys_change):
        assert (remove not in control.options.keys())
        assert (control.get_option(change) == rand[change])
    os.remove(backup)

    # Control saving to custom extension
    ext = 'newext'
    newpathext = newpath + '.' + ext
    backup = mdp.save(newpath, ext='newext')
    assert (os.access(newpathext, os.F_OK) == True)
    os.remove(newpathext)
