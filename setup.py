from setuptools import setup

APP = ['yourscript.py']
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
    name='YourApplicationName',
    version='1.0',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)