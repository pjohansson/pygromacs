from setuptools import setup, Command, find_packages

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys,subprocess
        coverage = ['--cov', 'pygromacs', '--cov-report', 'term-missing' ]
        errno = subprocess.call([sys.executable, 'runtests.py'] + coverage)
        raise SystemExit(errno)

setup(
        name='pygromacs',
        version='0.1',
        description='A simple Gromacs manager utility',
        url='http://',
        author='Petter Johansson',
        author_email='pettjoha@kth.se',
        license='None',
        packages=find_packages(),
        cmdclass = {'test': PyTest},
        zip_safe=False
        )


