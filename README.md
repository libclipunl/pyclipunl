pyclipunl
=========

Python interface to access CLIP UNL data

Usage
-----

Just copy the **ClipUNL.py** file to a directory, and develop from there.
On your file (for instance **mega_clip_scrapper.py**), all you need to type is

    from ClipUNL import ClipUNL

to start using ClipUNL. You're ready to programatically login to CLIP, and scrape data.

### Quick Start
Let's know your name on CLIP, shall we? Let's get us a ClipUNL object:

    from ClipUNL import ClipUNL
    import sys # For exit
    clip = ClipUNL()
    
Now, we login to CLIP, with some valid credentials. And if we can, we get the user's full name.

    if clip.login("SUPER_USER_NAME", "SECRET_PASSWORD"):
      print "Hello " + clip.get_full_name()

_These sections are very incomplete, because the API isn't fully featured yet. If you need help, read the provided docstrings_

Installation
------------

If you wish to install pyclipunl system-wide, there's a **setup.py** script for module installation.
To install this module system-wide, issue as root:

    ./setup.py install

Now you are able to import the ClipUNL module from anywhere.
