#!/usr/bin/env python

import os
from contextlib import redirect_stdout

def verify_path(path, verbose=True):
    """
    Verify that a location exists and backup any file found there.

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
        backup = "#%s.%d#" % (path, i)
        i += 1

    if i > 1:
        os.rename(path, backup)
        if verbose:
            print("Backed up '%s' to '%s'" % (path, backup))


class Topol(object):

    def __init__(self, **kwargs):
        self.filename = kwargs.pop('file', None)
        self.read()

        return None

class MdpFile(object):
    """
    An mdp file object. Initialise with path, or empty to build
    from scratch.

        mdp = MdpFile(path)
        mdp = MdpFile()

    The file is saved line by line into and MdpOption subclass object,
    containing the line parameter, value, and comment. The order of lines
    is remembered.

    Properties:
        path - a file name for reading
        ext - file name extension (default: .mdp)

    Methods:
        get_option(parameter) - return a parameter value
        set_comment(parameter, comment) - set a parameter comment
        set_option(parameter, value, [comment]) - set a parameter value
        remove_option(parameter) - remove a parameter option from list
        search(parameter) - search for a string among parameters
        print([comment]) - print all lines of file (set or disable comments)
        print_option(parameter) - print a parameter and its value
        read(path) - read file at path and set as path property
        save(path, verbose) - save mdp file to path

    """

    def __init__(self, path=None):
        self.path = path
        self.ext = ".mdp"
        self.lines = []
        self.options = {}

        if self.path:
            self.read(path)

    class MdpOption(object):
        def __init__(self, parameter="", value="", comment="", index=None):
            self.parameter = str(parameter)
            self.value = str(value)
            self.comment = str(comment)
            self.index = index

        def print(self, comment=True):
            if self.parameter:
                print("%-24s = %s" % (self.parameter, self.value), end=" ")
            if comment and self.comment:
                print("%s" % self.comment, end="")
            if self.parameter or comment:
                print()

    def get_option(self, parameter):
        """
        Return the value of a parameter.

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
        comment = comment.strip()
        if not comment.startswith(';'):
            comment = "; " + comment
        self.options[parameter].comment = comment

        return None

    def set_option(self, parameter, value, comment=""):
        """
        Set a parameter value for options list. If parameter not set,
        adds to end of list.

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
        Remove option from list.

        """

        if parameter in self.options.keys():
            # Find index of parameter and remove
            index = self.options[parameter].index
            self.options.pop(parameter)
            self.lines.pop(index)

            # Adjust indices of following in list
            for option in self.lines[index:]:
                option.index -= 1

    def search(self, parameter):
        """
        Search for parameter among options.

        """

        [self.print_option(option) for option in self.options.keys()
                if option.find(parameter) != -1]

    def print_option(self, parameter, comment=False):
        """
        Print the specified option if in list. Add comment=True to
        also print comment.

        """

        if parameter in self.options.keys():
            self.options[parameter].print(comment)

    def print(self, comment=True):
        """
        Print the read mdp file in order.
        Add comment=False to not print comments.

        """

        [option.print(comment) for option in self.lines]

    def read(self, path):
        """
        Read an mdp file and set as new path.

        """

        def parse_line(line):
            try:
                option, comment = line.split(';', 1)
                comment = ";" + comment
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

        self.path = path
        self.lines = []
        self.options = {}
        try:
            with open(self.path, 'r') as fp:
                self.lines = [add_line(line, index)
                        for index, line in enumerate(fp.readlines())]
        except FileNotFoundError:
            print("[ERROR] could not open '%s' for reading" % self.path)

    def save(self, path, verbose=True):
        """
        Save to mdp file at given path. Add verbose=False to print less.

        """

        # Verify file extension
        if not path.endswith(self.ext):
            path += self.ext

        # Verify path and back up collision
        verify_path(path, verbose)

        if verbose:
            print("Saving mdp file to '%s' ... " % path, end = "")

        # Actually save the file
        with open(path, 'w') as fp:
            with redirect_stdout(fp):
                self.print()

        if verbose:
            print("Done!")
