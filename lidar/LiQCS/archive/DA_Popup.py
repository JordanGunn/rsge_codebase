# Sam May's draft code for Density Analysis pop-up used in LiQCS
# Received from Sam May Oct. 19, 2022

from tkinter import *
from tkinter import ttk, filedialog, messagebox


class GUI:
    def __init__(self):
        self.root = Tk()
        mainFrame = Frame(self.root)
        mainFrame.grid()
        ttk.Button(
            mainFrame,
            text="Choose directory",
            command=lambda: self.DA_popup()
        ).grid(row=0, column=1)

    def DA_popup(self):
        popup = Toplevel()
        popup.grab_set()
        ttk.Label(
            popup,
            text="Density Analysis Parameters"
        ).grid(row=0, column=0, pady=5)

        dirFrame = Frame(popup)
        dirFrame.grid(row=1, column=0, padx=10)
        
        # Input Raster directory---------------------
        ttk.Label(
            dirFrame,
            text="Input density raster directory"
        ).grid(row=0, column=0)
        
        rasterEntry = StringVar()
        ttk.Entry(
            dirFrame,
            width=40,
            textvariable=rasterEntry
        ).grid(row=1, column=0)

        ttk.Button(
            dirFrame,
            text="Choose directory",
            command=lambda: self.path_select(rasterEntry)
        ).grid(row=1, column=1)
        # -------------------------------------------

        # Project area directory --------------------
        ttk.Label(
            dirFrame,
            text="Project area directory"
        ).grid(row=2, column=0)

        projectAreaEntry = StringVar()
        ttk.Entry(
            dirFrame,
            width=40,
            textvariable=projectAreaEntry
        ).grid(row=3, column=0)

        ttk.Button(
            dirFrame,
            text="Choose directory",
            command=lambda: self.path_select(rasterEntry)
        ).grid(row=3, column=1)
        # -------------------------------------------

        # Minimun desity requirement ----------------
        densityFrame = Frame(popup)
        densityFrame.grid(row=2, column=0, pady=10)

        ttk.Label(
            densityFrame,
            text="Minimun density requirement:  "
            ).grid(row=0, column=0)
        
        minDensityReqEntry = StringVar()    
        ttk.Entry(
            densityFrame,
            width=5,
            textvariable=minDensityReqEntry
        ).grid(row=0, column=1)
        
        ttk.Label(
            densityFrame,
            text="  points per square meter"
        ).grid(row=0, column=2)
        # -------------------------------------------

        # BCGW username and password ----------------
        BCGWFrame = Frame(popup)
        BCGWFrame.grid(row=3, column=0)

        ttk.Label(
            BCGWFrame,
            text="BCGW Username:      "
        ).grid(row=0, column=0, pady=(0,5))

        bcgwUserEntry=StringVar()
        ttk.Entry(
            BCGWFrame,
            textvariable=bcgwUserEntry
        ).grid(row=0, column=1, pady=(0,5))

        ttk.Label(
            BCGWFrame,
            text="BCGW Password:      "
        ).grid(row=1, column=0)

        bcgwPassEntry = StringVar()
        ttk.Entry(
            BCGWFrame,
            textvariable=bcgwPassEntry
        ).grid(row=1, column=1)
        # -------------------------------------------

        normalizeFrame = Frame(popup)
        normalizeFrame.grid(row=4, column=0, pady=10)

        ttk.Label(
            normalizeFrame,
            text="Divide raster values with incorrect units by: "
        ).grid(row=1, column=0)

        divisorEntry = StringVar(value="25")
        print(f'{divisorEntry.get()}')
        self.divisorEntryPointer=ttk.Entry(
            normalizeFrame,
            width=4,
            textvariable=divisorEntry,
            state='enabled'
        )
        self.divisorEntryPointer.grid(row=1, column=1)
        
        correctChkb = IntVar()
        correctChkb.set(0)
        ttk.Checkbutton(
            normalizeFrame,
            text="Check for correct units, and attempt to correct?",
            variable=correctChkb,
            command=lambda : self.chkb_check(correctChkb)
        ).grid(row=0, column=0)

        isSubmitClicked = IntVar()
        Submit = ttk.Button(
            popup,
            text="Submit",
            command=lambda: isSubmitClicked.set(1)
        )
        Submit.grid(row=5, column=0, pady=(0, 5))


    def chkb_check(self, var):
        
        if var.get() == 0:
            self.divisorEntryPointer.config(state='disable')
        else:
            self.divisorEntryPointer.config(state='enable')

    def path_select(self, pathSV):
            """
            Opens 'select folder' windows dialog, returns selected folder path
            """
            dirPath = filedialog.askdirectory(initialdir="/")
            pathSV.set(dirPath)

def main():
    gui = GUI()
    gui.root.mainloop()

if __name__ == '__main__':
    main()