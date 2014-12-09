#!/usr/bin/env python

import os
from contextlib import redirect_stdout
from pygromacs.utils import verify_path

"""Interfaces for reading and modifying Gromacs standard files."""

class Topol(object):

    def __init__(self, **kwargs):
        self.filename = kwargs.pop('file', None)
        self.read()

        return None

class MdpFile(object):
    """Container for MDP files.

    Args:
        path (str): Read from file at this path (optional)

    Attributes:
        path: Path to the last-read file. Used as default by :func:`save`
            when writing changes to disk.

        lines: This is an ordered list of :class:`MdpOption` objects, containing
            the parameters, values, and comments which together make up a file.
            It is a list to keep a read file as close to the original as possible
            when modifying it.

        options: This is a dictionary of parameters, linking to objects in
            :attr:`lines`. Used internally to quickly access any parameter
            of that list and thus file.

    """

    def __init__(self, path=""):
        self.path = path
        self.lines = []
        self.options = {}

        if self.path:
            self.read(path)

    class MdpOption(object):
        """Container for an MDP option.

        Args:
            parameter (str): A parameter,
            value (str): its value
            comment (str): and comment
            index (int): Index of option in :attr:`MdpFile.lines`

        """

        def __init__(self, parameter="", value="", comment="", index=None):
            self.parameter = str(parameter)
            self.value = str(value)
            self.comment = str(comment)
            self.index = index

        def print(self, comment=True):
            """Print option as a line.

            Uses a standard MDP format. Use ``comment`` to print or ignore
            a comment. Returns printed string.

            """

            string = ""
            if self.parameter:
                string += "%-24s = %s" % (self.parameter, self.value)
            if comment and self.comment:
                string += "; %s" % self.comment
            if self.parameter or comment:
                print(string)
            return string

    def get_option(self, parameter):
        """Return the value of a parameter.

        Args:
            parameter(str): A parameter

        Returns:
            str: The parameter value, empty if not found

        """

        try:
            value = self.options[parameter].value
        except KeyError:
            value = ""
            print("option '%s' not in list" % parameter)

        return value

    def set_comment(self, parameter, comment=""):
        """Add a comment to a parameter."""

        if parameter not in self.options.keys():
            print("option '%s' not in list" % parameter)
            return None

        # Verify that comment is of good form
        self.options[parameter].comment = comment.lstrip('; ')

        return None

    def set_option(self, parameter, value, comment=""):
        """Set a parameter value.

        If the parameter is not set the option is appended to
        end of :attr:`lines`.

        Args:
            parameter (str): A parameter to set,
            value (str): its new value
            comment (str): and comment (optional)

        """

        if parameter in self.options.keys():
            self.options[parameter].value = str(value)
        else:
            index = len(self.lines)
            self.options[parameter] = self.MdpOption(parameter, value, "", index)
            self.lines.append(self.options[parameter])

        if comment:
            self.set_comment(parameter, comment)

    def remove_option(self, parameter):
        """Remove a parameter from the file."""

        if parameter in self.options.keys():
            # Find index of parameter and remove
            index = self.options[parameter].index
            self.options.pop(parameter)
            self.lines.pop(index)

            # Adjust indices of following in list
            for option in self.lines[index:]:
                option.index -= 1

    def search(self, string):
        """Search for a parameter in the file.

        Prints any matching option and its value.

        """

        string = str(string).strip()
        test = [self.print_option(option) for option in self.options.keys()
                if option.find(string) != -1]
        return test

    def print_option(self, parameter):
        """Print a parameter, its value and comment."""

        if parameter in self.options.keys():
            string = self.options[parameter].print()
        return string

    def print(self, comment=True):
        """Print the current file.

        Args:
            comment (bool): Print or ignore comments

        """

        [option.print(comment) for option in self.lines]

    def read(self, path):
        """Read an MDP file at ``path``.

        Updates :attr:`path` to given value. Parameters and lines
        are stored in :attr:`lines` and :attr:`options`.

        """

        def parse_line(line):
            try:
                option, comment = line.split(';', 1)
            except ValueError:
                option, comment = line, ""
            try:
                parameter, value = option.split('=')
            except ValueError:
                parameter, value = "", ""
            return [var.strip() for var in (parameter, value, comment)]

        def add_line(line, index):
            parameter, value, comment = parse_line(line)

            # Link option keyword to place in ordered list
            option = self.MdpOption(parameter, value, comment, index)
            if parameter and value:
                self.options[parameter] = option

            return option

        # Verify file extension
        if not os.access(path, os.R_OK) and not path.endswith('.mdp'):
            path += '.mdp'

        self.path = path
        self.lines = []
        self.options = {}
        try:
            with open(self.path, 'r') as fp:
                self.lines = [add_line(line, index)
                        for index, line in enumerate(fp.readlines())]

        except FileNotFoundError:
            print("could not open '%s' for reading" % self.path)
            self.path = None

    def save(self, path="", verbose=True, ext='mdp'):
        """Save current MDP file.

        The written content is set in :attr:`lines`.

        Args:
            path (str): Write file to this path (by default to :attr:`path`)
            verbose (bool): Print information about save
            ext (str): Use this file extension (by default 'mdp')

        Returns:
            str: The path to a file if one was backed up

        """

        if path == "":
            path = self.path

        # Verify file extension
        if not path.endswith(ext):
            path = ''.join([path, '.', ext])

        # Verify path and backup collision
        backup = verify_path(path, verbose)

        if verbose:
            print("Saving MDP file as '%s' ... " % path, end = "")

        # Actually save the file
        with open(path, 'w') as fp:
            with redirect_stdout(fp):
                self.print()
        if verbose:
            print("Done!")

        return backup
