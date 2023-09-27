# Witten by: Harald Steiner, Harald.steiner@gov.bc.ca
# Copyright: Provincial Government of BC , May 2022
# Open file dialog box and create a file list 

import easygui as eg

def get_filenames(text1,f_type,title,file_desc,FLAG):
    file_list=eg.fileopenbox(text1, title,default=f_type, filetypes= [f_type,[f_type,file_desc] ], multiple=True)
    return file_list

