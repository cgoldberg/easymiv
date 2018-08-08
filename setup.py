from setuptools import setup

setup(
    name='easymiv',
    version='0.1.0',
    author='Sergio Perea',
    author_email='contacto@sergioperea.net',
    py_modules=['python-showcase',],
    url='https://github.com/sperea/python-showcase',
    license='GNU GPLv3',
    description='full-screen image slideshow',
    long_description=open('README.rst').read(),
    install_requires=['pillow',]
    ],
)
