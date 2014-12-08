from pygromacs.utils import *

def test_verify_path():
    path = 'pygromacs/tests/grompp.mdp'
    directory, filename = os.path.split(path)
    bkpfile = "#%s.1#" % filename

    backup = verify_path('')
    assert (backup == None)
    backup = verify_path(path)
    assert (backup == os.path.join(directory, bkpfile))
    assert (os.access(backup, os.F_OK) == True)
    os.rename(backup, path)

    # Test creation of a new directory
    newdir = os.path.join(directory, 'verify_path_test')
    backup = verify_path(os.path.join(newdir, filename))
    assert (backup == None)
    assert (os.path.isdir(newdir) == True)
    os.rmdir(newdir)
