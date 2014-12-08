pygromacs
=========
Some simple tools designed to generate input files for the molecular dynamics
package [Gromacs](http://www.gromacs.org/).

Planned features
----------
- [ ] Read .mdp configuration files and quickly generate many new ones with 
  specified options changed.
- [ ] Also .top topology files!
- [ ] Convolute sets of generated topologies and configuration files to prepare 
runs for a large parameter space.

Development status
------------------
Just about nothing is finished.
- [ ] MDP file tools
  - [x] File class
  - [ ] Generation tools
- [ ] Topology file tools
  - [ ] File class
  - [ ] Generation tools
- [ ] Tools for cross producing run input files far from done

Installation
------------
Currently only Python 3.4 is supported, while a workaround for redirect_stdout is implemented.
Also, there's currently nothing to install. In theory:

```bash
python setup.py install
```

Documentation
-------------
Documentation is available at Read the Docs: http://pygromacs.readthedocs.org/

[![Build Status](https://travis-ci.org/pjohansson/pygromacs.svg?branch=working)](https://travis-ci.org/pjohansson/pygromacs)
[![Documentation Status](https://readthedocs.org/projects/pygromacs/badge/?version=latest)](https://readthedocs.org/projects/pygromacs/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/pjohansson/pygromacs/badge.png?branch=working)]
(https://coveralls.io/r/pjohansson/pygromacs?branch=working)

Links
-----
http://www.gromacs.org/
