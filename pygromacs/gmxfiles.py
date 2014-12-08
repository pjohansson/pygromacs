#!/usr/bin/env python

import os
from contextlib import redirect_stdout

def verify_path(path, verbose=True):
    """
    Verify that a location exists by creating required directories and
    back up any conflicting file.

    :param path: Path to file.

    :param verbose: Print information about any backup.

    :return: If a file at ``path`` existed and was backed up, its new path is returned.
        Otherwise `None`.

    :rtype: str, None

    """

    # Extract the directory and filename from the given path
    directory, filename = os.path.split(path)
    if directory == "":
        directory = "."

    # If the directory does not exists, create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    # If a file exists, back it up
    i = 1
    backup = path
    while os.path.exists(backup):
        backup = "%s/#%s.%d#" % (directory, filename, i)
        i += 1

    if i > 1:
        os.rename(path, backup)
        if verbose:
            print("Backed up '%s' to '%s'" % (path, backup))
        return backup
    else:
        return None


class Topol(object):

    def __init__(self, **kwargs):
        self.filename = kwargs.pop('file', None)
        self.read()

        return None

class MdpFile(object):
    """Container for MDP files.

    :param path: Read from file at ``path`` (optional).

    .. attribute:: MdpFile.path

        Path to the last-read file. Used as default by :func:`save` when
        writing changes to disk.

    .. attribute:: MdpFile.lines

        This is an ordered list of :class:`MdpOption` objects, containing
        parameters, values, and comments which make up a file. It is a list
        to keep a read file as close to the original as possible when
        modifying it.

    .. attribute:: MdpFile.options

        This is a dictionary of parameters, linking to objects in :attr:`lines`.
        Used internally to quickly access any parameter value or comment of
        that list.

    """

    def __init__(self, path=None):
        self.path = path
        self.lines = []
        self.options = {}

        if self.path:
            self.read(path)

    class MdpOption(object):
        """Container for an MDP option.

        :param parameter: Option

        :param value: Value

        :param comment: Comment

        :param index: Index of option in :attr:`MdpFile.lines`.

        """

        def __init__(self, parameter="", value="", comment="", index=None):
            self.parameter = str(parameter)
            self.value = str(value)
            self.comment = str(comment)
            self.index = index

        def print(self, comment=True):
            """
            Print the option line in a standard format. Use ``comment``
            to print or ignore a comment. Returns printed string.

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
        """
        Return the value of a parameter, or an empty string if
        it is not found.

        """

        try:
            value = self.options[parameter].value
        except KeyError:
            value = None
            print("option '%s' not in list" % parameter)

        return value

    def set_comment(self, parameter, comment=""):
        """
        Set a comment to a parameter.

        """

        if parameter not in self.options.keys():
            print("option '%s' not in list" % parameter)
            return None

        # Verify that comment is of good form
        self.options[parameter].comment = comment.lstrip('; ')

        return None

    def set_option(self, parameter, value, comment=""):
        """
        Set a value and (optionally) a comment for a parameter in :attr:`options`.
        If the parameter is not set the option is appended to :attr:`lines`.

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
        """
        Find an option and remove it from :attr:`lines` and :attr:`options`.

        """

        if parameter in self.options.keys():
            # Find index of parameter and remove
            index = self.options[parameter].index
            self.options.pop(parameter)
            self.lines.pop(index)

            # Adjust indices of following in list
            for option in self.lines[index:]:
                option.index -= 1

    def search(self, string, comment=True):
        """
        Search for a parameter in :attr:`options`. Prints matching options.
        Use ``comment`` to include or ignore comments.

        """

        string = str(string).strip()
        test = [self.print_option(option, comment) for option in self.options.keys()
                if option.find(string) != -1]
        return test

    def print_option(self, parameter, comment=False):
        """
        Print the specified option if found in :attr:`options`.
        Use ``comment`` to print or ignore comment.

        """

        if parameter in self.options.keys():
            string = self.options[parameter].print(comment)
        return string

    def print(self, comment=True):
        """
        Print the file in current order of :attr:`lines`. Use ``comment``
        to print or ignore comments.

        """

        [option.print(comment) for option in self.lines]

    def read(self, path):
        """
        Read an MDP file at ``path``. See :attr:`lines` and :attr:`options`
        for information on how the data is stored. Updates :attr:`path`.

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
            # Parse line for variables
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

    def save(self, path=None, verbose=True, **kwargs):
        """
        Save current MDP file, which is given by :attr:`lines`.

        :param path: Write file to this path (by default to :attr:`path`).
            Any file at this location is backed up before writing.

        :param verbose: Write information.

        :keyword ext: Use this file extension (by default 'mdp').

        :return: If a file was backed up its new path is returned, otherwise `None`.

        :rtype: str, None

        """

        if path == None:
            path = self.path

        # Verify file extension
        ext = kwargs.pop('ext', 'mdp')
        if not path.endswith(ext):
            path += '.' + ext

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
