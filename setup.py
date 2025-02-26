from setuptools import setup, find_packages

setup(
    name='tibo',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'tibo': ['indexing/call_graph/typescript/build/typescript.so'],
    },
    install_requires=[
        'click',              
        'graphviz',           
        'tree_sitter',        
        'requests',           
        'numpy',              
        'sentence_transformers',  
        'faiss-cpu',          
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'tibo = tibo.cli:cli',
        ],
    },
    # Metadata
    description="CLI tool for codebase indexingand natural language retrieval.",
    long_description="A command-line tool for indexing codebases, generating call graphs, and chunking code into a vector database. It empowers users to query their code using natural language, retrieving relevant files, functions, and code snippets with ease.",
    long_description_content_type="text/plain",
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