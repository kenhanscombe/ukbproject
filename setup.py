from setuptools import setup, find_packages

setup(
    name='ukbproject',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    # py_modules=['prj'],
    entry_points='''
        [console_scripts]
        prj=ukbproject.prj:cli
    ''',
    install_requires=[
        'Click',
        'snakemake>=5.31',
        'pandas',
        'numpy',
        'bs4'
    ]
)
