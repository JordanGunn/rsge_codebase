
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog as fd


root = Tk()
root.title("UTM Zones")
"""root.withdraw()"""
root.attributes('-topmost', True)
root.geometry('144x150')  # width x height
"""root.eval('tk::PlaceWindow . center')"""
root.iconbitmap(r"Z:\SPENCER_FLOYD\.ico\bc_logo.ico")
root.configure(bg="dodger blue")
"""root.resizable(True, False)"""


utm08 = StringVar()
utm09 = StringVar()
utm10 = StringVar()
utm11 = StringVar()
utm12 = StringVar()
done = StringVar()

utm_list = (
    utm08,
    utm09,
    utm10,
    utm11,
    utm12,
)


def utm_zones():
    for zone in utm_list:
        zone = zone.get()
        proj_zones = []
        proj_zones.append(zone)
    print(proj_zones)


utm_zones()

label = Label(
    root,
    bg="medium blue",
    fg="peach puff",
    text=" Select project UTM zones: ",).grid(row=0, sticky=N)


def get_utm():
    for zone in user_zones:
        zone = Checkbutton.get()
        zone.get()

        global all_zones
        all_zones = zone

        print(zone)


def info_box():
    messagebox.showinfo(
        "Info",
        "This program (WORK IN PROGRESS) creates the folders for the lidar QC server. "
        "If the project does not contain imagery, it will remove the paths associated with imagery metadata."
    )


# Checkbuttons are made for each utm zone 8 through 12
Checkbutton(root, bg="dodger blue", fg="black", text="UTM08", variable=utm08).grid(row=1, sticky=W)
Checkbutton(root, bg="dodger blue", fg="black", text="UTM09", variable=utm09).grid(row=1, sticky=E)
Checkbutton(root, bg="dodger blue", fg="black", text="UTM10", variable=utm10).grid(row=3, sticky=W)
Checkbutton(root, bg="dodger blue", fg="black", text="UTM11", variable=utm11).grid(row=3, sticky=E)
Checkbutton(root, bg="dodger blue", fg="black", text="UTM12", variable=utm12).grid(row=5, sticky=S)

# done and information buttons:
button = Button(root, bg="light goldenrod", fg="black", text="DONE", command=get_utm).grid(row=6, sticky=S)

info_button = Button(
    root,
    bg="light goldenrod",
    fg="black",
    text="INFO",
    command=info_box).grid(row=7, sticky=S)

# create_utm_folders = input(f'{colour.magenta}Input all project UTM zones,
# separated by a single space: {colour.green}')
user_zones = [
    "utm08",
    "utm09",
    "utm10",
    "utm11",
    "utm12"
]

# user_zones = []
utm = "UTM"
utm_single_dig = "UTM0"

mainloop()
