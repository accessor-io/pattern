from setuptools import setup, find_packages

setup(
    name="bitcoin_puzzle_solver",
    version="0.6",
    author="Your Name",
    description="Bitcoin Puzzle Transaction Solver",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        'base58>=2.0.0',
        'bech32>=1.2.0',
        'pycryptodome>=3.10.1',
        'secp256k1>=0.14.0'
    ],
    entry_points={
        'console_scripts': [
            'puzzle-solver=bitcoin_puzzle_solver.__main__:main'
        ]
    },
    include_package_data=True,
    python_requires=">=3.8",
) 