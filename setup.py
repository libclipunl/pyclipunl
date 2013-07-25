from distutils.core import setup

setup(
        name='pyclipunl',
        version='0.0.1',
        description='Library to scrape UNL\'s CLIP (https://clip.unl.pt) data',
        author='David Serrano',
        author_email='david.nonamedguy@gmail.com',
        url="https://github.com/libclipunl/pyclipunl",
        py_modules=['ClipUNL'],
        requires=['BeautifulSoup==3'],
        license='MIT'
    )
