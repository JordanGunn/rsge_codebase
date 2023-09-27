# ------------------------------------------------------------------------------
# GUI module for LiCal
# Written by Sam May, Graeme Prendergast, Brett Edwards,
# and Natalie Jackson, GeoBC
# ------------------------------------------------------------------------------

import base64
import os

from itertools import chain
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
from tkinter import *

import lasdecompose
import config
import lical

# ------------------------------------------------------------------------------
# Testing parameters
# ------------------------------------------------------------------------------

lical_testing = False  # Set to False/None before creating executable
open_output_dir = False  # Set to False/None before creating executable

if lical_testing:
    # Testing input directory
    default_indir = (
        r"C:\CODE_DEVELOPMENT\_QC_repo_local_NJ_DD050861\LiDAR\LiCal\test_files\calibration_laz_for342"
    )

    # Testing output directory
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_outdir_parent = (
        r"C:\CODE_DEVELOPMENT\_QC_repo_local_NJ_DD050861\LiDAR\LiCal\test_files"
    )
    default_outdir = os.path.join(
        default_outdir_parent,
        f"lical_test_output_{timestamp}"
    )
    os.mkdir(default_outdir)
    if open_output_dir:
        #  Open a file explorer window to the output directory
        import subprocess
        subprocess.Popen(f'explorer.exe {default_outdir}')

    # Testing default company
    default_company_name = "Default Company Inc"
else:
    default_indir = None
    default_outdir = None
    default_company_name = None

# ------------------------------------------------------------------------------


class LiCalGUI:
    """Class for managing LiCal's GUI and input parameters."""
    def __init__(self):
        self.master = Tk()
        self.master.title(config.SOFTWARE_NAME)
        self.master.resizable(width=False, height=False)
        self.queueDict = {}
        self.queueItemFrames = []
        self.homepage()

    def homepage(self):
        """Add all the stuff to the GUI."""
        self.master['padx'] = 10
        self.master['pady'] = 5
        self.topFrame = Frame(self.master)
        self.topFrame.grid(row=0, column=0, padx=5)
        # -------------------------------------------------------------
        # I/O Frame - This makes up the left side of the GUI
        # -------------------------------------------------------------
        self.io_frame = ttk.Frame(self.topFrame)
        self.io_frame.grid(row=0, column=0)

        # -------------------------------------------------------------
        # Input Frame - Select your infiles here!
        # -------------------------------------------------------------
        self.input_frame = ttk.LabelFrame(
            self.io_frame,
            text="Input Files",
            relief=RIDGE
        )
        self.input_frame.grid(
            row=0,
            column=0,
            padx=5,
            pady=5,
            sticky=E + W + N + S
        )

        ttk.Label(self.input_frame, text="Lidar Directory").grid(row=0, column=0)
        self.indir = StringVar(value=default_indir)
        self.dir1_entry = ttk.Entry(self.input_frame, textvariable=self.indir, width=40)
        self.dir1_entry.grid(row=0, column=1)
        self.inputType = ""
        self.dir1_button = ttk.Button(self.input_frame, text="Raw Swaths", command=self.choose_dir1)
        self.dir1_button.grid(row=0, column=2)
        self.dir2_button = ttk.Button(
            self.input_frame,
            text="Lidar Tiles",
            command=self.choose_dir2
        )
        self.dir2_button.grid(row=1, column=2)
        # ttk.Label(self.input_frame, text="Lidar Swath 2").grid(row=1, column=0)
        self.recurse = IntVar()
        self.recurse_entry = ttk.Checkbutton(
            self.input_frame,
            text="Search Subdirectories",
            variable=self.recurse,
            onvalue=1,
            offvalue=0
        )
        self.recurse_entry.grid(row=1, column=1)

        # -------------------------------------------------------------
        # Options Frame - So far, only option is test sample size %
        # -------------------------------------------------------------
        self.options_frame = ttk.LabelFrame(self.topFrame, text="Options", relief=RIDGE)
        self.options_frame.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.options_frame, text="Sample Size (%)").grid(row=0, column=0)
        self.sample_size_str = StringVar()
        self.sample_size_str.set('3')
        self.sample_size_entry = ttk.Entry(
            self.options_frame,
            textvariable=self.sample_size_str,
            width=4
        )
        self.sample_size_entry.grid(row=1, column=0, pady=(0, 5))

        ttk.Label(self.options_frame, text="RMS Error Thresholds (cm)").grid(row=2, column=0)

        self.thresholds_frame = Frame(self.options_frame)
        self.thresholds_frame.grid(row=3, column=0)

        ttk.Label(self.thresholds_frame, text="Vertical").grid(row=0, column=0, sticky=E)
        self.vertical_threshold_str = StringVar()
        self.vertical_threshold_str.set('8')
        self.vertical_threshold_entry = ttk.Entry(
            self.thresholds_frame,
            textvariable=self.vertical_threshold_str,
            width=4
        )
        self.vertical_threshold_entry.grid(row=0, column=1)

        ttk.Label(self.thresholds_frame, text="Horizontal").grid(row=1, column=0)
        self.horizontal_threshold_str = StringVar()
        self.horizontal_threshold_str.set('35')
        self.horizontal_threshold_entry = ttk.Entry(
            self.thresholds_frame,
            textvariable=self.horizontal_threshold_str,
            width=4
        )
        self.horizontal_threshold_entry.grid(row=1, column=1, pady=(0, 5))

        # -------------------------------------------------------------
        # Output Frame - So far, only for selecting output location
        # -------------------------------------------------------------
        self.output_frame = ttk.LabelFrame(self.io_frame, text="Output", relief=RIDGE)
        self.output_frame.grid(row=1, column=0)

        ttk.Label(self.output_frame, text="Report Location").grid(row=0, column=0)
        self.outdir = StringVar(value=default_outdir)
        self.outdir_entry = ttk.Entry(self.output_frame, textvariable=self.outdir, width=34)
        self.outdir_entry.grid(row=0, column=1)
        self.outdir_button = ttk.Button(
            self.output_frame,
            text="Choose Directory",
            command=self.choose_outdir
        )
        self.outdir_button.grid(row=0, column=2)

        ttk.Label(self.output_frame, text="Company Name").grid(row=1, column=0)
        self.company_name_str = StringVar(value=default_company_name)
        self.company_name_entry = ttk.Entry(
            self.output_frame,
            textvariable=self.company_name_str,
            width=34
        )
        self.company_name_entry.grid(row=1, column=1, padx=5, pady=(0, 5))
        ttk.Button(
            self.output_frame,
            text="Add To Queue",
            command=lambda: self.addToQueue(
                self.indir.get(),
                self.outdir.get(),
                self.recurse.get(),
                self.company_name_str.get(),
                self.sample_size_str.get(),
                self.vertical_threshold_str.get(),
                self.horizontal_threshold_str.get()
            )
        ).grid(
            row=2,
            column=1,
            pady=(0, 5)
        )

        # -------------------------------------------------------------
        # Actions Frame - The buttons that make stuff happen
        # -------------------------------------------------------------
        self.actions_frame = ttk.Frame(self.master)
        self.actions_frame.grid(row=1, column=0, pady=5)

        ttk.Button(
            self.actions_frame,
            text=process_queue_button_text(),
            command=self.run
        ).grid(
            row=0,
            column=0
        )
        ttk.Button(
            self.actions_frame,
            text="Clear Queue",
            command=self.clearQueue
        ).grid(
            row=0,
            column=1,
            padx=5
        )
        ttk.Button(
            self.actions_frame,
            text="Help",
            command=self.show_help
        ).grid(row=0, column=2)
        ttk.Button(
            self.actions_frame,
            text="About",
            command=self.show_about
        ).grid(row=0, column=3, padx=5)
        ttk.Button(
            self.actions_frame,
            text=quit_button_text(),
            command=self.master.quit
        ).grid(row=0, column=4)

        # -------------------------------------------------------------
        # Queue frame - Contains queue of tests to be run
        # -------------------------------------------------------------

        self.queueFrame = scrollingFrame(self.master)
        self.queueFrame.grid(row=3, columnspan=2, pady=5, padx=5, sticky="WE")
        self.innerQueueFrame = self.queueFrame.frame

    def addToQueue(self, indir, outdir, recurse, company, sample_size, ver_thresh, hor_thresh):

        # check if input exists
        try:
            if not os.path.exists(indir) and not (indir.split(".")[1] == 'laz' or 'las'):
                messagebox.showerror(
                    "File error",
                    "Input path does not exist, please select another path."
                )
                return
        except IndexError:
            messagebox.showerror(
                "File error",
                "Input path does not exist, please select another path."
            )
            return

        # if indir
        self.req_satisfied = False
        self.checkReq(company, sample_size, ver_thresh, hor_thresh)

        lical_results_dir = "lical_results"

        # make an outputPath if it doesn't exist
        try:
            if (outdir == '') and (indir.split(".")[1] == 'laz' or 'las'):
                outdir = indir.split(".")[0]
                outdir = outdir.split("'")[1]
                outdir = os.path.join(outdir, lical_results_dir)
                os.makedirs(outdir)
                print("Output path created: ", outdir)
        except IndexError:
            pass

        if outdir == '':
            outdir = os.path.join(indir, lical_results_dir)
            os.makedirs(outdir)
            print("Output path created: ", outdir)
        elif not os.path.exists(outdir):
            os.makedirs(outdir)
            if not os.path.exists(outdir):
                print("Selected output path could not be created")
                outdir = os.path.join(indir, lical_results_dir)
                os.makedirs(outdir)
                print("Output path created: ", outdir)
            else:
                print("Output path created: ", outdir)

        if self.req_satisfied:
            # point to end of queue
            sample_size = float(sample_size)
            ver_thresh = float(ver_thresh)
            hor_thresh = float(hor_thresh)
            queuePointer = len(self.queueDict)
            self.queueDict[queuePointer] = {}
            self.queueDict[queuePointer]['indir'] = indir
            self.queueDict[queuePointer]['outdir'] = outdir
            self.queueDict[queuePointer]['company'] = company
            self.queueDict[queuePointer]['recurse'] = recurse
            self.queueDict[queuePointer]['sample_size'] = sample_size
            self.queueDict[queuePointer]['hor_thresh'] = hor_thresh
            self.queueDict[queuePointer]['ver_thresh'] = ver_thresh
            self.queueDict[queuePointer]['inputType'] = self.inputType

            self.indir.set('')
            self.outdir.set('')
            self.company_name_str.set('')
            self.recurse.set(0)
            self.vertical_threshold_str.set(8)
            self.horizontal_threshold_str.set(35)

            self.updateQueue()
        else:
            return

    def checkReq(self, company, sample_size, ver_thresh, hor_thresh):

        try:
            sample_size = float(sample_size)
        except ValueError:
            messagebox.showerror("Value Error", "Sample size must be a positive number")
            return

        if not 0 < sample_size <= 100:
            messagebox.showerror("Value Error", "Sample size must be a positive number <= 100")
            return

        try:
            ver_thresh = float(ver_thresh)
            hor_thresh = float(hor_thresh)

        except ValueError:
            messagebox.showerror("Value Error", "Error thresholds must be numbers")
            return

        try:
            if (ver_thresh < 0) or (hor_thresh < 0):
                raise ValueError("Negative error thresholds are not permitted")

        except Exception:
            messagebox.showerror("Value Error", "Error thresholds must be positive numbers")
            return

        if len(company.split()) == 0:
            messagebox.showerror("Value Error", "Must specify a company name")
            return

        self.req_satisfied = True

    def updateQueue(self):
        # destory all queueItemFrames rebuild using queueDict
        # print("updateQueue: ", self.queueDict)

        for x in range(len(self.queueItemFrames)):
            self.queueItemFrames[x].destroy()
        self.queueItemFrames = []
        i = 0
        rowNum = 0

        for i in range(len(self.queueDict)):

            inputStr, outputStr = self.getInOutStr(
                self.queueDict[i]['indir'],
                self.queueDict[i]['outdir']
            )
            self.queueItemFrames.append(
                ttk.LabelFrame(
                    self.innerQueueFrame,
                    width=450,
                    height=100,
                    text=(i + 1)
                )
            )

            if i == 0:
                self.queueItemFrames[i].grid(row=0, column=0, padx=5, pady=(0, 5))
            elif i % 2 != 0:
                self.queueItemFrames[i].grid(row=rowNum, column=1, padx=(5, 20), pady=(0, 5))
                rowNum += 1
            else:
                self.queueItemFrames[i].grid(row=rowNum, column=0, padx=5, pady=(0, 5))

            ttk.Label(
                self.queueItemFrames[i],
                width=30,
                text=inputStr
            ).grid(
                row=0,
                column=0,
                sticky=W
            )
            ttk.Label(
                self.queueItemFrames[i],
                width=30,
                text=outputStr
            ).grid(
                row=1,
                column=0,
                sticky=W
            )

            ttk.Button(
                self.queueItemFrames[i],
                text="Edit",
                command=lambda i=i: self.editQueue(i)
            ).grid(
                row=0,
                column=2
            )
            ttk.Button(
                self.queueItemFrames[i],
                text="Delete",
                command=lambda i=i: self.deleteQueue(i)
            ).grid(
                row=1,
                column=2
            )

        self.innerQueueFrame.update_idletasks()
        self.queueFrame.onCanvasConfigure(None)

    def clearQueue(self):
        self.queueDict = {}
        self.updateQueue()

    def deleteQueue(self, queuePointer):
        # print("Queue before delete: ", self.queueDict)
        # print("queuePointer: ", queuePointer)
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

        self.updateQueue()

    def editQueue(self, queuePointer):
        # print("edit entry: ", queuePointer)
        popup = Toplevel()
        # self.set_icon(popup)
        popup.grab_set()

        # -------------------------------------------------------------
        # I/O Frame - This makes up the left side of the GUI
        # -------------------------------------------------------------
        topFrame = Frame(popup)
        topFrame.grid(row=0, column=0)
        io_frame = ttk.Frame(topFrame)
        io_frame.grid(row=0, column=0)

        # -------------------------------------------------------------
        # Input Frame - Select your infiles here!
        # -------------------------------------------------------------
        input_frame = ttk.LabelFrame(io_frame, text="Input Files", relief=RIDGE)
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky=E + W + N + S)

        ttk.Label(input_frame, text="Lidar Directory").grid(row=0, column=0)
        indir = StringVar()
        indir.set(self.queueDict[queuePointer]['indir'])
        dir1_entry = ttk.Entry(input_frame, textvariable=indir, width=40)
        dir1_entry.grid(row=0, column=1)
        self.inputType = ""
        dir1_button = ttk.Button(input_frame, text="Raw Swaths", command=self.choose_dir1)
        dir1_button.grid(row=0, column=2)
        dir2_button = ttk.Button(input_frame, text="Tiled Lidar", command=self.choose_dir2)
        dir2_button.grid(row=1, column=2)
        # ttk.Label(input_frame, text="Lidar Swath 2").grid(row=1, column=0)
        recurse = IntVar()
        recurse_entry = ttk.Checkbutton(
            input_frame,
            text="Search Subdirectories",
            variable=recurse,
            onvalue=1,
            offvalue=0
        )
        recurse_entry.grid(row=1, column=1)

        # -------------------------------------------------------------
        # Options Frame - So far, only option is test sample size %
        # -------------------------------------------------------------
        options_frame = ttk.LabelFrame(topFrame, text="Options", relief=RIDGE)
        options_frame.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(options_frame, text="Sample Size (%)").grid(row=0, column=0)
        sample_size_str = StringVar()
        sample_size_str.set(int(self.queueDict[queuePointer]['sample_size']))
        sample_size_entry = ttk.Entry(options_frame, textvariable=sample_size_str, width=4)
        sample_size_entry.grid(row=1, column=0, pady=(0, 5))

        ttk.Label(options_frame, text="RMS Error Thresholds (cm)").grid(row=2, column=0)

        thresholds_frame = Frame(options_frame)
        thresholds_frame.grid(row=3, column=0)

        ttk.Label(thresholds_frame, text="Vertical").grid(row=0, column=0, sticky=E)
        vertical_threshold_str = StringVar()
        vertical_threshold_str.set(int(self.queueDict[queuePointer]['ver_thresh']))
        vertical_threshold_entry = ttk.Entry(
            thresholds_frame,
            textvariable=vertical_threshold_str,
            width=4
        )
        vertical_threshold_entry.grid(row=0, column=1)

        ttk.Label(thresholds_frame, text="Horizontal").grid(row=1, column=0)
        horizontal_threshold_str = StringVar()
        horizontal_threshold_str.set(int(self.queueDict[queuePointer]['hor_thresh']))
        horizontal_threshold_entry = ttk.Entry(
            thresholds_frame,
            textvariable=horizontal_threshold_str,
            width=4
        )
        horizontal_threshold_entry.grid(row=1, column=1, pady=(0, 5))

        # -------------------------------------------------------------
        # Output Frame - So far, only for selecting output location
        # -------------------------------------------------------------
        output_frame = ttk.LabelFrame(io_frame, text="Output", relief=RIDGE)
        output_frame.grid(row=1, column=0)

        ttk.Label(output_frame, text="Report Location").grid(row=0, column=0)
        outdir = StringVar()
        outdir.set(self.queueDict[queuePointer]['outdir'])
        outdir_entry = ttk.Entry(output_frame, textvariable=outdir, width=34)
        outdir_entry.grid(row=0, column=1)
        outdir_button = ttk.Button(
            output_frame,
            text="Choose Directory",
            command=self.choose_outdir
        )
        outdir_button.grid(row=0, column=2)

        ttk.Label(output_frame, text="Company Name").grid(row=1, column=0)
        company_name_str = StringVar()
        company_name_entry = ttk.Entry(output_frame, textvariable=company_name_str, width=34)
        company_name_entry.grid(row=1, column=1, padx=5, pady=(0, 5))

        buttonClicked = IntVar()
        saveClicked = IntVar(value=0)
        doneClicked = IntVar()
        buttonFrame = Frame(popup)
        buttonFrame.grid(row=1, column=0)

        ttk.Button(
            buttonFrame,
            text="Save",
            command=lambda: [
                saveClicked.set(value=1),
                buttonClicked.set(1)
            ]
        ).grid(
            row=0,
            column=0
        )
        ttk.Button(
            buttonFrame,
            text="Discard Changes",
            command=lambda: [
                doneClicked.set(1),
                buttonClicked.set(1)
            ]
        ).grid(
            row=0,
            column=1,
            padx=5
        )
        ttk.Button(
            buttonFrame,
            text="Delete",
            command=lambda: [
                self.deleteQueue(queuePointer),
                doneClicked.set(1),
                buttonClicked.set(1)
            ]
        ).grid(
            row=0,
            column=2
        )

        popup.wait_variable(buttonClicked)

        if saveClicked.get() == 1:
            self.req_satisfied = False
            self.checkReq(
                indir,
                outdir,
                company_name_str,
                sample_size_str,
                horizontal_threshold_str,
                vertical_threshold_str
            )
            if self.req_satisfied:
                popup.destroy()
            else:
                popup.destroy()
                self.editQueue(queuePointer)

        popup.wait_variable(doneClicked)
        popup.destroy()

    def run(self):
        if len(self.queueDict) == 0:
            messagebox.showerror(
                'Input Error',
                'There are no tests in the queue!!!'
            )
            return
        """ # progress bar stuff:
        widgets = [
            progressbar.SimpleProgress(),
            ' ', progressbar.Percentage(),
            ' ', progressbar.Bar(),
            ' ', progressbar.Timer()
        ]
        with progressbar.ProgressBar(
            widgets=widgets,
            max_value=len(self.queueDict),
            redirect_stdout=True
        ) as p:
            p.start()"""
        if True:  # Use this line if not using progress bar (to maintain indent level)
            num_queue_items = len(self.queueDict)

            for x in range(num_queue_items):
                if self.queueDict[x]['inputType'] == 'tl':
                    inpath = Path(self.queueDict[x]['indir'])

                    if self.queueDict[x]['recurse'] == 1:
                        las_files = inpath.rglob('*.las')
                        laz_files = inpath.rglob('*.laz')
                        tiledFList = list(chain(las_files, laz_files))
                        self.queueDict[x]['recurse'] = 0
                    else:
                        las_files = inpath.glob('*.las')
                        laz_files = inpath.glob('*.laz')
                        tiledFList = list(chain(las_files, laz_files))

                    for i in range(len(tiledFList)):
                        lasdecompose.decompose(
                            tiledFList[i],
                            self.queueDict[x]['outdir']
                        )

                    self.queueDict[x]['indir'] = os.path.join(
                        self.queueDict[x]['outdir'],
                        "decomposed_lidar"
                    )

                try:
                    recurse = False
                    if self.queueDict[x]['recurse'] == 1:
                        recurse = True
                    lical.run_batch_lical(
                        self.queueDict[x]['indir'],
                        self.queueDict[x]['outdir'],
                        self.queueDict[x]['company'].strip(),
                        self.queueDict[x]['sample_size'],
                        self.queueDict[x]['ver_thresh'],
                        self.queueDict[x]['hor_thresh'],
                        recurse=recurse,
                        queue_item=x + 1
                    )
                except Exception as e:
                    # self.master.deiconify()
                    print("Runtime Error", str(e))
                    return

                # self.master.deiconify()
                print(
                    f"\nQueue item {x + 1} finished; LiCal ran succesfully."
                    f"\n\nResults saved here:"
                    f"\n\t{config.AnsiColors.yellow}{self.queueDict[x]['outdir']}"
                    f"{config.AnsiColors.reset}"
                )

                # Update progress bar
                # p.update(x + 1, force=True)

            self.clearQueue()

            print(
                f"{config.dashline}"
                "\nTo run more LiCal tests, add more items to the queue "
                f"in the GUI and click the "
                f"{process_queue_button_text()} button."
                f"\n\nTo quit LiCal, close this window (kill terminal), "
                f"or click the {quit_button_text()} button in the GUI."
            )

    def getInOutStr(self, inputPath, outputPath):
        try:
            if inputPath.split(".")[1] == 'laz' or 'las':
                inputPath = inputPath.split(".")[0]
                inputPath = inputPath[2::]  # Drop the drive letter and colon
        except IndexError:
            pass

        if (inputPath.count('/') > 1):
            startOfPath = inputPath[0:2]
            endOfPath = inputPath.split('/').pop()
            inputStr = f"Input: {startOfPath}/.../{endOfPath}"

        else:
            inputStr = "Input: " + inputPath

        if (outputPath.count('/') > 1):
            startOfPath = outputPath[0:2]
            endOfPath = outputPath.split('/').pop()
            outputStr = f"Output: {startOfPath}/.../{endOfPath}"

        else:
            outputStr = f"Output: {outputPath}"

        return inputStr, outputStr

    def choose_fp1(self):
        new_fp = filedialog.askopenfilename(
            initialdir='\\'.join(self.fp2.get().split('\\')[:-1]),
            title="Select Lidar File",
            filetypes=[("lidar files", '*.las *.laz')]
        )
        if new_fp != '':
            self.fp1.set(new_fp)

    def choose_fp2(self):
        new_fp = filedialog.askopenfilename(
            initialdir='\\'.join(self.fp1.get().split('\\')[:-1]),
            title="Select Lidar File",
            filetypes=[("lidar files", '*.las *.laz')]
        )
        if new_fp != '':
            self.fp2.set(new_fp)

    def choose_dir1(self):
        new_indir = filedialog.askdirectory(
            title="Select Raw Swath Directory"
        )
        if new_indir != '':
            self.indir.set(new_indir)
        self.inputType = 'rs'

    def choose_dir2(self):
        new_indir = filedialog.askdirectory(
            title="Select Tiled Lidar Directory"
        )
        if new_indir != '':
            self.indir.set(new_indir)
        self.inputType = 'tl'

    def choose_outdir(self):
        new_outdir = filedialog.askdirectory(
            initialdir='\\'.join(self.indir.get().split('\\')[:-1]),
            title="Select Output Directory"
        )
        if new_outdir != '':
            self.outdir.set(new_outdir)

    def set_icon(self):
        """
        Use a base64 image stored in config as the GUI window icon.
        """
        icon_data = base64.b64decode(config.BC_LOGO_B64)
        icon_path = os.getcwd() + r'\bc.ico'

        with open(icon_path, 'wb') as icon_file:
            icon_file.write(icon_data)

        self.master.iconbitmap(icon_path)
        os.remove(icon_path)

    def show_help(self):
        messagebox.showinfo(
            "LiCal Help",
            config.HELP_TEXT
        )

    def show_about(self):
        messagebox.showinfo(
            "About LiCal",
            config.ABOUT_TEXT
        )

    def show_disclaimer(self):
        messagebox.showinfo(
            "Disclaimer",
            config.DISCLAIMER_TEXT
        )


class scrollingFrame(Frame):
    def __init__(self, parentObject):
        ttk.LabelFrame.__init__(
            self,
            parentObject,
            text="Queue"
        )
        self.canvas = Canvas(self)
        self.frame = Frame(self.canvas)
        self.grid(sticky=E + W)

        self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview)
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


def process_queue_button_text():
    return "Process Queue"


def quit_button_text():
    return "Quit"

def main():
    gui = LiCalGUI()

    gui.set_icon()
    gui.show_disclaimer()

    gui.master.mainloop()


if __name__ == '__main__':
    main()
