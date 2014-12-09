import os

def prepare_path(path, verbose=True):
    """Prepare a path for writing.

    Creates required directories and backs up any conflicting file.

    Args:
        path (str): Path to file
        verbose (bool, optional): Whether or not to print information
            about a performed backup

    Returns:
        str: The path to a backed up file, empty if no backup was taken

    """

    # Extract the directory and filename from the given path
    directory, filename = os.path.split(path)
    if directory == "":
        directory = "."

    # If the directory does not exists, create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Search for first non-existent filename based on path
    i = 1
    backup = path
    while os.path.exists(backup):
        new_file = ''.join(['#', filename, '.%d#' % i])
        backup = os.path.join(directory, new_file)
        i += 1

    # If there was a conflict, move file to backup location
    if backup != path:
        os.rename(path, backup)
        if verbose:
            print("Backed up '%s' to '%s'." % (path, backup))
    else:
        backup = ""

    return backup
