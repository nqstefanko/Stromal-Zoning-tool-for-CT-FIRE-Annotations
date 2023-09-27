from setuptools import setup

APP = ['gui_main.py']  # Replace 'your_script.py' with the name of your Python script
DATA_FILES = []  # List of additional files or resources your app requires
OPTIONS = {
    'argv_emulation': True,
    'packages': [
        'PIL', 
        'datetime', 
        'numpyencoder', 
        'pprint', 
        'scipy', 
        'termcolor', 
        'shapely', 
        'matplotlib', 
        'numpy', 
        'os', 
        'sys', 
        'multiprocessing',
        'tkinter', 
        'tkinter.ttk', 
        'tkinter.filedialog', 
        'tkinter.messagebox', 
        'pathlib', 
        'json',
        'test_export',
        'sv_ttk',
        'geojson'
    ],
}


setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
