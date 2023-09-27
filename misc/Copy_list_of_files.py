import shutil
from os import path
from tkinter import filedialog
from tkinter import Tk
import time


Tk().withdraw()

# Specify input and output directory
csv_path = filedialog.askopenfilename(title='Select csv/txt file containing files to copy', filetypes= (('text files', ".txt"), ('csv files', '*.csv')))
dstdir = filedialog.askdirectory(title='Select destination directory')


with open(csv_path) as csv:
    csv = csv.read().splitlines()
    files = []
    for file in csv:
        if path.isfile(file):
            files.append(file)

    for idx,file in enumerate(files, start=1):
        
        print("\r Copying file {} of {}".format(idx, len(csv)), end='')  

        base = path.basename(file.strip())
        dst = path.join(dstdir,base)

        shutil.copy2(file.strip(), dst) 

print('\n\nAll files copied')
time.sleep(3)

