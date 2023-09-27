# ============================ FUTURE IDEAS ====================================
# todo Prompt user if it is a BCTS Project (business areas) or not -- will make
# todo it more complicated. =====

# todo Validation: delete any folders that were created in this process that
# todo are empty (i.e., imagery for one UTM zone only, but multiple zones in proj)

# ==============================================================================
from tkinter import *
from tkinter import Tk
from tkinter import filedialog as Fd
from tkinter import messagebox
import os
import shutil
import re
from ansi_colours import AnsiColors as colour
import logging
import datetime

# ------------------------------------------------------------------------------
# Global Variables:
QC_path = ""  # path to contract folder in LiDAR_QC server to create "LiDAR_Metadata folder"
lidar_meta_path = ""
lasinfo_path = ""
QC_server_path = "T:"
# QC_server_path = r'C:\_SAM\sandbox\lasinfo_2_QC'  # Only for testing
all_zones = []
all_checkbuttons = []
checked_zones = []  # empty list to fill with selected UTM zone checkboxes
#  todo create an empty errors.txt file to be read/used in the code
#  todo create an empty log.txt file to log run info (paths made, # of las files moved, etc)
# ------------------------------------------------------------------------------


def input_path():
    """
    User-input for navigating to LiDAR_QC_Server project folder to add datafiles
    (lasinfo) to

    Returns:
        string: path to LiDAR_QC_Server project folder
    """
    messagebox.showinfo(
        "Navigate to lidar QC Server",
        "Navigate to path of project/contract folder inside \n"
        "the proper LiDAR_QC Server year folder. "
    )
    global QC_path
    QC_path = Fd.askdirectory(
        parent=root,
        title=(
            "Select contract directory to generate lidar QC Folders for projects without business areas "
        ),
        initialdir=QC_server_path
    )

    logger.info('files2LiDAR_QC_lasinfo run: {}'.format(time))
    logger.info('lidar QC project path recorded as {}'.format(QC_path))
    print(
        f'{colour.green}'
        f'"lidar QC project path recorded as: " {QC_path}'
        f'{colour.reset}'
    )
    return QC_path


def reset_utm():
    checked_zones.clear()
    logger.debug("UTM Zones were reset!")
    print(
        f'{colour.yellow}'
        f"UTM zones were reset!"
        f'{colour.reset}')
    return checked_zones


def get_utm():
    """
    Adds user-input UTM zones into utm_zones list, from checkboxes in GUI. Only runs if a QC path has
    been set first, otherwise a warning window is populated.
    """
    all_zones = [
        "UTM08",
        "UTM09",
        "UTM10",
        "UTM11",
        "UTM12"
    ]

    if QC_path != "":
        # if len(checked_zones) == 0:
        for checked, zone in zip(all_checkbuttons, all_zones):
            if checked.get():
                checked_zones.append(zone)
        # elif len(checked_zones) != 0 and zone not in checked_zones and checked.get():
        #         # elif zone not in checked_zones and checked.get():
        #     checked_zones.append(zone)
        logger.info('UTM Zones: {} were checked/selected'.format(checked_zones))
        print(
            f'{colour.green}'
            "UTM zones: " f'{checked_zones}' " were recorded"
            f'{colour.reset}')

    else:
        messagebox.showwarning(
            "Error!",
            "You must must first input a lidar QC path!"
        )


def make_folders():
    """
    Creates a "LiDAR_Metadata folder", and UTM zone subfolders from get_utm().
    Outputs an error if user has not first directed script to the lidar QC
    contract folder.
    """
    if QC_path != "":
        global lidar_meta_path
        lidar_meta_path = os.path.join(QC_path, "LiDAR_Metadata")
        if not os.path.exists(lidar_meta_path):
            os.mkdir(lidar_meta_path)
        for zone in checked_zones:
            if not os.path.exists(os.path.join(lidar_meta_path, zone)):
                os.mkdir(os.path.join(lidar_meta_path, zone))
        logger.info('lidar Metadata folder and UTM subfolders were made here: {}'.format(lidar_meta_path))
        print(
            f'{colour.green}'
            f'lidar Metadata folder and UTM subfolders were made here: {lidar_meta_path}'
            f'{colour.reset}'
        )

    else:
        messagebox.showwarning(
            "Error!",
            "You must first input a lidar QC path!"
        )


# Lasinfo regex:
lasinfo = r'^(bc)_\d\d\d[A-Za-z]\d\d\d_\d_\d_\d_xyes_\d_(utm08|utm09|utm10|utm11|utm12)_\d\d\d\d\.txt$'


def move_lasinfo_files():
    """
    Prompts user to navigate to where lasinfo files exist.
    Uses a regex string to then find all lasinfo files, searches for UTM zones
    inside the lasinfo file, and if it matches the utm zone folder created from
    make_folders(), it will copy the lasinfo file to the appropriate UTM folder.
    """
    if QC_path != "":
        messagebox.showinfo(
            "Lasinfo Files",
            "Navigate to where lasinfo files exist"
        )

        input_path = Fd.askdirectory(
            title=("Lasinfo Input path")
        )

        all_files_list = []

        for roots, subdirs, files in os.walk(r"{}".format(input_path)):
            for file in files:
                all_files_list.append(file)
                # print(all_files_list)
            for info_file in all_files_list:
                if re.match(lasinfo, info_file):
                    for zone in checked_zones:
                        dest_folder = os.path.join(lidar_meta_path, zone)
                        if r"{}".format(zone).lower() in info_file:
                            lasinf = os.path.join(dest_folder, info_file)
                            if not os.path.exists(lasinf):
                                shutil.copy(os.path.join(roots, info_file), dest_folder)
                                
                else:
                    # todo record if info_files are a match, and they are not copied over.
                    print(
                        f'{colour.yellow}'
                        f'Other files found in directory. Copying only lasinfo files.'
                        f'{colour.reset}'
                    )

        verify_copy(input_path, lidar_meta_path)
    else:
        messagebox.showwarning(
            "Error!",
            "You must first input a lidar QC path!"
        )


def verify_copy(input, path):
    """
    Verifies if all lasinfo files from input path directory have been properly copied to the LiDAR_QC_server
    folder path. If not, a warning will be added to the run_info.log file for each file that was not copied,
    as well as output a text file with only the lasinfo files not copied listed. 

    Args:
        input (string): input path of lasinfos
        path (string): LiDAR_QC LiDAR_Metadata path where lasinfos are to be copied
    """
    for roots, dirs, files in os.walk(input):
        input_list = []
        for f in files:
            if re.match(lasinfo, f):
                input_list.append(f)
        print('input list: {}'.format(input_list))

    for roots, dirs, files in os.walk(path):
        copied_list = []
        for copied in files:
            if re.match(lasinfo, copied):
                copied_list.append(copied)
        print('copied list: {}'.format(copied_list))
    
    lasinfo_not_copied = []

    for input_file in input_list:
        if input_file not in copied_list:
            lasinfo_not_copied.append(input_file)
            logger.warning('{} was not copied to LiDAR_QC path!'.format(input_file))
        else:
            continue
    with open('{}/lasinfos_not_copied.txt'.format(path), 'a') as txt:
        txt.write("Lasinfo files that were not copied to LiDAR_QC project path:\n")
        for not_copied in lasinfo_not_copied:
            txt.write(f"{not_copied}\n")


def info_button():
    messagebox.showinfo(
        'Usage Directions/Info',
        "This program will allow you to move lasinfo files in bulk to the appropriate "
        "lidar Metadata folder on the lidar QC Server."
        "\n\n"
        "1. Navigate to the LiDAR_QC_Server project folder. "
        "If the project folder does not already exist in the path, create one."
        "\n\n"
        "2. Select the UTM zone checkbox(es) for the project, and click 'Submit UTM Zones'."
        "\n\n"
        "If you forgot to add a zone, hit 'Reset' and add in the missing zone."
        "\n\n"
        "3. Click 'Make Folders' to create a folder called 'LiDAR_Metadata'. The individual UTM zone "
        "subfolders (from step 2) will be made inside the created 'LiDAR_Metadata' folder."
        "\n\n"
        "4. Click 'Move Files', and direct the program to the root of where all lasinfo files exist "
        "(i.e., for all UTM zones). The program will then automatically search for only lasinfo files, "
        "as well as move them to their respective UTM subfolder (i.e., utm09 lasinfo files will be moved "
        "to the 'UTM09' folder created in step 3."
    )


# ------------------------------------------------------------------------------------------------------------
#                           EXECUTE SCRIPT
#  -----------------------------------------------------------------------------------------------------------
if __name__ == "__main__":

    # ----------------------------- LOGGER SETTINGS ----------------------------
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s:%(message)s')
    file_handler = logging.FileHandler('run-info.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    time = datetime.datetime.now()
    # --------------------------------------------------------------------------

    # Creates GUI window
    root = Tk()
    root.withdraw()
    root.iconbitmap(r"Z:\SPENCER_FLOYD\.ico\bc_logo.ico")
    root.title("Lasinfo files to lidar QC Server")
    root.geometry("350x235")  # width x height
    root.attributes('-topmost', True)
    root.configure(bg="#9CFFFA")
    root.eval('tk::PlaceWindow . center')
    root.resizable(width=True, height=True)
    # label = Label(root, text="Enter UTM Zones: ", bg="#8AFFFF")
    # label.grid(row=2, column=0)
    
    # utm zone checkbox intvars:
    check_zone8 = IntVar()
    check_zone9 = IntVar()
    check_zone10 = IntVar()
    check_zone11 = IntVar()
    check_zone12 = IntVar()

    all_checkbuttons = [
        check_zone8,
        check_zone9,
        check_zone10,
        check_zone11,
        check_zone12
    ]

    # lidar QC dir input button:
    button_dir = Button(
        root,
        # justify='center',
        width=17,
        text="1. lidar QC Directory",
        bg="#DD6E42",
        fg="white",
        command=input_path
    )
    button_dir.place(x=110, y=0)

    # UTM checkbuttons
    utm08 = Checkbutton(root, text="UTM08", variable=check_zone8).place(x=110, y=30)
    utm09 = Checkbutton(root, text="UTM09", variable=check_zone9).place(x=175, y=30)
    utm10 = Checkbutton(root, text="UTM10", variable=check_zone10).place(x=110, y=55)
    utm11 = Checkbutton(root, text="UTM11", variable=check_zone11).place(x=175, y=55)
    utm12 = Checkbutton(root, text="UTM12", variable=check_zone12).place(x=142.5, y=80)

    # Submit button for UTM zones:
    button_submit = Button(
        root,
        # justify='center',
        bg="#4CF39D",
        width=17,
        borderwidth=2,
        text='2. Submit UTM Zones',
        command=get_utm
    )
    button_submit.place(x=110, y=110)

    button_reset = Button(
        root,
        bg="black",
        fg="white",
        command=reset_utm,
        borderwidth=2,
        text="Reset"
    )
    button_reset.place(x=250, y=110)

    # Button for folder generation:
    button_make_folders = Button(
        root,
        # justify='center',
        bg="#4059AD",
        fg="white",
        width=17,
        borderwidth=2,
        text="3. Make Folders",
        command=make_folders
    )
    button_make_folders.place(x=110, y=140)

    # Button to move lasinfo into folder(s):
    button_move_lasinfo = Button(
        root,
        # justify='center',
        bg="#8F00FF",
        fg="white",
        width=17,
        borderwidth=2,
        text='4. Move Lasinfo Files',
        command=move_lasinfo_files
    )
    button_move_lasinfo.place(x=110, y=170)

    button_info = Button(
        root,
        # justify='center',
        bg="red",
        fg="white",
        width=10,
        borderwidth=2,
        text="Info",
        command=info_button
    )
    button_info.place(x=135, y=200)

    root.mainloop()
