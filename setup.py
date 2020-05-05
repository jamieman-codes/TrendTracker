import sys
from cx_Freeze import setup, Executable
import os.path
import matplotlib

base = None
if sys.platform == "win32": #Checking what version of windows you are running
    base = "Win32GUI" 
#Have to load certain files and modules to be saved with the program so that the exe doesnt crash when it is run
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__)) #Load the directory that python is saved to
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6') #Load the tcl8.6 file from the python directory to be saved with the program
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6') 
build_exe_options = {"packages": ["os","tkinter", "tkinter.filedialog", "idna", "tweepy"], #The depencies for the program are normally auto matically detected but in some cases they need to be specified
                     "includes":["tkinter","matplotlib.backends.backend_tkagg",'numpy.core._methods', 'numpy.lib.format'], 
                     "include_files":["countryCodes.p","tcl86t.dll", "tk86t.dll", (matplotlib.get_data_path(), "mpl-data")]}


setup(
    name = "Trend Tracker",
    version = "1.1",
    author  = 'Jamie Stevens',
    author_email = 'jamiestevens2000@gmail.com',
    description = "Trend tracking tool for Google and Twitter",
    options = {"build_exe": build_exe_options},
    package_dir={'': ''},
    executables = [Executable("TrendTracker.py", base = base)])