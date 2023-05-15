.. image:: https://raw.githubusercontent.com/GuyTeichman/DOubleBlind/master/docs/source/doubleblind.png
    :target: https://guyteichman.github.io/DoubleBlind
    :width: 400
    :alt: logo

**Useful links:** `Documentation <https://guyteichman.github.io/DoubleBlind>`_ |
`Source code <https://github.com/GuyTeichman/DoubleBlind>`_ |
`Bug reports <https://github.com/GuyTeichman/DoubleBlind/issues>`_ | |pipimage| | |versionssupported| | |githubactions| | |downloads|

What is DoubleBlind?
---------------------
DoubleBlind is a software tool that automatically and reversibly replaces file names with random strings to help experimenters quantify microscopy experiments blindly and maintain experimental integrity.

DoubleBlind aims to solve a common problem in scientific image quantification - keeping oneself blind to the experimental conditions.
When experimenters are able to see the experimental conditions of their data during quantification, it can bias their observations and interpretations of the results.
DoubleBlind solves this problem by automatically replacing file names with random strings, which can then be unblinded later when the experiment is complete. This allows experimenters to analyze their experiments without being influenced by knowledge of the experimental conditions, while still being able to access their original files later.

DoubleBlind file name replacement process is completely reversible, so users can easily unblind their image files when the experiment is complete.
You don't need to keep any special mapping of the original filenames - a blinded file can be unblinded just based on its encoded name.

Files can be blinded and unblinded at any time, individually or in groups.
This allows experimenters to maintain the blinding of their data until the end of the experiment, while still being able to access the original filenames when needed.

DoubleBlind supports most accepted file formats, as well as specialized microscopy image formats, such as Olympus .vsi files.

Once the experiment is complete, DoubleBlind makes it easy to unblind the files and to replace the coded filenames with the original filenames in data files such as Excel sheets and text files.
This ensures that the final data analysis is accurate and reliable.

DoubleBlind is also designed to be easy to use, with a simple and intuitive interface that works on all operating systems.
This ease of use is particularly important for experimenters who may not have extensive experience with software tools.


.. |pipimage| image:: https://img.shields.io/pypi/v/doubleblind.svg
    :target: https://pypi.python.org/pypi/doubleblind
    :alt: PyPI version
.. |downloads| image:: https://pepy.tech/badge/doubleblind
    :target: https://pepy.tech/project/doubleblind
    :alt: Downloads
.. |versionssupported| image:: https://img.shields.io/pypi/pyversions/doubleblind.svg
    :target: https://pypi.python.org/pypi/doubleblind
    :alt: Python versions supported

..  |githubactions| image:: https://github.com/guyteichman/DoubleBlind/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/GuyTeichman/DoubleBlind/actions/workflows/tests.yml
    :alt: Build status