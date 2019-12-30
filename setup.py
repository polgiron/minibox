from setuptools import setup, find_packages

setup(
    name='minibox',
    version='0.1',
    packages=find_packages(exclude=["tests"]),
    url='',
    license='',
    author='Pol Giron',
    description='',
    include_package_data=True,
    package_data={
        '': ['*.avsc'],
    },
    install_requires=[
        'urwid',
        'spotipy'
    ],
    entry_points={
        'console_scripts': [
            ' minibox = minibox:main',
        ],
    },
)
