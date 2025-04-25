import glob
import sys
import os
import shutil

for i in range(1, len(sys.argv)):
    arg = sys.argv[i]
    pathname = os.path.join(os.getcwd(), arg)

    paths = glob.glob(pathname, recursive=True)
    for path in paths:
        if os.path.exists(path):
            if os.path.isfile(path):
                os.unlink(path)
            else:
                shutil.rmtree(path)
