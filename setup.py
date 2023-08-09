from setuptools import setup

APP = ['gui_main.py']  # Replace 'your_script.py' with the name of your Python script
DATA_FILES = []  # List of additional files or resources your app requires
OPTIONS = {
    'packages': [],  # List of Python packages used by your app
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
