from setuptools import setup, find_packages

setup(
    name='polynx',  
    version='0.1.3',
    packages=find_packages(),
    install_requires=[  
        "polars>=1.24",
        "lark>=1.2.2",
        "matplotlib>=3.8.2",
        "pandas>=2.1.4",
        "numpy>=1.26.2",
    ],
    author='Lowell Winsston',
    author_email='lowell.j.winston@gmail.com',
    description='String-powered Polars expression engine with extended DataFrame utilities.',
    long_description=open('README.md').read(),
    long_description_content_type="A polars wrapper that support .query and .eval similar to pandas",
    url="https://github.com/LowellWinston/polynx.git",  
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    project_urls={
        'Changelog': 'https://github.com/LowellWinston/polynx.git/blob/main/CHANGELOG.md',
    },
)
