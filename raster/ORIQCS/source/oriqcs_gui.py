# ------------------------------------------------------------------------------
# ORIQCS © GeoBC
# Ortho Raster Imagery Quality Control Suite (ORIQCS)
# Pronunciation: "orks", "oh-rix"
# ------------------------------------------------------------------------------
# GUI module for GeoBC's ortho, raster, and imagery QC tests
# Original author: Sam May
# Updates by: Natalie Jackson
# ------------------------------------------------------------------------------

from datetime import datetime
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from multiprocessing import freeze_support
import oriqcs_config

import progressbar
import os
import base64
import time
import glob
import errno
import random
import traceback
import config
import math
import re


# ------------------------------------------------------------------------------
# Update the software name here to change the ORIQCS version number.
# It also needs to be changed in the oriqcs_gui.spec file.
# ------------------------------------------------------------------------------

def _software_name():
    return "ORIQCS v.2.1.8"


# ------------------------------------------------------------------------------
# Testing parameters - populate the the input and output directory parameters
# so they don't need to be navigated to when testing this script
# ------------------------------------------------------------------------------

# Set to True to use hard-coded input directory and create a new
# timestamped output directory in a hard-coded location.
# Set to False before compiling executable.
oriqcs_testing = False

# Set to True to delete previous test outputs in the the test output folder
# (only relevant if oriqcs_testing is True)
delete_previous_outputs = False

# Set to True to pop open the test output folder
# (only relevant if oriqcs_testing is True)
open_output_folder = False

if oriqcs_testing:
    # Testing input directory
    default_indir = (
        r'C:\CODE_DEVELOPMENT\_QC_repo_local_NJ_DD050861\imagery\ORiQCS\source\test_files\INPUT\orthophoto_limit_inputs'
    )

    # Testing output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_outdir_parent = (
        r"C:\CODE_DEVELOPMENT\_QC_repo_local_NJ_DD050861\imagery\ORiQCS\source\test_files"
    )
    test_outdir_prefix = "oriqcs_test_output_"
    default_outdir = os.path.join(
        default_outdir_parent,
        f"{test_outdir_prefix}{timestamp}"
    )

    # Delete old output folders
    if delete_previous_outputs:
        for item in os.listdir(default_outdir_parent):
            if item.startswith(test_outdir_prefix):
                import shutil
                shutil.rmtree(os.path.join(default_outdir_parent, item))

    if not os.path.isdir(default_outdir):
        os.mkdir(default_outdir)

    if open_output_folder:
        import subprocess
        subprocess.Popen(f'explorer.exe {default_outdir}')

else:
    default_indir = None
    default_outdir = None


# ------------------------------------------------------------------------------
# Some parts of the main GUI are replicated in the 'edit queue' popup,
# and other parts of this script.
# To ensure the labels of these elements are the same in multiple places,
# here are some functions to use by all similar items or cross-references.
# ------------------------------------------------------------------------------

def _io_frame_label():
    return "Set input and output directories"


def _input_frame_label():
    return (
        "Input directory path or .txt path (.txt contains list of input file paths)"
    )


def _output_frame_label():
    return "Output directory path"


def _choose_input_directory_button_text():
    return "Browse to input\ndirectory"


def _choose_output_directory_button_text():
    return "Browse to output\ndirectory"


def _select_input_directory_popup_title():
    return "Select input directory"


def _select_output_directory_popup_title():
    return "Select output directory"


def _file_list_button_text():
    return "Browse to file list\n.txt file"


def _search_subdirectories_checkbutton_text():
    return "Include subdirectories"


def _select_clear_all_button_text():
    return "Select/clear all"


def _default_tests_frame_label():
    return "Default tests"


def _percentage_of_files_label():
    return "Percentage of files to test: ", "%"


def _core_frame_label():
    return "Choose number of cores for processing"


def _cores_label():
    return "Cores: "


def _test_frame_label():
    return "Tests:"


def _choose_tests_frame_label():
    return "Choose tests to run on input data"


def _process_queue_button_text():
    return "Process queue"


def _quit_button_text():
    return "Quit"


# ------------------------------------------------------------------------------
# Formatting
# ------------------------------------------------------------------------------

def _dashline():
    """
    Get the dashline string from the config file.

    Returns:
        string: 80 hyphens with new line characters before and after
    """
    return config.DASHLINE


# ------------------------------------------------------------------------------
# Class for the ORIQCS gui
# ------------------------------------------------------------------------------

class ORIQCS_GUI:
    """
    ORIQCS GUI class.
    """
    def __init__(self):
        """
        Initialize the ORIQCS GUI attributes
        and run the populate_gui() function.
        """
        self.root = Tk()
        self.root.title(_software_name())
        self.root.resizable(width=False, height=False)
        self.queueDict = {}
        self.queueItemFrames = []
        self.populate_gui()

    def populate_gui(self):
        """
        Generates the main ORIQCS GUI.
        """

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # top_frame (populate_gui) - makes up top of GUI, contains test options,
        # input and output path select
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        top_frame = Frame(self.root)
        top_frame.grid(row=0, column=0, padx=(64, 64), pady=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # io_frame (populate_gui) - Houses Input, Output, and Core Frames
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        io_frame = ttk.LabelFrame(
            top_frame,
            text=_io_frame_label()
        )
        io_frame.grid(row=0, column=0, padx=5, pady=5, sticky=W)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # input_frame (populate_gui) - Select input directory
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        input_frame = ttk.LabelFrame(
            io_frame,
            text=_input_frame_label()
        )
        input_frame.grid(row=0, column=0, padx=5)
        self.input_entry = StringVar(value=default_indir)
        ttk.Entry(
            input_frame,
            width=40,
            textvariable=self.input_entry
        ).grid(row=0, column=0)
        ttk.Button(
            input_frame,
            text=_choose_input_directory_button_text(),
            command=lambda: self.path_select(
                self.input_entry,
                _select_input_directory_popup_title()
            )
        ).grid(row=0, column=1, sticky=W)
        ttk.Button(
            input_frame,
            text=_file_list_button_text(),
            command=lambda: self.file_list_select(self.input_entry)
        ).grid(row=0, column=2)

        self.recurse = IntVar()
        recurse_entry = ttk.Checkbutton(
            input_frame,
            text=_search_subdirectories_checkbutton_text(),
            variable=self.recurse,
            onvalue=1,
            offvalue=0
        )
        recurse_entry.grid(row=1, column=0)

        percent_frame = Frame(input_frame)
        percent_frame.grid(row=2, column=0)
        ttk.Label(
            percent_frame,
            text=_percentage_of_files_label()[0]
        ).grid(row=0, column=0)
        self.sample_size = StringVar(value=100)
        ttk.Entry(
            percent_frame,
            width=3,
            textvariable=self.sample_size
        ).grid(row=0, column=1)
        ttk.Label(
            percent_frame,
            text=_percentage_of_files_label()[1]
        ).grid(row=0, column=2)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # output_frame (populate_gui) - Select output directory
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        output_frame = ttk.LabelFrame(
            io_frame,
            text=_output_frame_label()
        )
        output_frame.grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.output_entry = StringVar(value=default_outdir)
        ttk.Entry(
            output_frame,
            width=40,
            textvariable=self.output_entry
        ).grid(row=0, column=0)
        ttk.Button(
            output_frame,
            text=_choose_output_directory_button_text(),
            command=lambda: self.path_select(
                self.output_entry,
                _select_output_directory_popup_title()
            )
        ).grid(row=0, column=1, padx=2, pady=4, sticky=W)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # core_frame (populate_gui)
        # - Select number of processor cores from drop down menu
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        core_frame = ttk.LabelFrame(
            top_frame,
            text=_core_frame_label()
        )
        core_frame.grid(row=1, column=0, pady=0, sticky=W)
        ttk.Label(
            core_frame,
            text=_cores_label()
        ).grid(row=0, column=0)

        # Core selection combobox
        self.core_select = StringVar()
        core_options = ttk.Combobox(
            core_frame,
            textvariable=self.core_select,
            state="readonly",
            width=9,
            height=9
        )

        core_options['values'] = self._core_options_values()

        core_options.current(3)
        core_options.grid(row=0, column=1)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # config_frame (populate_gui) - contains Add to queue button
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        config_frame = Frame(self.root)
        config_frame.grid(row=1, column=0, pady=(20, 0))

        ttk.Button(
            config_frame,
            text="Add to queue",
            padding=20,
            command=lambda: self.add_to_queue(
                self.chkbList,
                self.core_select.get(),
                self.recurse.get(),
                self.sample_size.get(),
                self.input_entry.get(),
                self.output_entry.get()
            )
        ).grid(row=3, column=0, pady=(0, 5))

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # outer_test_frame (populate_gui)
        # - contains testFrame and default_tests_frame
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        outer_test_frame = ttk.LabelFrame(
            top_frame,
            text=_choose_tests_frame_label()
        )
        outer_test_frame.grid(row=0, column=1, padx=5, rowspan=2)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # testFrame (populate_gui) - contains all test options
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        testFrame = ttk.LabelFrame(
            outer_test_frame,
            text=_test_frame_label()
        )
        testFrame.grid(row=0, column=0, padx=5)
        chkbFrame = Frame(testFrame)
        chkbFrame.grid(row=0, column=0)
        selectFrame = Frame(testFrame)
        selectFrame.grid(row=1, column=0)

        self.chkbList = [IntVar() for i in range(len(oriqcs_config.FULL_TEST_LIST))]

        testRowNum = 0
        testColumnNum = 0
        for i in range(len(self.chkbList)):
            chkb = ttk.Checkbutton(chkbFrame, text=oriqcs_config.FULL_TEST_LIST[i]['testText'], variable=self.chkbList[i])
            if testRowNum >= 5:
                testRowNum = 0
                testColumnNum = testColumnNum + 2
            chkb.grid(row=testRowNum, column=testColumnNum, sticky='W')
            testRowNum += 1
        
        ttk.Button(
            selectFrame,
            text=_select_clear_all_button_text(),
            command=lambda: self.select_trigger(self.chkbList)
        ).grid(row=0, column=0, pady=5, sticky='WE')

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Default Tests (populate_gui)
        # - Contains buttons that select tests in chkblist
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        default_tests_frame = ttk.LabelFrame(
            outer_test_frame,
            text=_default_tests_frame_label()
        )
        default_tests_frame.grid(row=0, column=1, padx=5)
        default_test_dict = self._default_test_dict()
        default_test_dict_keys = list(default_test_dict)
        default_test_buttons_column = 0
        default_test_button_padx = 5
        default_test_buttons_pady = 4
        default_test_buttons_sticky = W
        ttk.Button(
            default_tests_frame,
            text=self._default_test_button_text(0),
            command=lambda: self.default_test_select(
                self.chkbList,
                default_test_dict_keys[0]
            )
        ).grid(
            row=0,
            column=default_test_buttons_column,
            padx=default_test_button_padx,
            pady=default_test_buttons_pady,
            sticky=default_test_buttons_sticky
        )
        ttk.Button(
            default_tests_frame,
            text=self._default_test_button_text(1),
            command=lambda: self.default_test_select(
                self.chkbList,
                default_test_dict_keys[1]
            )
        ).grid(
            row=1,
            column=default_test_buttons_column,
            padx=default_test_button_padx,
            pady=default_test_buttons_pady,
            sticky=default_test_buttons_sticky
        )
        ttk.Button(
            default_tests_frame,
            text=self._default_test_button_text(2),
            command=lambda: self.default_test_select(self.chkbList, default_test_dict_keys[2])
        ).grid(
            row=2,
            column=default_test_buttons_column,
            padx=default_test_button_padx,
            pady=default_test_buttons_pady,
            sticky=default_test_buttons_sticky
        )
        ttk.Button(
            default_tests_frame,
            text=self._default_test_button_text(3),
            command=lambda: self.default_test_select(self.chkbList, default_test_dict_keys[3])
        ).grid(
            row=3,
            column=default_test_buttons_column,
            padx=default_test_button_padx,
            pady=default_test_buttons_pady,
            sticky=default_test_buttons_sticky
        )

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # queue_action_frame (populate_gui)
        # - Queue process and clear buttons
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        queue_action_frame = Frame(self.root)
        queue_action_frame.grid(row=3, column=0, pady=5)
        ttk.Button(
            queue_action_frame,
            text=_process_queue_button_text(),
            command=lambda: self.run_tests(),
            padding=20
        ).grid(row=0, column=0, padx=10)
        ttk.Button(
            queue_action_frame,
            text="Clear queue",
            padding=20,
            command=lambda: self.clear_queue()
        ).grid(row=0, column=1, padx=10)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # software_frame (populate_gui)
        # - Quit and info buttons
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        software_frame = Frame(self.root)
        software_frame.grid(row=4, column=0, pady=(5, 10))
        ttk.Button(
            software_frame,
            text="Help",
            command=lambda: self.help_page()
        ).grid(row=0, column=0, padx=4)
        ttk.Button(
            software_frame,
            text="About",
            command=lambda: self.about_page()
        ).grid(row=0, column=1, padx=4)
        ttk.Button(
            software_frame,
            text=_quit_button_text(),
            command=self.root.destroy
        ).grid(row=0, column=2, padx=4)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # queueFrame (populate_gui)
        #  - Contains queue of tests to be run
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.queueFrame = ScrollingFrame(self.root)
        self.queueFrame.grid(row=2, column=0, pady=5, padx=5, sticky="WE")

        self.innerQueueFrame = self.queueFrame.frame

    def run_tests(self):
        """
        Passes queue dictionary to relevent imagery scripts.
        """
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{_dashline()}ORIQCS queue started: {start_time}{_dashline()}")

        if not self.queueDict:
            print("No items in queue")
            return

        widgets = [
            progressbar.SimpleProgress(),
            ' ', progressbar.Percentage(),
            ' ', progressbar.Bar(),
            ' ', progressbar.Timer()
        ]

        with progressbar.ProgressBar(
            max_value=len(self.queueDict),
            widgets=widgets,
            redirect_stdout=True
        ) as p:
            for x in range(len(self.queueDict)):

                inDir = self.queueDict[x]['inputPath']
                outDir = self.queueDict[x]['outputPath']
                recurse = self.queueDict[x]['recurse']
                cores = self.queueDict[x]['cores']
                contract_number = self.queueDict[x]['contract_number']
                sample_size = self.queueDict[x]['sample_size']

                tifGlob, jpgGlob, sidGlob, demGlob, ascGlob, xlsxGlob = self.glob_input_files(
                    inDir,
                    self.queueDict[x]['tests'],
                    recurse, self.queueDict[x]['file_list']
                )

                if sample_size != 1.0:
                    if len(tifGlob) > 1:
                        tifGlob = self.get_percent_files(tifGlob, sample_size)
                    elif len(jpgGlob) > 1:
                        jpgGlob = self.get_percent_files(jpgGlob, sample_size)
                    elif len(sidGlob) > 1:
                        sidGlob = self.get_percent_files(sidGlob, sample_size)
                    elif len(demGlob) > 1:
                        demGlob = self.get_percent_files(demGlob, sample_size)
                    elif len(ascGlob) > 1:
                        ascGlob = self.get_percent_files(ascGlob, sample_size)

                fListTxt = open(outDir + '/File_List.txt', 'w+')
                if len(tifGlob) > 0:
                    fListTxt.write("Tif/Tiff:\n")
                    for file in tifGlob:
                        fListTxt.write(f"{file}\n")
                    fListTxt.write("\n")
                if len(jpgGlob) > 0:
                    fListTxt.write("Jpg/Jpeg:\n")
                    for file in jpgGlob:
                        fListTxt.write(f"{file}\n")
                    fListTxt.write("\n")
                if len(sidGlob) > 0:
                    fListTxt.write("Sid:\n")
                    for file in sidGlob:
                        fListTxt.write(f"{file}\n")
                    fListTxt.write("\n")
                if len(demGlob) > 0:
                    fListTxt.write("Dem:\n")
                    for file in demGlob:
                        fListTxt.write(f"{file}\n")
                    fListTxt.write("\n")
                if len(ascGlob) > 0:
                    fListTxt.write("Asc:\n")
                    for file in ascGlob:
                        fListTxt.write(f"{file}\n")
                    fListTxt.write("\n")
                if len(xlsxGlob) > 0:
                    fListTxt.write("Xlsx:\n")
                    for file in xlsxGlob:
                        fListTxt.write(f"{file}\n")
                    fListTxt.write("\n")
                fListTxt.close()

                FNGlob = []
                corruptGlob = []
                tifAscDemGlob = []
                FNGlob.extend(tifGlob + jpgGlob + sidGlob + ascGlob)
                corruptGlob.extend(tifGlob + jpgGlob + sidGlob)
                tifAscDemGlob.extend(tifGlob + ascGlob + demGlob)

                del jpgGlob
                del sidGlob
                del demGlob
                del ascGlob

                queueItemTime = time.time()

                sum = open(outDir + '/ORIQCS_Summary.txt', 'w+')
                sum.write(f"Input: {inDir}\n")
                sum.write(f"Output: {outDir}\n\n")
                sum.write('Tests:\n')
                exceptions = []
                # Test 1
                try:
                    if 'File Naming' in self.queueDict[x]['tests']:
                        import File_Naming
                        fileNameTime = time.time()
                        print(
                            f"Starting File Naming for queue item: {x + 1}",
                            flush=True
                        )
                        p.update(x, force=True)
                        File_Naming.run_from_gui(FNGlob, outDir, recurse)
                        print(
                            f"File Naming complete for queue item: {x + 1}\n",
                            flush=True
                        )
                        sum.write(f"File Naming: {self.get_format_time(fileNameTime)}\n")
                except Exception:
                    print(
                        "Exception occured in File Naming test."
                        "\nSee check ORIQCS_Summary.txt for details.\n"
                    )
                    exceptions.append(f"File Naming:\n{traceback.format_exc()}")

                # Test 2
                try:
                    if 'Image Corruption' in self.queueDict[x]['tests']:
                        import Image_Corruption
                        corruptionTime = time.time()
                        print(
                            f"Starting Image Corruption for queue item: {x + 1}",
                            flush=True
                        )
                        p.update(x, force=True)
                        Image_Corruption.run_from_gui(corruptGlob, outDir, recurse)
                        print(
                            f"Image Corruption complete for queue item: {x + 1}\n",
                            flush=True
                        )
                        sum.write(f"Image Corruption: {self.get_format_time(corruptionTime)}\n")
                except Exception:
                    print(
                        "Exception occured in Image Corruption test."
                        "\nSee ORIQCS_Summary.txt for details.\n"
                    )
                    exceptions.append(f"Image Corruption:\n{traceback.format_exc()}")

                # Test 3
                try:
                    if 'Validate COG' in self.queueDict[x]['tests']:
                        import Validate_COG
                        VCTime = time.time()
                        print(
                            f"Starting Validate COG for queue item: {x + 1}",
                            flush=True
                        )
                        p.update(x, force=True)
                        cog_dir = os.path.join(outDir, 'COG')
                        if 'Create COG' in self.queueDict[x]['tests'] and os.path.exists(cog_dir):
                            cogList = glob.glob(cog_dir + "/*.tif")
                            Validate_COG.run_from_gui(cogList, outDir)
                        else:
                            Validate_COG.run_from_gui(tifGlob, outDir)
                        print(
                            f"Validate COG complete for queue item: {x + 1}\n",
                            flush=True
                        )
                        sum.write(f"Validate Cog: {self.get_format_time(VCTime)}\n")
                except Exception:
                    print(
                        "Exception occured in Validate COG test."
                        "\nSee ORIQCS_Summary.txt for details.\n"
                    )
                    exceptions.append(f"Validate COG:\n{traceback.format_exc()}")
                
                # Test 4
                try:
                    if 'Check Thumbnails' in self.queueDict[x]['tests']:
                        import Check_Thumbnails
                        VCTime = time.time()
                        print(
                            f"Starting Check Thumbnails for queue item: {x + 1}",
                            flush=True
                        )
                        p.update(x, force=True)
                        Check_Thumbnails.run_from_gui(inDir, outDir)
                        print(
                            f"Check Thumbnails complete for queue item: {x + 1}\n",
                            flush=True
                        )
                        sum.write(f"Check Thumbnails: {self.get_format_time(VCTime)}\n")
                except Exception:
                    print(
                        "Exception occured in Check Thumbnails test."
                        "\nSee ORIQCS_Summary.txt for details.\n"
                    )
                    exceptions.append(f"Check Thumbnails:\n{traceback.format_exc()}")
                
                # Test 5
                try:
                    if 'Metadata' in self.queueDict[x]['tests']:
                        import Check_Metadata
                        metadataTime = time.time()
                        print(
                            f"Starting Metadata check for queue item: {x + 1}",
                            flush=True
                        )
                        p.update(x, force=True)
                        Check_Metadata.run_from_gui(
                            xlsxGlob,
                            outDir,
                            # self.queueDict[x]['gsd'],
                            self.queueDict[x]['solarAngle']
                        )
                        print(
                            f"Metadata check complete for queue item: {x + 1}\n",
                            flush=True
                        )
                        sum.write(f"Metadata: {self.get_format_time(metadataTime)}\n")
                except Exception:
                    print(
                        "Exception occured in Metadata test"
                        "\nSee check ORIQCS_Summary.txt for details.\n")
                    exceptions.append(f"Metadata:\n{traceback.format_exc()}")

                # Test 6
                try:
                    if 'Tile Index' in self.queueDict[x]['tests']:
                        import Tile_Index
                        ICITime = time.time()
                        print(
                            f"Starting Tile Index for queue item: {x + 1}",
                            flush=True
                        )
                        p.update(x, force=True)
                        
                        tifNoDensityList=[]
                        reDensity = '(d|D)ensity'
                        for file in tifGlob:
                            if re.search(reDensity, os.path.basename(file)) is None:
                                tifNoDensityList.append(file)

                        Tile_Index.run_from_gui(
                            tifNoDensityList,
                            outDir,
                            cores,
                            contract_number,
                            
                        )
                        print(
                            f"Tile Index complete for queue item: {x + 1}\n",
                            flush=True
                        )
                        sum.write(f"Tile Index: {self.get_format_time(ICITime)}\n")
                except Exception:
                    print(
                        "Exception occured in Tile Index test."
                        "\nSee ORIQCS_Summary.txt for details.\n"
                    )
                    exceptions.append(f"Tile Index:\n{traceback.format_exc()}")

                # Test 7
                try:
                    if 'Header Report' in self.queueDict[x]['tests']:
                        import header_report
                        imgSumTime = time.time()
                        print(
                            f"Starting Header Report for queue item: {x + 1}",
                            flush=True
                        )
                        p.update(x, force=True)
                        header_report.run_from_gui(
                            inDir,
                            outDir,
                            tifAscDemGlob,
                            recurse,
                            cores
                        )
                        print(
                            f"Header Report complete for queue item: {x + 1}\n",
                            flush=True
                        )
                        sum.write(
                            f"Header Report: {self.get_format_time(imgSumTime)}\n"
                        )
                except Exception:
                    print(
                        "Exception occured in Header Report test."
                        "\nSee ORIQCS_Summary.txt for details.\n"
                    )
                    exceptions.append(f"Header Report:\n{traceback.format_exc()}")
                
                # Test 8
                try:
                    if 'Histogram RGB' in self.queueDict[x]['tests']:
                        import Histogram_RGB_Batch
                        histTime = time.time()
                        print(f"Starting Histogram RGB for queue item: {x + 1}", flush=True)
                        p.update(x, force=True)
                        Histogram_RGB_Batch.run_from_gui(inDir, outDir, tifGlob, recurse, cores)
                        print(
                            f"Histogram RGB complete for queue item: {x + 1}\n",
                            flush=True
                        )
                        sum.write(
                            f"Histogram RGB: {self.get_format_time(histTime)}\n"
                        )
                except Exception:
                    print(
                        "Exception occured in Histogram RGB test."
                        "\nSee check ORIQCS_Summary.txt for details.\n"
                    )
                    exceptions.append(f"Histogram RGB:\n{traceback.format_exc()}")
                
                # Test 9
                try:
                    if 'Valid Image Area' in self.queueDict[x]['tests']:
                        import Valid_Image_Area
                        VIATime = time.time()
                        print(
                            f"Starting Valid Image Area for queue item: {x + 1}",
                            flush=True
                        )
                        p.update(x, force=True)
                        Valid_Image_Area.run_from_gui(
                            tifGlob,
                            outDir,
                            self.queueDict[x]['nodata']
                        )
                        print(
                            f"Valid Image Area complete for queue item: {x + 1}\n",
                            flush=True
                        )
                        sum.write(f"Valid Image Area: {self.get_format_time(VIATime)}\n")
                except Exception:
                    print(
                        "Exception occured in Valid Image Area test."
                        "\nSee ORIQCS_Summary.txt for details.\n"
                    )
                    exceptions.append(f"Valid Image Area:\n{traceback.format_exc()}")

                # Test 10
                try:
                    if 'QC Prep' in self.queueDict[x]['tests']:
                        import QC_prep
                        QCPrepTime = time.time()
                        print(
                            f"Starting QC Prep for queue item: {x + 1}",
                            flush=True
                        )
                        p.update(x, force=True)
                        if self.queueDict[x]['lidarDir'] is not None:
                            QC_prep.run_from_gui(
                                tifGlob,
                                outDir,
                                self.queueDict[x]['lidarDir'],
                                recurse,
                                cores,
                                self.queueDict[x]['orthoSample']
                            )
                        else:
                            QC_prep.run_from_gui(
                                tifGlob,
                                outDir,
                                None,
                                recurse,
                                cores,
                                self.queueDict[x]['orthoSample']
                            )
                        print(
                            f"QC Prep complete for queue item: {x + 1}\n",
                            flush=True
                        )
                        sum.write(
                            f"QC Prep: {self.get_format_time(QCPrepTime)}\n"
                        )
                except Exception:
                    print(
                        "Exception occured in QC Prep test."
                        "\nSee ORIQCS_Summary.txt for details.\n"
                    )
                    exceptions.append(f"QC Prep:\n{traceback.format_exc()}")

                # Test 11
                try:
                    if 'Create COG' in self.queueDict[x]['tests']:
                        import Create_COG
                        CCTime = time.time()
                        print(
                            f"Starting Create COG for queue item: {x + 1}",
                            flush=True
                        )
                        p.update(x, force=True)
                        Create_COG.run(tifAscDemGlob, outDir)
                        print(
                            f"Create COG complete for queue item: {x + 1}\n",
                            flush=True
                        )
                        sum.write(f"Create Cog: {self.get_format_time(CCTime)}\n")
                except Exception:
                    print(
                        "Exception occured in Create Cog test."
                        "\nSee ORIQCS_Summary.txt for details.\n"
                    )
                    exceptions.append(f"Create Cog:\n{traceback.format_exc()}")

                TotalTime = self.get_format_time(queueItemTime)
                sum.write('\n')
                sum.write(f'Runtime: {TotalTime}\n')
                sum.write(f"Time Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                if len(exceptions) > 0:
                    sum.write("\n\nExceptions:\n")
                    for exception in exceptions:
                        sum.write(f"{exception}\n\n")
                sum.close()

                p.update(x)
                print(
                    f"Finished queue item: {x + 1}"
                    f"\nRuntime: {TotalTime}{_dashline()}\n"
                    f"\n\nView queue item {x + 1} outputs here:"
                    f"\n\t{outDir}"
                    f"{_dashline()}"
                )

        print(
            f"All queue items complete!"
            f"{_dashline()}To run more ORIQCS tests, add more items to the queue "
            f"in the GUI and click the '{_process_queue_button_text()}' button."
            "\n\nTo quit ORIQCS, close this window (kill terminal), "
            f"or click the '{_quit_button_text()}' button in the GUI."
        )

        self.clear_queue()

    def add_to_queue(
        self,
        chkbList,
        cores,
        recurse,
        sample_size,
        inputPath,
        outputPath,
        queuePointer=None
    ):
        """
        Takes in a list of tests, input and output paths, creates queue object
        """
        testList = []
        for t in range(len(chkbList)):
            if type(chkbList[t]) == IntVar:
                if chkbList[t].get() == 1:
                    testList.append(oriqcs_config.FULL_TEST_LIST[t]['testName'])

        # Check if there's tests selected
        if len(testList) == 0:
            messagebox.showerror(
                "Input error",
                "No tests selected! Please select one or more tests."
            )
            return

        # check if input exists
        if not os.path.exists(inputPath):
            messagebox.showerror(
                "Input Error",
                "Input path does not exist, please select another path."
            )
            if queuePointer:
                self.edit_queue()
            return

        try:
            sample_size = int(sample_size)
        except ValueError:
            messagebox.showerror(
                "Percentage error",
                "Invalid value for percentage"
            )
            return

        if sample_size > 100:
            sample_size = 100
        sample_size /= 100

        if cores == "Default (4)":
            cores = 4
        else:
            cores = int(cores)

        try:
            if inputPath.split(".")[1] == 'txt':
                file_list = True
            else:
                file_list = False

        except IndexError:
            file_list = False

        tifGlob, jpgGlob, sidGlob, demGlob, ascGlob, xlsxGlob = self.glob_input_files(
            inputPath,
            testList,
            recurse,
            file_list
        )

        FNGlob = []
        corruptGlob = []
        tifAscDemGlob = []
        FNGlob.extend(tifGlob + jpgGlob + sidGlob + ascGlob)
        corruptGlob.extend(tifGlob + jpgGlob + sidGlob)
        tifAscDemGlob.extend(tifGlob + ascGlob + demGlob)

        if 'File Naming' in testList and len(FNGlob) < 1:
            messagebox.showerror("Input Error", "No files found for file naming check!")
            return
        elif 'Image Corruption' in testList and len(corruptGlob) < 1:
            messagebox.showerror("Input Error", "No files found for image corruption check!")
            return
        elif 'Metadata' in testList and len(xlsxGlob) < 1:
            messagebox.showerror("Input Error", "No files found for metadata check!")
            return
        elif ('Header Report', 'Create COG') in testList and len(tifAscDemGlob) < 1:
            messagebox.showerror("Input Error", "No tif, asc, or dem files found!")
            return
        elif ('Tile Index', 'Histogram RGB', 'Valid Image Area', 'Validate COG') in testList and len(tifGlob) < 1:
            messagebox.showerror("Input Error", "No tif files found!")
            return

        # Make an outputPath if it doesn't exist
        if outputPath == '':
            try:
                outputPath = os.path.join(inputPath, 'ORIQCS_results')
                os.makedirs(outputPath)
                print(f"Output path created: {outputPath}")
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    messagebox.showwarning(
                        message="Selected output path could not be created!"
                    )
                    return

        elif not os.path.exists(outputPath):
            try:
                os.makedirs(outputPath)
                print(f"Output path created: {outputPath}")
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    messagebox.showwarning(
                        message="Selected output path could not be created!"
                    )
                    return

        #epsg = None
        # gsd = None
        solarAngle = None
        contract_number = None
        nodata = None
        orthoSample = None
        lidarDir = None

        if 'Metadata' in testList:
            solarAngle = self.get_xlsx_max_values()

        if 'Tile Index' in testList:
            #epsg = self.get_EPSG()
            contract_number = self.contract_input()
            
        if 'Valid Image Area' in testList:
            nodata = self.valid_image_area_prompt()

        if 'QC Prep' in testList:
            i = 0
            while i < 2:
                i = 0
                orthoSample, lidarDir = self.get_lidar()
                try:
                    orthoSample = int(orthoSample)
                    i += 1
                except ValueError:
                    messagebox.showerror(
                        "Percentage error",
                        "Invalid value for percentage!"
                    )

                if orthoSample > 100:
                    orthoSample = 100
                orthoSample = orthoSample / 100

                if lidarDir is not None:
                    extensions = [".las", ".laz"]
                    for extension in extensions:
                        lidarGlob = glob.glob(lidarDir + "/*" + extension)
                    if len(lidarGlob) > 0:
                        i += 1
                    else:
                        messagebox.showerror(
                            "Input error",
                            "No lidar files found!"
                        )
                else:
                    i += 1

        # Point to end of queue
        if queuePointer is None:
            queuePointer = len(self.queueDict)
        self.queueDict[queuePointer] = {}
        self.queueDict[queuePointer]['inputPath'] = inputPath
        self.queueDict[queuePointer]['outputPath'] = outputPath
        self.queueDict[queuePointer]['tests'] = testList
        self.queueDict[queuePointer]['file_list'] = file_list
        self.queueDict[queuePointer]['recurse'] = recurse
        self.queueDict[queuePointer]['sample_size'] = sample_size
        self.queueDict[queuePointer]['cores'] = cores
        #self.queueDict[queuePointer]['epsg'] = epsg
        self.queueDict[queuePointer]['solarAngle'] = solarAngle
        self.queueDict[queuePointer]['contract_number'] = contract_number
        # self.queueDict[queuePointer]['gsd'] = gsd
        self.queueDict[queuePointer]['nodata'] = nodata
        self.queueDict[queuePointer]['orthoSample'] = orthoSample
        self.queueDict[queuePointer]['lidarDir'] = lidarDir
        # self.queueDict[queuePointer]['COGComp'] = COGComp

        for x in self.chkbList:
            x.set(0)
        self.input_entry.set('')
        self.output_entry.set('')
        self.recurse.set(0)
        self.sample_size.set(100)

        self.update_queue()

    def valid_image_area_prompt(self):
        popup = Toplevel()
        popup.grab_set()

        ttk.Label(
            popup,
            text="Valid Image Area test: white or black no-data?"
        ).grid(row=0, column=0, padx=14)

        buttonFrame = Frame(popup)
        buttonFrame.grid(row=1, column=0)
        blackButton = IntVar()
        whiteButton = IntVar()
        isButtonClicked = IntVar()
        white_black_button_padding = 10
        Button(
            buttonFrame,
            text="White",
            bg='white',
            fg='black',
            padx=white_black_button_padding,
            pady=white_black_button_padding,
            command=lambda: [isButtonClicked.set(1), whiteButton.set(1)]
        ).grid(row=0, column=0, padx=5, pady=10)
        Button(
            buttonFrame,
            text="Black",
            bg='black',
            fg='white',
            padx=white_black_button_padding,
            pady=white_black_button_padding,
            command=lambda: [isButtonClicked.set(1), blackButton.set(1)]
        ).grid(row=0, column=1)

        popup.wait_variable(isButtonClicked)
        if whiteButton.get() == 1:
            nodata = 255
        else:
            nodata = 0
        popup.destroy()
        return nodata

    def get_xlsx_max_values(self):

        while True:
            solarAngle = self.get_metadata_parameters()
            """"
            GSD not checked via metadata anymore

            # try:
            #     gsd = int(gsd)
            # except ValueError:
            #     print("Invalid GSD")
            #     continue
            """
            try:
                solarAngle = int(solarAngle)
            except ValueError:
                print("Invalid Solar Angle")
                continue
            else:
                break

        return solarAngle

    def open_popup_on_top_of_other_windows(self, popup):
        # Open window on top of others
        popup.attributes('-topmost', True)
        popup.update()
        # Allow other windows to go on top of it afterwards
        popup.attributes('-topmost', False)

    def contract_input(self):
        popup = Toplevel()
        self.open_popup_on_top_of_other_windows(popup)
        popup.resizable(False, False)
        popup.grab_set()
        ttk.Label(
            popup,
            text="Input Contract Number"
        ).grid(row=0, column=0, padx=5, pady=(5, 0))

        contract = StringVar()
        ttk.Entry(
            popup,
            textvariable=contract
        ).grid(row=1, column=0, padx=5, pady=5)

        isSubmitClicked = IntVar()
        shapeFileSubmit = ttk.Button(
            popup,
            text="Submit",
            command=lambda: isSubmitClicked.set(1)
        )
        shapeFileSubmit.grid(row=2, column=0, pady=(0, 5))

        popup.wait_variable(isSubmitClicked)
        popup.destroy()
        return contract.get()

    '''def get_EPSG(self):
        popup = Toplevel()
        popup.grab_set()

        epsgCodes = [
            2955,
            3157,
            3156,
            3155,
            3154,
            3005
        ]

        options = [
            "EPSG 2955: NAD83(CSRS) / UTM zone 11",
            "EPSG 3157: NAD83(CSRS) / UTM zone 10",
            "EPSG 3156: NAD83(CSRS) / UTM zone 9",
            "EPSG 3155: NAD83(CSRS) / UTM zone 8",
            "EPSG 3154: NAD83(CSRS) / UTM zone 7",
            "EPSG 3005: NAD83 / BC Albers"
        ]

        ttk.Label(
            popup,
            text="Tile Index requires defining a CRS"
        ).grid(row=0, column=0)
        ttk.Label(
            popup,
            text="Please select EPSG code: "
        ).grid(row=1, column=0)
        epsgRb = IntVar()
        isButtonClicked = IntVar()
        for i, option in enumerate(options):
            ttk.Radiobutton(
                popup,
                text=option,
                variable=epsgRb,
                value=i
            ).grid(row=i + 2, column=0, sticky='W')
        ttk.Button(
            popup,
            text="Submit",
            command=lambda: isButtonClicked.set(1)
        ).grid(row=i + 3, column=0)
        popup.wait_variable(isButtonClicked)
        popup.destroy()
        return epsgCodes[epsgRb.get()]
    '''
    
    def get_lidar(self):
        popup = Toplevel()
        popup.grab_set()

        ttk.Label(
            popup,
            text="QC Prep has additional options"
        ).grid(row=0, column=0)

        input_frame = ttk.LabelFrame(popup, text="lidar path (optional)")
        input_frame.grid(row=1, column=0, padx=5, pady=5)
        input_entry = StringVar()
        ttk.Entry(
            input_frame,
            width=40,
            textvariable=input_entry
        ).grid(row=0, column=0)
        ttk.Button(
            input_frame,
            text=_choose_input_directory_button_text(),
            command=lambda: self.path_select(
                input_entry,
                _select_input_directory_popup_title()
            )
        ).grid(row=0, column=1)

        sampleFrame = ttk.Frame(popup)
        sampleFrame.grid(row=2, column=0)
        ttk.Label(
            sampleFrame,
            text="Ortho sample size %:"
        ).grid(row=0, column=0)
        sampleEntry = StringVar(value=25)
        ttk.Entry(
            sampleFrame,
            width=2,
            textvariable=sampleEntry
        ).grid(row=0, column=1)
        isButtonClicked = IntVar()
        ttk.Button(
            popup,
            text="Submit",
            command=lambda: isButtonClicked.set(1)
        ).grid(row=3, column=0)

        popup.wait_variable(isButtonClicked)

        lidarDir = input_entry.get()
        if not os.path.exists(lidarDir):
            lidarDir = None

        orthoSample = sampleEntry.get()
        popup.destroy()
        return orthoSample, lidarDir

    def _core_options_values(self):
        core_options_values = (
            '1',
            '2',
            '3',
            'Default (4)',
            '5',
            '6',
            '7',
            '8'
        )
        return core_options_values

    def get_metadata_parameters(self):
        popup = Toplevel()
        popup.grab_set()

        ttk.Label(
            popup,
            text="Metadata check requires a minimum Solar Angle"
        ).grid(row=0, column=0)
        iFrame = Frame(popup)
        iFrame.grid(row=1, column=0)
                
        """"
        GSD not checked via metadata anymore

        # ttk.Label(iFrame, text="GSD").grid(row=0, column=0)
        # gsdEntry = StringVar()
        # ttk.Entry(
        #     iFrame,
        #     width=6,
        #     textvariable=gsdEntry
        # ).grid(row=0, column=1)
        """

        ttk.Label(iFrame, text="Solar Angle (DDMMSS)").grid(row=1, column=0)
        SAEntry = StringVar()
        ttk.Entry(iFrame, width=6, textvariable=SAEntry).grid(row=1, column=1)
        isButtonClicked = IntVar()
        ttk.Button(
            popup,
            text="Submit",
            command=lambda: isButtonClicked.set(1)
        ).grid(row=3, column=0)

        popup.wait_variable(isButtonClicked)
        popup.destroy()
        return SAEntry.get()

    def get_percent_files(self, fGlob, percent):
        # Define total sample size
        sample_size = int(len(fGlob) * percent)

        # Create empty set
        sample_set = set({})

        # While set is smaller than sample size add random samples index values
        while len(sample_set) < sample_size:

            # Generate random numbers
            i = random.randrange(0, len(fGlob))

            # Add random number index values to set
            sample_set.add(i)

        # Convert to list
        sample_set = list(sample_set)

        # Sort list
        sample_set.sort()

        # Create empty list
        sample_files = []

        # For all random integer index values in set
        for x in sample_set:

            # Index tif list to get random selection of orthos
            sample_files.append(fGlob[x])

        return sample_files

    def get_test_list_str(self, test_list, wrap_test_list_length=5):
        """
        Convert list of tests to a multiline string
        with a label and wrapping at set list increments.

        Args:
            test_list (list):
                List of tests, e.g., [
                                    'File Naming',
                                    'Image Corruption',
                                    'Tile Index',
                                    'Histogram RGB',
                                    'QC Prep',
                                    ]
            wrap_test_list_length (int, optional):
                Number of tests numbers to include on one line. Defaults to 5.

        Returns:
            str:
                Formatted text block of tests, e.g.,
                "Tests:\n
                1, 2, 4, 7, 8,\n
                9, 10"
        """
        testNumList = []
        for test in test_list:
            for i in range(len(oriqcs_config.FULL_TEST_LIST)):
                if test == oriqcs_config.FULL_TEST_LIST[i]['testName']:
                    testNumList.append(i+1)
            
        
        str_test_list = "Tests:\n"
        
        remaining_tests = testNumList

        # How many lines will the list be split into?
        num_lines_of_tests = math.ceil(len(testNumList) / wrap_test_list_length)

        # Add the list of tests to the string line-by-line
        for sets_of_x_tests in range(num_lines_of_tests):
            next_x_tests, remaining_tests = (
                remaining_tests[:wrap_test_list_length],
                remaining_tests[wrap_test_list_length:]
            )
            str_test_list += str(next_x_tests)[1:-1]

            # If it's not the last line of tests, add a comma and new line
            if sets_of_x_tests != num_lines_of_tests - 1:
                str_test_list += ",\n"

        return str_test_list

    def select_trigger(self, chkbList):
        """
        Check/uncheck all test checkboxes.
        """
        intList = [var.get() for var in chkbList]
        if 0 not in intList:
            for x in chkbList:
                x.set(0)
        else:
            for x in chkbList:
                x.set(1)

    def _default_test_dict(self):
        default_test_dict = {
            "DEM/DSM": [
            'File Naming',
            'Image Corruption', 
            'Tile Index', 
            'Header Report', 
            'QC Prep'
            ],
            "Raw imagery": [
            'File Naming', 
            'Image Corruption', 
            'Check Thumbnails'
            ],
            "Ortho imagery": [
            'File Naming', 
            'Image Corruption', 
            'Tile Index', 
            'Header Report', 
            'Valid Image Area', 
            'QC Prep'
            ],
            "DEM/DSM COGs": [
            'Validate COG',
            'Create COG'
            ]
        }
        return default_test_dict

    def _default_test_button_text(self, default_test_dict_index):
        default_test_dict = self._default_test_dict()
        default_test_dict_keys = list(default_test_dict)
        default_test_dict_nums = []
        for test in default_test_dict.get(default_test_dict_keys[default_test_dict_index]):
            for i in range(len(oriqcs_config.FULL_TEST_LIST)):
                if test == oriqcs_config.FULL_TEST_LIST[i]['testName']:
                    default_test_dict_nums.append(i+1)
        test_numbers_in_string_with_commas = str(default_test_dict_nums
        )[1:-1]
        default_test_button_text = (
            f"{default_test_dict_keys[default_test_dict_index]}"
            f"\nTests: {test_numbers_in_string_with_commas}"
        )
        return default_test_button_text

    def default_test_select(self, chkbList, test):
        # Reset all tests to unchecked
        for chkb in chkbList:
            chkb.set(0)
        testDict = self._default_test_dict()
        # Check the default tests
        for x in testDict[test]:
            for i in range(len(oriqcs_config.FULL_TEST_LIST)):
                if x == oriqcs_config.FULL_TEST_LIST[i]['testName']:
                    chkbList[i].set(1)

    def edit_queue(self, queuePointer):
        """
        After an item has been added to the queue,
        it can be edited by an Edit button.

        This function runs when that button is clicked,
        and opens a popup in which the user can edit
        the input options for the queue item.

        The pop-up contains many similar features as
        the main (root) GUI window.
        """
        popup = Toplevel()
        popup.grab_set()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # top_frame (edit_queue) - makes up top of popup, contains test options,
        # input and output path select
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        top_frame = Frame(popup)
        top_frame.grid(row=0, column=0, padx=(64, 64), pady=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # io_frame (edit_queue) -  Houses input_frame and output_frame
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        io_frame = ttk.LabelFrame(
            top_frame,
            text=_io_frame_label()
        )
        io_frame.grid(row=0, column=0, padx=5, pady=5, sticky=W)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # input_frame (edit_queue) - Select input directory
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        input_frame = ttk.LabelFrame(
            io_frame,
            text=_input_frame_label()
        )
        input_frame.grid(row=0, column=0, padx=5)
        input_entry = StringVar()
        input_entry.set(self.queueDict[queuePointer]['inputPath'])
        ttk.Entry(
            input_frame,
            width=40,
            textvariable=input_entry
        ).grid(row=0, column=0)
        ttk.Button(
            input_frame,
            text=_choose_input_directory_button_text(),
            command=lambda: self.path_select(
                input_entry,
                _select_input_directory_popup_title()
            )
        ).grid(row=0, column=1)
        ttk.Button(
            input_frame,
            text=_file_list_button_text(),
            command=lambda: self.file_list_select(input_entry)
        ).grid(row=1, column=1)

        recurse = IntVar()
        recurse.set(self.queueDict[queuePointer]['recurse'])
        recurse_entry = ttk.Checkbutton(
            input_frame,
            text=_search_subdirectories_checkbutton_text(),
            variable=recurse,
            onvalue=1,
            offvalue=0
        )
        recurse_entry.grid(row=1, column=0, sticky=W)

        percent_frame = Frame(input_frame)
        percent_frame.grid(row=2, column=0)
        ttk.Label(
            percent_frame,
            text=_percentage_of_files_label()[0]
        ).grid(row=0, column=0)
        sample_size = StringVar(
            value=int(self.queueDict[queuePointer]['sample_size'] * 100)
        )
        ttk.Entry(
            percent_frame,
            width=3,
            textvariable=sample_size
        ).grid(row=0, column=1)
        ttk.Label(
            percent_frame,
            text=_percentage_of_files_label()[1]
        ).grid(row=0, column=2)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # output_frame (edit_queue) - Select output directory
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        output_frame = ttk.LabelFrame(
            io_frame,
            text=_output_frame_label()
        )
        output_frame.grid(row=1, column=0, padx=5, pady=5, sticky=W)
        output_entry = StringVar()
        output_entry.set(self.queueDict[queuePointer]['outputPath'])
        ttk.Entry(
            output_frame,
            width=40,
            textvariable=output_entry
        ).grid(row=0, column=0)
        ttk.Button(
            output_frame,
            text=_choose_output_directory_button_text(),
            command=lambda: self.path_select(
                output_entry,
                _select_output_directory_popup_title()
            )
        ).grid(row=0, column=1, padx=2, pady=4)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # core_frame (edit_queue)
        # - Select number of processor cores from drop down menu
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        core_frame = ttk.LabelFrame(
            top_frame,
            text=_core_frame_label()
        )
        core_frame.grid(row=1, column=0, pady=0, sticky=W)
        ttk.Label(
            core_frame,
            text=_cores_label()
        ).grid(row=0, column=0)

        # Core selection combobox
        core_select = StringVar()
        core_options = ttk.Combobox(
            core_frame,
            textvariable=core_select,
            state="readonly",
            width=9,
            height=9
        )

        core_options['values'] = self._core_options_values()

        core_options.current(self.queueDict[queuePointer]['cores'] - 1)
        core_options.grid(row=0, column=1)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # outer_test_frame (edit_queue)
        # - contains testFrame and default_tests_frame
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        outer_test_frame = ttk.LabelFrame(
            top_frame,
            text=_choose_tests_frame_label()
        )
        outer_test_frame.grid(row=0, column=1, padx=5, rowspan=2)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # testFrame (edit_queue) - contains all test options
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        testFrame = ttk.LabelFrame(
            outer_test_frame,
            text=_test_frame_label()
        )
        testFrame.grid(row=0, column=0, padx=5)
        chkbFrame = Frame(testFrame)
        chkbFrame.grid(row=0, column=0)
        selectFrame = Frame(testFrame)
        selectFrame.grid(row=1, column=0)

        chkbList = [IntVar() for i in range(len(oriqcs_config.FULL_TEST_LIST))]

        selectedTests = self.queueDict[queuePointer]['tests']

        for i in range(len(chkbList)):
            if oriqcs_config.FULL_TEST_LIST[i]['testName'] in selectedTests:
                chkbList[i].set(1)

        testRowNum = 0
        testColumnNum = 0
        for i in range(len(chkbList)):
            chkb = ttk.Checkbutton(chkbFrame, text=oriqcs_config.FULL_TEST_LIST[i]['testText'], variable=chkbList[i])
            if testRowNum >= 5:
                testRowNum = 0
                testColumnNum = testColumnNum + 2
            chkb.grid(row=testRowNum, column=testColumnNum, sticky='W')
            testRowNum += 1
    
        ttk.Button(
            selectFrame,
            text=_select_clear_all_button_text(),
            command=lambda: self.select_trigger(chkbList)
        ).grid(row=0, column=0, pady=5, sticky='WE')

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Default Tests (edit_queue)
        # - Contains buttons that select tests in chkblist
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        default_tests_frame = ttk.LabelFrame(
            outer_test_frame,
            text=_default_tests_frame_label()
        )
        default_tests_frame.grid(row=0, column=1, padx=5)
        default_test_dict = self._default_test_dict()
        default_test_dict_keys = list(default_test_dict)
        default_test_buttons_column = 0
        default_test_button_padx = 5
        default_test_buttons_pady = 4
        default_test_buttons_sticky = W
        ttk.Button(
            default_tests_frame,
            text=self._default_test_button_text(0),
            command=lambda: self.default_test_select(
                chkbList,
                default_test_dict_keys[0]
            )
        ).grid(
            row=0,
            column=default_test_buttons_column,
            padx=default_test_button_padx,
            pady=default_test_buttons_pady,
            sticky=default_test_buttons_sticky
        )
        ttk.Button(
            default_tests_frame,
            text=self._default_test_button_text(1),
            command=lambda: self.default_test_select(
                chkbList,
                default_test_dict_keys[1]
            )
        ).grid(
            row=1,
            column=default_test_buttons_column,
            padx=default_test_button_padx,
            pady=default_test_buttons_pady,
            sticky=default_test_buttons_sticky
        )
        ttk.Button(
            default_tests_frame,
            text=self._default_test_button_text(2),
            command=lambda: self.default_test_select(
                chkbList,
                default_test_dict_keys[2]
            )
        ).grid(
            row=2,
            column=default_test_buttons_column,
            padx=default_test_button_padx,
            pady=default_test_buttons_pady,
            sticky=default_test_buttons_sticky
        )
        ttk.Button(
            default_tests_frame,
            text=self._default_test_button_text(3),
            command=lambda: self.default_test_select(
                chkbList,
                default_test_dict_keys[3]
            )
        ).grid(
            row=3,
            column=default_test_buttons_column,
            padx=default_test_button_padx,
            pady=default_test_buttons_pady,
            sticky=default_test_buttons_sticky
        )

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # buttonFrame (edit_queue)
        # - contains Save, Discard, and Delete buttons in the edit popup
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        buttonFrame = Frame(popup)
        buttonFrame.grid(row=1, column=0, pady=10)

        buttonClicked = IntVar()
        saveClicked = IntVar(value=0)
        doneClicked = IntVar()
        buttonFrame = Frame(popup)
        buttonFrame.grid(row=1, column=0, pady=(0, 5))

        ttk.Button(
            buttonFrame,
            text="Save",
            command=lambda: [saveClicked.set(value=1), buttonClicked.set(1)]
        ).grid(row=0, column=0)
        ttk.Button(
            buttonFrame,
            text="Discard Changes",
            command=lambda: [doneClicked.set(1), buttonClicked.set(1)]
        ).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(
            buttonFrame,
            text="Delete",
            command=lambda: [
                self.delete_queue(queuePointer),
                buttonClicked.set(1),
                doneClicked.set(1)
            ]
        ).grid(row=0, column=2)

        popup.wait_variable(buttonClicked)

        if saveClicked.get() == 1:
            self.add_to_queue(
                chkbList,
                core_select.get(),
                recurse.get(),
                sample_size.get(),
                input_entry.get(),
                output_entry.get(),
                queuePointer
            )
            popup.destroy()

        popup.wait_variable(doneClicked)
        popup.destroy()

    def get_format_time(self, totalTime):
        """
        _summary_

        Args:
            totalTime (_type_): _description_

        Returns:
            _type_: _description_
        """
        raw_time = time.time() - totalTime
        hours = int(raw_time // 3600)
        minutes = int((raw_time % 3600) // 60)
        seconds = int((raw_time % 3600) % 60)
        FormattedTime = f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}"
        return FormattedTime

    def glob_input_files(self, input_path, testList, recurse, file_list):
        """_summary_

        Args:
            input_path (_type_): _description_
            testList (_type_): _description_
            recurse (_type_): _description_
            file_list (_type_): _description_

        Returns:
            _type_: _description_
        """
        infile_glob = []
        extensions = []

        if 'Metadata' in testList:
            extensions.append(".xlsx")
        if ('File Naming', 'Image Corruption') in testList:
            extensions.extend([".sid", ".jpg", ".jpeg"])
        if ('Header Report', 'Create COG') in testList:
            extensions.append(".dem")
        if ('File Naming', 'Header Report', 'Create COG') in testList:
            extensions.append(".asc")
        if testList != ['Metadata']:
            extensions.extend([".tif", ".tiff"])

        if file_list is False:
            for extension in extensions:
                if recurse == 1:
                    infile_glob.extend(
                        glob.glob(input_path + "\**/*" + extension, recursive=True)
                    )
                else:
                    infile_glob.extend(glob.glob(input_path + "/*" + extension))
        else:
            with open(input_path, 'r') as f:
                line_strip = [line.strip() for line in f]
            for line in line_strip:
                if os.path.isfile(line):
                    if os.path.splitext(line)[1] in extensions:
                        infile_glob.append(line)
        tifGlob = []
        jpgGlob = []
        sidGlob = []
        demGlob = []
        ascGlob = []
        xlsxGlob = []

        for file in infile_glob:
            if os.path.splitext(file)[1] in (".tif", ".tiff"):
                tifGlob.append(file)
            elif os.path.splitext(file)[1] in (".jpg", ".jpeg"):
                jpgGlob.append(file)
            elif os.path.splitext(file)[1] in ".xlsx":
                xlsxGlob.append(file)
            elif os.path.splitext(file)[1] in ".sid":
                sidGlob.append(file)
            elif os.path.splitext(file)[1] in ".dem":
                demGlob.append(file)
            elif os.path.splitext(file)[1] in ".asc":
                ascGlob.append(file)
        del infile_glob

        return tifGlob, jpgGlob, sidGlob, demGlob, ascGlob, xlsxGlob

    def delete_queue(self, queuePointer):
        lastQueuePos = len(self.queueDict) - 1

        del self.queueDict[queuePointer]

        # idx of first queueDict that needs to be changed
        posChange = lastQueuePos - queuePointer

        # print("# of queue items need to be changed: ", posChange)

        if queuePointer < lastQueuePos:

            for n in range(posChange):
                queueMove = queuePointer + 1 + n
                # print("queueMove: ", queueMove)

                if (queueMove) == lastQueuePos:
                    self.queueDict[queueMove - 1] = self.queueDict[queueMove]
                    # print('last in queue: ', self.queueDict[queueMove-1])
                    del self.queueDict[lastQueuePos]
                    break
                else:
                    # print('queue move: ', queueMove)
                    self.queueDict[queueMove - 1] = self.queueDict[queueMove]
                    # print('not last in queue: ', self.queueDict[queueMove-1])

        self.update_queue()

    def update_queue(self):
        """
        Destory all queueItemFrames rebuild using queueDict.
        """
        for x in range(len(self.queueItemFrames)):
            self.queueItemFrames[x].destroy()

        self.queueItemFrames = []
        i = 0
        rowNum = 0

        for i in range(len(self.queueDict)):

            input_str = f"Input directory:\n{self.queueDict[i]['inputPath']}"
            output_str = f"Output directory:\n{self.queueDict[i]['outputPath']}"

            tests_str = self.get_test_list_str(self.queueDict[i]['tests'])

            cores_str = f"Cores: {self.queueDict[i]['cores']}"

            percentage_to_test_str = (
                f"Files to test:\n{int(self.queueDict[i]['sample_size'] * 100)}%"
            )

            self.queueItemFrames.append(
                ttk.LabelFrame(
                    self.innerQueueFrame,
                    width=450,
                    height=100,
                    text=i + 1,
                )
            )

            # Position the queue item frame in the queue frame
            self.queueItemFrames[i].grid(
                row=rowNum,
                column=0,
                padx=4,
                pady=(0, 5)
            )
            rowNum += 1

            io_string_wraplength = '180m'  # millimetres

            # Input string
            ttk.Label(
                self.queueItemFrames[i],
                width=116,
                wraplength=io_string_wraplength,
                text=input_str
            ).grid(row=0, column=0, sticky=N)

            # Output string
            ttk.Label(
                self.queueItemFrames[i],
                width=116,
                wraplength=io_string_wraplength,
                text=output_str
            ).grid(row=1, column=0, pady=4, sticky=N)

            # Percentage of files to test string
            ttk.Label(
                self.queueItemFrames[i],
                text=percentage_to_test_str
            ).grid(row=0, column=1, padx=4, sticky=N + W)

            # Tests string
            ttk.Label(
                self.queueItemFrames[i],
                width=12,
                wraplength='24m',
                text=tests_str
            ).grid(row=0, column=2, padx=4, sticky=W)

            # Cores string
            ttk.Label(
                self.queueItemFrames[i],
                text=cores_str
            ).grid(row=1, column=2, padx=4, sticky=W)

            # Button: edit queue item
            ttk.Button(
                # self.queue_buttons_frames[i],
                self.queueItemFrames[i],
                text="Edit",
                command=lambda i=i: self.edit_queue(i)
            ).grid(row=0, column=3)

            # Button: delete queue item
            ttk.Button(
                # self.queue_buttons_frames[i],
                self.queueItemFrames[i],
                text="Delete",
                command=lambda i=i: self.delete_queue(i)
            ).grid(row=1, column=3)

        self.innerQueueFrame.update_idletasks()
        self.queueFrame.onCanvasConfigure(None)

    def clear_queue(self):
        self.queueDict = {}
        self.update_queue()

    def save_changes(
        self,
        queuePointer,
        inputPath,
        outputPath,
        chkbList,
        cores,
        recurse,
        sample_size
    ):

        self.queueDict[queuePointer]['inputPath'] = inputPath
        self.queueDict[queuePointer]['outputPath'] = outputPath
        self.queueDict[queuePointer]['cores'] = cores
        self.queueDict[queuePointer]['recurse'] = recurse

        if sample_size > 100:
            sample_size = 100
        sample_size /= 100
        self.queueDict[queuePointer]['sample_size'] = sample_size

        testList = []
        x = 0
        for x in range(len(chkbList)):
            if chkbList[x].get() == 1:
                testList.append(x + 1)
        self.queueDict[queuePointer]['tests'] = testList

        self.update_queue()

    def path_select(self, pathSV, title_text="Select directory"):
        dirPath = filedialog.askdirectory(
            initialdir="/",
            title=title_text
        )
        pathSV.set(dirPath)

    def file_list_select(self, entry):
        fileListInput = filedialog.askopenfilename(
            initialdir="/",
            filetypes=[("Text File", "*.txt")],
            title="Select .txt file containing input file paths"
        )
        entry.set(fileListInput)

    def set_icon(self):
        icon_data = base64.b64decode(config.BC_LOGO_B64)
        icon_path = os.path.join(
            os.getcwd(),
            'bc.ico'
        )

        with open(icon_path, 'wb') as icon_file:
            icon_file.write(icon_data)

        self.root.iconbitmap(icon_path)
        os.remove(icon_path)

    def about_page(self):
        messagebox.showinfo(
            "About ORIQCS",
            config.ABOUT_TEXT
        )

    def help_page(self):
        messagebox.showinfo(
            "ORIQCS Help",
            config.HELP_TEXT
        )


# ------------------------------------------------------------------------------
# Scrolling frame class
# ------------------------------------------------------------------------------

class ScrollingFrame(Frame):
    """
    ScrollingFrame class makes the queue frame scrollable.
    """
    def __init__(self, parentObject):
        ttk.LabelFrame.__init__(
            self,
            parentObject,
            text="Queue"
        )
        self.canvas = Canvas(self)
        self.frame = Frame(self.canvas)
        self.grid(sticky=E + W)

        self.vsb = Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.grid(row=0, column=1, sticky=N + S + E)

        self.canvas.grid(row=0, column=0, sticky=N + S + E + W)
        self.window = self.canvas.create_window(
            0,
            0,
            window=self.frame,
            anchor="nw",
            tags="self.frame"
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame.bind("<Configure>", self.onFrameConfigure)
        self.canvas.bind("<Configure>", self.onCanvasConfigure)

    def onFrameConfigure(self, event):
        # Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def onCanvasConfigure(self, event):
        # Resize the inner frame to match the canvas
        minHeight = self.frame.winfo_reqheight()

        if self.winfo_height() >= minHeight:
            newHeight = self.winfo_height()
            # Hide the scrollbar when not needed
            self.vsb.grid_remove()
        else:
            newHeight = minHeight
            # Show the scrollbar when needed
            self.vsb.grid()

        self.canvas.itemconfig(self.window, height=newHeight)


# ------------------------------------------------------------------------------
# "Go!"
# ------------------------------------------------------------------------------

def main():
    gui = ORIQCS_GUI()
    gui.set_icon()
    gui.root.mainloop()


if __name__ == '__main__':
    freeze_support()
    main()
