#################################
DoubleBlind User guide
#################################



Starting the DoubleBlind app
*****************************

When you first start the DoubleBlind application, you will see a window with two tabs: "Blind data" and "Un-blind data".

Blind Data
------------

From the "Blind data" tab, you can encode ("blind") your data, by replacing the original names of the files with randomly generated names.
You can set the following options:

* **File types to blind** – a dropdown menu to select the files type to blind. The common options include Olympus microscope images (.vsi) and image/video files (.tif,.png,.mp4, etc.) However, you can specify your file types by selecting “other file type”.
* **Input director** – select a directory containing files you want to blind.
* **Output directory for a mapping table (optional)** – select a directory to store a .csv file containing the encrypted names (encoded_name), original file names (decoded_name), as well as the paths to the blinded files. If this is not specified, the mapping file will be stored in the input directory. This file is for your reference only - DoubleBlind can unblind your data without it.
* **Apply to files in subfolders** – if selected, blinding will be applied to all files of the same type in the subfolders, in addition to the ones at the top level.


When you're ready to blind your data, click on the "run" button.

Un-blind Data
---------------

In the "Un-blind data" tab, you can decode ("un-blind") your data.
DoubleBlind can decode a file using only its encoded name - no reference table is necessary, and you don't have to un-blind all of your files at the same time.
You can set the following options:

* **File types to un-blind** – choose the file type to un-blind, which should be the same as your input.
* **Input directory** – select the folder containing the blinded files.
* **Replace blinded names in more files** – if selected, DoubleBlind will read through data files (.txt, .csv, xlsx, etc.) in the specified directory, and replace all occurances of the encoded names in these data files with the original names. This is useful when you store your blinded quantification results in an Excel files, and want to un-blind the names in that file.
* **Apply to files in subfolders** – if selected, unblinding will be applied to all files of the same type in the subfolders, in addition to the ones in the top level.

When you're ready to un-blind your data, click on the "run" button.

Additional Options
**********************

On the top of the main window, you will find a menu bar with the options "View" and "Help".

View
------

Under "View", you have options to toggle "Dark mode", change "Font size", and "Reset view settings".

Help
--------


About DoubleBlind
======================

When you click on "About DoubleBlind", a window will open that shows information about the version of DoubleBlind, the development lead, and contributors.

How to Cite DoubleBlind
========================

If you click on "How to Cite DoubleBlind", a window will open that shows the citation format for DoubleBlind.

Check for Updates
==================
If you click on "Check for Updates", DoubleBlind will check if there's a new version available and will ask if you wish to download it.

