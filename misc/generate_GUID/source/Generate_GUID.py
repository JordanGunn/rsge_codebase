import re
import os,glob
import binascii
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox

# Creates GUI window

root = tk.Tk()
root.title("GeoBC GUID Generator")
root.geometry("290x180")
root.configure(bg="#9EB1CE")
root.eval('tk::PlaceWindow . center')
label = Label(root, text="Fill in Contract Number provided by GeoBC", bg="#9EB1CE")
label2 = Label(root, text="Format = OP##BMRS###", bg="#9EB1CE")
label3 = Label(root, text="# = Number", bg="#9EB1CE")
label.place(x=23, y=10)
label2.place(x=75, y=65)
label3.place(x=106, y=85)

# Entry box for Contract Number

entry = Entry(root,justify = 'center', bg="#F2F2F2", width = 20, borderwidth= 4)
entry.place(x=80,y=35)


# Encode string, convert to hexadecimal, then convert datatype back to string

def string_to_hex(arg):
    return binascii.hexlify(arg.encode()).decode()
    

# Format hexadecimal string for entry into las file header

def format_GUID(hex_string):
    while len(hex_string) < 32:        
        hex_string += '0'               
    GUID = hex_string[0:8] + '-' \
         + hex_string[8:12] + '-' \
         + hex_string[12:16] + '-' \
         + hex_string[16:20] + '-'  \
         + hex_string[20:32]
    print(f'\nGUID:\t{GUID}')           
    return GUID


# Write GUID to a text file in directory of user's choosing

def write_GUID(GUID):
    messagebox.showinfo("Choose Directory", "Choose a directory for the text file containing the GUID to be saved to.")
    cwd = filedialog.askdirectory(title="Select Directory for text file containing GUID")
    contract_number = entry.get()
    tgt = os.path.join(cwd, 'GUID_for_contract_number_' + str(contract_number) + '.txt') 
    for filename in glob.glob(cwd+"/GUID_for_Contract_Number*"):
        os.remove(filename)                 
    with open(tgt, 'a+') as f:              
        f.write(GUID)                       
    print(f'GUID written to: {tgt}')
    messagebox.showinfo("Saved", f'GUID written to: {tgt}')
    os.startfile(tgt)          


# Use pattern match to verify correctness of Contract Number and return string if matched. If matched, convert string to hexidecimal string, format to be used in LAS header and save to text file.

def prompt():
    done = False                                                                      
    regex_str = r'^OP\d{2}BMRS\d{3}$'                                               
    reg = re.compile(regex_str)                                                        
    contract_number = entry.get()                                                     
    op_string = str(contract_number)                                                                                
    while not done:                                                                    
        if bool(reg.match(op_string)):                                                  
            done = True                                                                 
            hex_string = binascii.hexlify(op_string.encode()).decode()
            GUID = format_GUID(hex_string)   
            write_GUID(GUID)
        else:
            messagebox.showinfo("Incorrect", "\n\nIncorrect Contract Number format entered.\nContract Number should be formatted as: OP##BMRS###\n\nWhere:\n\n# = Number\ne.g. OP20BMRS001\n")
            break


# Help message for Help button

def help_info():
    messagebox.showinfo("Help", help_message)

help_message = 'If you do not know the Contract Number,\nemail (lidar@gov.bc.ca)\n'

# Disclamier string
dis = "\n\nThis software is supplied as a tool for data providers to generate a GUID. " + \
"GeoBC assumes no responsibility for errors or omissions in the " + \
"software or documentation available.\n\n" + \
"In no event shall GeoBC be liable to the user or any third parties for any special, punitive, " + \
"incidental, indirect or consequential damages of any kind, or any damages whatsoever, " + \
"including, without limitation, those resulting from loss of use, data or profits, " + \
"whether or not GeoBC has been advised of the possibility of such damages, and on any theory " + \
"of liability, arising out of or in connection with the use of this software.\n\n" + \
"The use of the software downloaded through the provincial website is done at your own " + \
"discretion and risk and with agreement that you will be solely responsible for any damage " + \
"to your computer system or loss of data that results from such activities. No advice or " + \
"information, whether oral or written, obtained from GeoBC or from the provincial " + \
"website shall create any warranty for the software.\n\n" + \
"By clicking 'OK' you confirm that you have read and agree to the above disclaimer."

messagebox.showinfo("Disclaimer", dis)


# GUI buttons

submit_button = Button(root, text="Submit Contract Number", bg = '#003366', fg = 'white', command = prompt).place(x=70, y=110)
help_btn = Button(root, text="Help", bg='#FCBA19', command = help_info).place(x=127,y=145)

root.mainloop()