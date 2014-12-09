from pygromacs.utils import *

def test_prepare_path():
    path = 'pygromacs/tests/grompp.mdp'
    directory, filename = os.path.split(path)
    bkpfile = "#%s.1#" % filename

    backup = prepare_path('')
    assert (backup == "")
    backup = prepare_path(path)
    assert (backup == os.path.join(directory, bkpfile))
    assert (os.access(backup, os.F_OK) == True)
    os.rename(backup, path)

    # Test creation of a new directory
    newdir = os.path.join(directory, 'prepare_path_test')
    backup = prepare_path(os.path.join(newdir, filename))
    assert (backup == "")
    assert (os.path.isdir(newdir) == True)
    os.rmdir(newdir)
