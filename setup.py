from setuptools import setup, find_packages

setup(
    name='tibo',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'tibo': ['indexing/call_graph/typescript/build/typescript.so'],
    },
    entry_points={
        'console_scripts': [
            'tibo = tibo.cli:cli',
        ],
    },
)