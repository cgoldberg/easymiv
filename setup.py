from setuptools import setup

setup(
    name='easymiv',
    version='0.1.0',
    author='Corey Goldberg',
    author_email='cgoldberg@gmail.com',
    py_modules=['easymiv',],
    url='https://github.com/cgoldberg/easymiv',
    license='GNU GPLv3',
    description='full-screen image slideshow',
    long_description=open('README.rst').read(),
    install_requires=['pillow',]
    ],
)
