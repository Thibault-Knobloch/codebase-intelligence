from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='tibo',
    version='1.1.3',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'tibo': ['indexing/call_graph_utils/typescript/build/typescript.so'],
    },
    install_requires=[
        'click==8.1.8',              
        'graphviz==0.20.3',           
        'tree_sitter==0.21.3',        
        'requests==2.32.3',           
        'numpy==1.26.4',              
        'sentence_transformers==3.4.1',  
        'faiss-cpu==1.10.0',          
        'python-dotenv==1.0.1',
        'anthropic==0.43.0',
        'openai==1.59.3'
    ],
    entry_points={
        'console_scripts': [
            'tibo = tibo.cli:cli',
        ],
    },
    # Metadata
    description="CLI tool for codebase indexing and natural language retrieval.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Thibault Knobloch",
    author_email="thibaultknobloch@yahoo.fr",
    url="https://github.com/Thibault-Knobloch/codebase-intelligence",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.9",
)