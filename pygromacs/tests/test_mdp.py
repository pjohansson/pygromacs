import os
import random
import shutil
import tempfile as tmp

from pygromacs.gmxfiles import *

path = 'pygromacs/tests/grompp.mdp'
num_tests = 10 # number of parameters to modify

def test_empty_init():
    mdp = MdpFile()
    assert (mdp.path == "")

def test_read():
    mdp = MdpFile(path)
    assert (type(mdp) == MdpFile)
    assert (mdp.path == path)

    # Try extension completion
    noext = path.rsplit('.mdp')[0]
    mdp = MdpFile(noext)
    assert (mdp.path == path)

    # Try reading bad files
    with tmp.TemporaryDirectory() as tmp_dir:
        not_a_file = os.path.join(tmp_dir, 'test.mdp')
        mdp = MdpFile(not_a_file)
        assert (mdp.path == "")

    with tmp.NamedTemporaryFile() as tmp_file:
        assert (os.access(tmp_file.name, os.F_OK) == True)
        mdp = MdpFile(tmp_file.name)
        assert (mdp.path == tmp_file.name)
        assert (mdp.lines == [])

        # Fill file with random data
        tmp_file.file.write(os.urandom(128))
        mdp = MdpFile(tmp_file.name)
        assert (mdp.path == tmp_file.name)
        assert (mdp.lines == [])

def test_get_option():
    mdp = MdpFile(path)
    assert (mdp.get_option('nsteps') == '10000')
    assert (mdp.get_option('Tcoupl') == 'v-rescale')
    assert (mdp.get_option('include') == '')
    assert (mdp.get_option('not-a-parameter') == "")
    assert (mdp.get_option(10) == "")
    assert (mdp.get_option(True) == "")

def test_set_option():
    mdp = MdpFile(path)
    mdp.set_option('nsteps', 25000)
    assert (mdp.get_option('nsteps') == '25000')

    # Try setting an option not in list
    mdp.set_option('not-a-parameter', 0.15, 'test-comment')
    assert (mdp.get_option('not-a-parameter') == '0.15')
    assert (mdp.options['not-a-parameter'].comment == 'test-comment')
    assert (mdp.lines[-1] == mdp.options['not-a-parameter'])

    # Try adding the same option again
    length, index = len(mdp.lines), mdp.options['not-a-parameter'].index
    mdp.set_option('not-a-parameter', 0.30, 'new-comment')
    assert (mdp.get_option('not-a-parameter') == '0.3')
    assert (mdp.options['not-a-parameter'].comment == 'new-comment')
    assert (len(mdp.lines) == length)
    assert (mdp.options['not-a-parameter'].index == index)

    # Try modifying many random options
    keys_change = random.sample(mdp.options.keys(), num_tests)
    for parameter in keys_change:
        value = str(random.random())
        mdp.set_option(parameter, value)
        assert (mdp.get_option(parameter) == value)

def test_remove_option():
    # Verify that indices of MdpFile.lines are adjusted
    def verify_indices(test_lines, control_lines, index):
        for test, control in zip(test_lines[index:], control_lines[index+1:]):
            assert (test.parameter == control.parameter)

    mdp = MdpFile(path)
    length = len(mdp.lines)

    keys = random.sample(mdp.options.keys(), num_tests)
    for parameter in keys:
        index = mdp.options[parameter].index
        copy_lines = mdp.lines.copy()

        # Verify that option is removed
        mdp.remove_option(parameter)
        assert (parameter not in mdp.options)
        verify_indices(mdp.lines, copy_lines, index)

        # Try to remove again
        copy_options = mdp.options.copy()
        copy_lines = mdp.lines.copy()
        mdp.remove_option(parameter)
        assert (copy_options == mdp.options)
        assert (copy_lines == mdp.lines)

    assert (len(mdp.lines) == length - num_tests)

def test_comment():
    mdp = MdpFile(path)

    assert (mdp.lines[0].comment == "")
    assert (mdp.lines[1].comment == "File 'mdout.mdp' was generated")
    assert (mdp.options['nsteps'].comment == '4 ns')

    # Try some different inputs for setting commment
    mdp.set_comment('nsteps', '4 ns set  ')
    assert (mdp.options['nsteps'].comment == '4 ns set')
    mdp.set_comment('nsteps', '   4 ns initial space')
    assert (mdp.options['nsteps'].comment == '4 ns initial space')
    mdp.set_comment('nsteps', ';4 ns initial semicolon')
    assert (mdp.options['nsteps'].comment == '4 ns initial semicolon')
    mdp.set_comment('nsteps', '4 ns ; many semicolon ;')
    assert (mdp.options['nsteps'].comment == '4 ns ; many semicolon ;')

    # Try setting a comment to non-set parameter
    mdp.set_comment('not-a-parameter', 'really important parameter')
    assert ('not-a-parameter' not in mdp.options.keys())

def test_search():
    mdp = MdpFile(path)
    assert (mdp.search('step') == 4)
    assert (mdp.search('sTeP') == 4)
    assert (mdp.search('not-a-parameter') == 0)
    assert (mdp.search(10) == 0)

def test_print():
    mdp = MdpFile(path)
    mdp.print(True)
    mdp.print(False)

def test_save():
    # Find a default backup path
    def backup_path(path, i=1):
        directory, filename = os.path.split(path)
        backup_filename = ''.join(['#', filename, '.%d#' % i])
        return os.path.join(directory, backup_filename)

    # Copy file to temporary directory
    with tmp.TemporaryDirectory() as tmp_dir:
        _, filename = os.path.split(path)
        tmp_path = os.path.join(tmp_dir, filename)
        shutil.copyfile(path, tmp_path)

        # Open file and try saving to own path
        mdp = MdpFile(tmp_path)
        mdp.save()
        backup = backup_path(tmp_path)
        assert (os.access(backup, os.F_OK) == True)

        # Compare the two versions line by line
        test = MdpFile(backup)
        for line, control in zip(test.lines, mdp.lines):
            assert (line.parameter == control.parameter)
            assert (line.value == control.value)
            assert (line.comment.strip() == control.comment.strip())
            assert (line.index == control.index)

        # Change some options
        keys_remove = random.sample(mdp.options.keys(), num_tests)
        for parameter in keys_remove:
            mdp.remove_option(parameter)
        keys_change = random.sample(mdp.options.keys(), num_tests)
        values = {}
        for parameter in keys_change:
            values[parameter] = str(random.random())
            mdp.set_option(parameter, values[parameter])

        # Save to new path
        new_filename = 'new'
        new_path = os.path.join(tmp_dir, new_filename)
        mdp.save(new_path, True)

        # Verify that changes were written
        control = MdpFile(new_path)
        for remove, change in zip(keys_remove, keys_change):
            assert (remove not in control.options.keys())
            assert (control.get_option(change) == values[change])

        # Try to save with a custom extension
        ext = 'pdm'
        ext_path = '.'.join([new_path, ext])
        mdp.save(ext_path, ext=ext)
        assert (os.access(ext_path, os.F_OK) == True)
