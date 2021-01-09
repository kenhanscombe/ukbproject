from setuptools import setup

setup(
    name='ukbproject',
    version='0.1',
    py_modules=['prj'],
    install_requires=[
        'Click',
        'pandas',
        'numpy',
        'bs4'
    ],
    entry_points='''
        [console_scripts]
        prj=prj:cli
    ''',
)
