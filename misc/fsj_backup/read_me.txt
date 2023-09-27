This python scipt was created to copy data from the memory card of the fort st. john
GNSS receiver to the local machine used for storing and monitoring GNSS data at GeoBC. In the future,
if anything should change about the location of the data (e.g. the ftp host for the sd card of the receiver),
The constant values should be adjusted to reflect these changes. Additonally, the script will also convert
the copied data from the leica proprietary format (.00) to Rinex format. The program should run without any
input from the user, from any directory on your local computer (just double click to run). Finally, the code
has been set to run on the windows task scheduler at <<insert time here>> everyday, so unless it is necessary
to manually run the file, no human intervention should be needed.

Created by: Jordan Godau
Date: 2020-01-24