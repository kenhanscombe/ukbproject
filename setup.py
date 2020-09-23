from setuptools import setup

setup(
    name='exclude',
    version='0.1',
    py_modules=['exclude'],
    install_requires=[
        'Click',
        'pandas >= 1.1.1',
        'numpy >= 1.19.1'
    ],
    entry_points='''
        [console_scripts]
        exclude=exclude:exclude
    ''',
)
