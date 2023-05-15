.. highlight:: shell

============
Installation
============

.. |pipimage| image:: https://img.shields.io/pypi/v/doubleblind.svg
        :target: https://pypi.python.org/pypi/doubleblind

Latest version: |pipimage|

DoubleBlind stand-alone app (most beginner-friendly)
-----------------------------------------------------
A stand-alone version of DoubleBlind is available for both Windows and MacOS.
This version is the most beginner-friendly to install, since it requires the least amount of setup to make it work.

How to install it
^^^^^^^^^^^^^^^^^
You can download the latest stand-alone of DoubleBlind from the
`GitHub Releases page <https://github.com/GuyTeichman/DoubleBlind/releases/latest>`_ ('DoubleBlind-X.Y.Z_windows.zip' for Windows, and 'DoubleBlind-X.Y.Z_macos.zip' for MacOS).

If you use the DoubleBlind stand-alone app, the only other programs you will need to install are external programs that interface with DoubleBlind - such as `R <https://cran.r-project.org/bin/>`_ (if you want to use *DESeq2*), and `kallisto <https://pachterlab.github.io/kallisto/download>`_.

How to run it
^^^^^^^^^^^^^
First, unzip the .zip file you downloaded.

**On Windows:**

After unzipping,  open the "DoubleBlind.exe" file:

.. image:: /installation_screenshots/01b01_open_windows.png
  :width: 600
  :alt: Open DoubleBlind stand-alone app on Windows - Open "DoubleBlind.exe"

If this is the first time you launch DoubleBlind, the following messagebox will show up.
To get past it, first click on "More info":

.. image:: /installation_screenshots/01b02_open_windows.png
  :width: 600
  :alt: Open DoubleBlind stand-alone app on Windows - click on "More info"

Next, click on the "Run anyway" button at the bottom-right corner:

.. image:: /installation_screenshots/01b03_open_windows.png
  :width: 600
  :alt: Open DoubleBlind stand-alone app on Windows - click on "Run anyway"

The DoubleBlind app should launch now - this may take a minute or two, so be patient!

**On MacOS:**

After unzipping, open the "DoubleBlind.dmg" file.
The DoubleBlind app should launch now - this may take a minute or two, so be patient!

Install as a Python package with *pip* (best performance)
----------------------------------------------------------

You can install DoubleBlind as a Python package via `pip`_.

How to install it
^^^^^^^^^^^^^^^^^

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

**On Windows:** you may also need to install `Microsoft Visual C++ 14.0 <https://visualstudio.microsoft.com/visual-cpp-build-tools/>`_ or greater, and `Perl <https://strawberryperl.com/>`_.

**On Linux:** you may also need to install **Qt 6 Image Formats** to view tutorial videos from within DoubleBlind.
To do so on Debian/ubuntu systems, use the command `sudo apt install qt6-image-formats-plugins`.
To do so on Red Hat-based distros such as Fedora, use the command `dnf install qt6-qtimageformats`.

After installing these external dependencies, you can install DoubleBlind by typing the following command in your terminal window::

    pip install doubleblind


.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

How to run it
^^^^^^^^^^^^^

If you installed DoubleBlind with *pip*, you can open the DoubleBlind app by executing the command `doubleblind-gui` from your terminal.

Alternatively, you can open the DoubleBlind app by typing the following code into a Python console::

    >>> from doubleblind import main
    >>> main.run()


In addition, you can write Python code that uses DoubleBlind functions as described in the `programmatic interface user guide <https://guyteichman.github.io/DoubleBlind/build/user_guide.html>`_.

From sources
------------

The source code for DoubleBlind can be downloaded from the `Github repository`_.

How to install it
^^^^^^^^^^^^^^^^^

First, clone the public repository:

.. code-block:: console

    $ git clone git://github.com/GuyTeichman/doubleblind


Once you have a copy of the source, you can install the basic version of DoubleBlind with:

.. code-block:: console

    $ python -m pip setup.py install

Or you can install the full version of DoubleBlind with:

.. code-block:: console

    $ python -m pip setup.py install .[all]


.. _Github repository: https://github.com/GuyTeichman/DoubleBlind


How to run it
^^^^^^^^^^^^^

If you installed DoubleBlind from source, you can open the DoubleBlind app by executing the command `doubleblind-gui` from your terminal.

Alternatively, you can open the DoubleBlind app by typing the following code into a Python console::

    >>> from doubleblind import main
    >>> main.run()

