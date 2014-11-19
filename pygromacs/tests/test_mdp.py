from unittest import TestCase
from pygromacs.gmxfiles import MdpFile

class TestMdp(TestCase):
    def test_read(self):
        mdp = MdpFile(file='grompp.mdp')
