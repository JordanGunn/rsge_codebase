# Created by Sam Grant
# Creates folders for __PROJECTS__ organization, prompting a user for input to where the contract,/n
# maps and PM spreadsheet template are located
# and copies these files to the appropriate generated folders.

import tkinter
from tkinter import *
from tkinter import Tk
from tkinter import filedialog as Fd
from tkinter import messagebox
import os
import shutil
import re



# ------------------------------------------------------------------------------
# Global Variables
# ------------------------------------------------------------------------------
_proj_path = r'Z:\__PROJECTS__'
_proj_path_test = r'C:\_SAM\sandbox\__PROJECTS__\OP00BMRS000'
# RSGE_contracts_path = r'C:\_SAM\sandbox\fake_contracts_folder\$'  # for testing 
RSGE_contracts_path = r'R:\2022-2023\RSGE'
path_string = ""
contract = ""
cont_path_string = ""

testing = True

if testing:
    def project_path():
        """
        Asks for dir location of the __PROJECTS__ project folder

        Returns:
            string: path to __PROJECTS__ contract folder
        """

        path_string = Fd.askdirectory(
            parent=root,
            title="Navigate to __PROJECTS__ project folder",
            initialdir=_proj_path_test
        )
        # entry.get()
        print("{} was saved as path_string".format(path_string))
        # path = path_string
        create_folders(path_string)
        # project_path_string(path_string)
        return str(path_string)

else:
    def project_path():
        """
        Asks for dir location of the __PROJECTS__ project folder

        Returns:
            string: path to __PROJECTS__ contract folder
        """
        global path_string
        path_string = Fd.askdirectory(
            parent=root,
            title="Navigate to __PROJECTS__ project folder",
            initialdir=_proj_path
        )
        # entry.get()
        print("{} was saved as path_string".format(path_string))
        # path = path_string
        create_folders(path_string)
        # project_path_string(path_string)
        return str(path_string)


def submit_contract():
    """
    Takes input from entry of contract #

    Returns:
        string: contract string
    """
    contract = entry.get()
    if contract == "":
        messagebox.showwarning(
            "Uh oh!",
            "Please enter a contract number!"
        )
    else:
        if contract.lower():
            contract = contract.upper()
            print(contract)
            return contract
        else:
            print(contract)
            return str(contract)


# List of folders to create in the __PROJECTS__ directory
folder_list = ['Contract', 'Maps', 'Metadata', 'Project_Management', 'QC', 'Supplementary']

"""
Below are the file types that go into the Metadata and Supplementary folders, after the project is 'complete':

Files that will go into the Metadata folder are:
    - lidar Metadata
    - lidar Quality Control Report
    - DEM Quality Control Report
    - Ortho-image QC Report
    - Ortho-image POsitional acc. report
    - air photo metadata

Files that will go into the Supplementary folder are:
    - lidar Calib report
    - Full LiCal results (PDF and .csv) -- make a subfolder?!
    - Final Project report
    - Ground Control & Gr. C. report
    - Photo centre index file
    - any other relevant project reports/documentation
"""


def create_folders(path_string):
    """
    Creates all required folders (empty) inside the __PROJECTS__ path

    Args:
        path_string (string): string to the __PROJECTS__ path directory

    Returns:
        _type_: _description_
    """
    for i in folder_list:
        new_path = os.path.join(path_string, i)
        if not os.path.exists(new_path):
            os.mkdir(new_path)
        # return str(new_path)


""" Variables for full path length of created contract, maps and
project_management directories: """
contract_path = os.path.join(path_string, folder_list[0])
maps_path = os.path.join(path_string, folder_list[1])
pm_path = os.path.join(path_string, folder_list[3])

# * Regexes for schedule_a, maps folder, contract number and PM spreadsheet:
contract_no = r"(?i)" + re.escape(contract) + r"-.*"
sched_a = r'^(s|S)chedule_(a|A)\.pdf$'
maps_folder = r'^Maps'
pm_spreadsheet = r'^.*\.xlsm$'


def cont_path():
    """
    Asks for dir location of the RSGE Contracts folder

    Returns:
        string: path to RSGE contracts folder
    """
    contract = entry.get()
    # year = '20{}'.format(contract[2:4])
    # print(year)

    # Below f'n trying to have the program search for the RSGE contract folder automatically, based on the 
    # entered contract number.
    for root, dirs, files in os.walk(RSGE_contracts_path):
        for dir in dirs:
            if contract in dir:
                contract_folder = os.path.join(root, dir)
        for root, dirs, files in os.walk(contract_folder):
            for folder in dirs:
                if folder == "Maps":
                    # os.chdir(os.path.join(root, folder))
                    for root, dirs, files in os.walk(os.path.join(root, folder)):
                        shutil.copy(files, os.path.join(path_string, "Maps"))
                # elif folder == "Contracts":
                #     contracts_folder = os.chdir(os.path.join(root, folder))
                #     schedule_a = re.search(sched_a, contracts_folder)
                #     if schedule_a is not None:
                #         shutil.copy(os.path.join(root, schedule_a))
                elif folder == "Project-Management":
                    # write a shortcut of the .xlsx file inside the pm_folder to the path_string (PROJECTS folder)
                    pm_folder = os.chdir(root, folder)
                    for xlsx in pm_folder:
                        search = re.search(pm_spreadsheet, xlsx)
                        if search is not None:
                            continue  # only added this so python wasn't mad about line 253.
                            # write the shortcut here.....

    # cont_path_string = Fd.askdirectory(initialdir=RSGE_contracts_path)
    # # entry.get()
    # print("This is the cont_path_string: " + cont_path_string)
    # # path = path_string
    # return str(cont_path_string)

# Intended to search for the schedule a PDF, maps folder and PM spreadsheet file.
# ! Doesn't currently run, look at the dis_proj_regex-test.py for something that might work.


def find_cont_folder():
    for root, subDirs, files in os.walk(cont_path_string):
        # Search for contract folder:
        search_cont_folder = re.search(contract_no, root)
        if search_cont_folder is not None:
            print("The contract folder '" + contract + "' was found! ")
            # print(search)
            # os.chdir(search)
            
        else:
            print("This contract not found in Contracts folder! ")
        
        # Search schedule A in files:
        search_schedA = re.search(sched_a, files)
        if search_schedA is not None:
            print("Schedule A found ")
        else:
            print("No Schedule A found ")
        
        # Search for Maps folder:
        search_maps_folder = re.search(maps_folder, subDirs)
        if search_maps_folder is not None:
            print("Maps folder found ")
        else:
            print("Maps folder not found ")


def info_button():
    messagebox.showinfo(
        'Usage Directions/Info',
        "This program will create the proper __PROJECTS__ folder structure, and populate these folders with "
        "the Schedule A and 'Maps' shapefiles from the appropriate RSGE Contracts folder based on user-input "
        "of a contract number. "
        "\n\n"
        "1. Input the Contract Number. "
        "\n\n"
        "If the a mistake is made entering the Contract Number, edit the entry and click 'Submit' again."
        "\n\n"
        "2. Click 'Select Directory' and navigate to the __PROJECTS__ project folder."
        "\n\n"
        "If you entered the wrong path/directory, simply re-click 'Select Directory'."
        "\n\n"
        "3. Click 'Contract Folder' and navigate to the root of the RSGE contracts directory, for the "
        "project year (i.e., 2022-2023). "
        "\n\n"
        "The program will find the appropriate contract folder from the entered Contract Number "
        "from Step 1 automatically."
        "\n\n"
        "4. Click 'Move Files'. The program will then create the empty folder structure inside the path from "
        "'Select Directory', and populate the empty folders with the Schedule A, the maps shapefile(s) "
        "and a shortcut to the PM Spreadsheet. "
    )


# ==============================================================================
# EXECUTE SCRIPT
# ==============================================================================
if __name__ == "__main__":

    # Creates GUI window
    root = Tk()
    root.iconbitmap(r"Z:\SPENCER_FLOYD\.ico\bc_logo.ico")
    root.title("__PROJECTS__ folder Organization 2022/23")
    root.geometry("350x180")  # width x height
    root.attributes('-topmost', True)
    root.configure(bg="#9EB1CE")
    root.eval('tk::PlaceWindow . center')
    label = Label(root, text="Enter Contract Number:", bg="#9EB1CE")
    label.pack()

    # Entry box:
    entry = Entry(root, justify='center', width=30, borderwidth=4)
    entry.pack()

    # Submit button
    submitbutton = Button(
        root,
        text="1. Submit",
        justify='center',
        command=submit_contract,
        width=10,
        borderwidth=2,
        bg="green"
    )
    submitbutton.pack()

    # # Entry box to be populated by the project_path
    # entry_path = Entry(root, justify='center', width=50, borderwidth=4)
    # entry_path.pack()

    # Button to input path of __PROJECTS__ folder
    path_button = Button(
        root,
        fg="black",
        text="2. Select Directory",
        justify='center',
        width=15,
        borderwidth=2,
        bg='light blue',
        command=project_path
    )
    path_button.pack()

    # # Entry box to be populated by the project_path
    # contract_entry_path = Entry(root, justify='center', width=50, borderwidth=4)
    # contract_entry_path.pack()

    # Button to input path of Contract folder in RSGE Contracts
    contract_button = Button(
        root,
        justify='center',
        width=15,
        text="3. Contract Folder ",
        bg='orange',
        borderwidth=2,
        command=cont_path
    )
    contract_button.pack()

    # message_enter_contract()

    button_move_files = Button(
        root,
        justify='center',
        width=15,
        text="4. Move Files",
        bg="#08415C",
        fg='white',
        borderwidth=2,
        command=find_cont_folder
    )
    button_move_files.pack()

    button_info = Button(
        root,
        justify='center',
        width=15,
        text="Info",
        bg="#08967A",
        borderwidth=2,
        command=info_button
    )
    button_info.pack()

    root.mainloop()
