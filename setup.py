#!/usr/bin/env python2
from distutils.core import setup

setup(
        name='pyclipunl',
        version='0.0.1',
        description='Library to scrape UNL\'s CLIP (https://clip.unl.pt) data',
        long_description="""This library allows people with credentials
to the UNL (Universidade Nova de Lisboa) CLIP system, to
programatically access their data""",
        author='David Serrano',
        author_email='david.nonamedguy@gmail.com',
        url="https://github.com/libclipunl/pyclipunl",
        py_modules=['ClipUNL'],
        requires=['BeautifulSoup (==3.0)'],
        license='MIT'
    )
