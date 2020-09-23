from setuptools import setup

setup(
    name='exclude',
    version='0.1',
    py_modules=['exclude'],
    install_requires=[
        'Click',
        'pandas',
        'numpy'
    ],
    entry_points='''
        [console_scripts]
        exclude=exclude:exclude
    ''',
)
