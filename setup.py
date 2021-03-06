"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['chronos.py']
DATA_FILES = ['idle.png', 'ticking.png']
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'clock.icns',
    'plist': {
        'CFBundleShortVersionString': '0.1',
        'NSHumanReadableCopyright': 'Remigiusz \'lRem\' Modrzejewski',
        'CFBundleIconFile': 'clock.icns',
        'LSUIElement': '1',
        }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
