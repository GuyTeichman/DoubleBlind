from multiprocessing import freeze_support

from doubleblind import main

if __name__ == '__main__':
    freeze_support()
    main.run()
