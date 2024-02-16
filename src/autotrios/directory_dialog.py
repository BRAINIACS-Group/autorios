#STL modules
import logging
import os

#3rd party modules
import win32gui
from win32com.shell import shell, shellcon

logger = logging.getLogger(__name__)

def open_directory_dialog():
    mydocs_pidl = shell.SHGetFolderLocation (0, shellcon.CSIDL_PERSONAL, 0, 0)
    pidl, display_name, image_list = shell.SHBrowseForFolder (
    win32gui.GetDesktopWindow (),
    mydocs_pidl,
    "Select a file or folder",
    shellcon.BIF_BROWSEINCLUDEFILES,
    None,
    None
    )

    if (pidl, display_name, image_list) == (None, None, None):
        logger.info("Nothing selected")
    else:
        path = shell.SHGetPathFromIDList (pidl)
        logger.info(f"Opening{path}")
        os.startfile (path)

