import os

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
