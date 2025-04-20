# New setup file for proper packaging
from setuptools import setup, find_packages

setup(
    name="btc_puzzle_solver",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'pycryptodome>=3.15.0',  # Patched CVE-2023-48795
        'ecdsa==0.18.0',         # Pinned to resolve conflict
        'tqdm>=4.65.0'
    ],
    entry_points={
        'console_scripts': [
            'btc-puzzle-solve=btc_puzzle_solver.cli:main',
        ],
    },
    python_requires='>=3.8',
    package_data={
        'btc_puzzle_solver': ['patterns/*.json']
    },
    include_package_data=True,
) 