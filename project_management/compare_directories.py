import os
from tkinter import filedialog

dir1 = filedialog.askdirectory(title="Select first directory to compare")
dir2 = filedialog.askdirectory(title="Select second directory to compare")

dir1_files = list()
for (root, sub, files) in (os.walk(dir1)):
    dir1_files += [os.path.join(file) for file in files]

dir2_files = list()
for (root, sub, files) in (os.walk(dir2)):
    dir2_files += [os.path.join(file) for file in files]

set_dif = set(dir1_files).symmetric_difference(set(dir2_files))
difference = list(set_dif)

list_length = len(difference)

if list_length >0:
    print(f'The following files were found to be unique between both directories:')
    for e in difference:
        print(f'{e}')  
else: print ("Both directories have the same files")