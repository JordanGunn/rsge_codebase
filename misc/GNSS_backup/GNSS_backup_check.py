import os
import smtplib
import datetime

# constant values
RINEX_DIR = r"N:\RINEX"
TYSON_EMAIL = r"Tyson.Altenhoff@gov.bc.ca"
JORDAN_EMAIL = r"Jordan.Godau@gov.bc.ca"
YASER_EMAIL = r"Yaser.Sadeghi@gov.bc.ca"
# JORDAN_GMAIL = R"JordanGunn92@gmail.com"
# CRED_PATH = R"Z:\JORDAN\___python_projects_qc__\working\credentials.json"
# RINEX_DIR = r"D:\test\gnss_test_check\RINEX"

# create dictionary for expected values related to station codes
EXPECTED_COUNT = {
    "BCCG": 24,
    "BCDI": 24,
    "BCES": 24,
    "BCFN": 24,
    "BCIN": 24,
    "BCLC": 48,
    "BCLI": 48,
    "BCMR": 48,
    "BCNS": 24,
    "BCPG": 24,
    "BCPR": 24,
    "BCSF": 48,
    "BCSL": 24,
    "BCSM": 24,
    "BCSS": 24,
    "BCTE": 24,
    "BCVC": 48,
    "BCWA": 24,
}


def read_error_report(file):
    with open(file, "r") as f:
        file_content = f.read()
    return file_content


# retrieve dates
dd = datetime.date.today() - datetime.timedelta(1)

# get the previous day
y = dd.year  # get the year from yesterday
d = dd.day  # get the day from yesterday
d_not = datetime.date(y, 1, 1)  # beginning of the year
diff_days = (
    dd.toordinal() - d_not.toordinal()
)  # get amount of days that have passed since beginning of the year
pd = str(diff_days + 1)  # add one

# format day number to fit folder naming
while len(pd) != 3:
    pd = "0" + pd

# List of frequencies
file_frequency = ["1_Dual", "15_Dual"]
# Used to determine when to use final separating line type
frequencies_number = len(file_frequency)
# Run process for each frequency in frequency list
for frequency in file_frequency:
    # Set expected count depending on frequency
    if frequency == "1_Dual":
        dual_error_text = "1 Dual"

    if frequency == "15_Dual":
        dual_error_text = "15 Dual"

    # create directory name as string
    check_dir = RINEX_DIR + "\\" + str(y) + "\\" + f"{pd}" + "\\" + f"{frequency}"

    list_dir = os.listdir(check_dir)
    # Exclude certain folders depending on directory
    if frequency == "1_Dual":
        list_dir = [d for d in list_dir if d != "BCFJ"]
        list_dir = [d for d in list_dir if d != "BCAI"]
    if frequency == "15_Dual":
        list_dir = [d for d in list_dir if d != "BCFJ"]
        list_dir = [d for d in list_dir if d != "BCAI"]
        EXPECTED_COUNT["BCDL"] = 24

    list_dir.sort()
    a_dir = list(EXPECTED_COUNT.keys())

    # start counter for problems found
    problems = 0
    total_missing = 0
    stn_issues = []
    missing_dir = []

    # check for missing directories at output location
    if len(list_dir) != len(list(EXPECTED_COUNT.keys())):
        a_dir = [
            x for x in list(EXPECTED_COUNT.keys()) if x in list_dir
        ]  # compare dictionary and directories at output
        missing_dir = set(list(EXPECTED_COUNT.keys())) - set(
            a_dir
        )  # get the missing the directories

        for k in list(missing_dir):
            del EXPECTED_COUNT[
                k
            ]  # delete keys and values associated with missing directories
            problems += 1  # record instance of missing directory

    # open file and start writing issues encountered during backup check
    error_log_str = os.path.join(
        r"C:\GNSS Spider", "file_check_log.txt"
    )  # filename as string
    with open(
        error_log_str, "a+"
    ) as f:  # open file in append mode, create if it doesn't exist
        f.write(
            f"<<GNSS backup check --- {dual_error_text} --- Date: {datetime.date.today()}>>\n"
        )  # write the header
        f.write(f"Checking back up for Julian Day {pd}\n\n")  # write the header
        f.write("--- Expected file counts ---\n")  # show expected file counts
        for k, v in zip(EXPECTED_COUNT.keys(), EXPECTED_COUNT.values()):
            f.write(f"{k}:\t{v}\n")  # write expected file counts
        f.write("\n")  # newline
        f.write(
            "--- Files Missing Summary ---\n"
        )  # start showing errors encountered for each folder check
        for dir, num_expected, stn in zip(
            list_dir, list(EXPECTED_COUNT.values()), list(EXPECTED_COUNT.keys())
        ):
            num_files = len(os.listdir(os.path.join(check_dir, dir)))
            # if number of files not the same as expected, record problems
            if num_files != num_expected:
                problems += 1
                total_missing += num_expected - num_files
                stn_issues.append(stn)
                f.write(f"GNSS station {stn} missing {num_expected-num_files} files\n")
        f.write("\n")
        # if any problems are encountered, record summary of issues
        if problems != 0:
            f.write("--- Problems Encountered Summary ---\n")
            f.write(f"Number of stations with missing files: {problems}\n")
            f.write(f"Total number of missing files: {total_missing}\n")
            f.write(f"Stations with missing files: {stn_issues}\n")
            if len(missing_dir) != 0:
                f.write(
                    f"Number of directories missing from back up location: {len(missing_dir)}\n"
                )
                f.write(f"Directories missing from back up location: {missing_dir}\n")
        # if no problems encounters, record
        if problems == 0:
            f.write("No problems encountered\n")
        # write log seperator
        # coutn down frequencies number
        frequencies_number = frequencies_number - 1
        # frequency seperator if there are still more logs to be written
        if frequencies_number > 0:
            f.write(
                "\n--------------------------------------------------------------------------------------------------------------------------------------------------------\n"
            )
        # log seperator, written after last frequency report
        elif frequencies_number == 0:
            f.write(
                "\n****************************************************************************************************************\n"
            )
        list_dir = None

    if problems != 0:
        # read the error report and send email if there is anything wrong
        p = read_error_report(error_log_str)  # read report
        i = p.find(
            f"<<GNSS backup check --- 1 Dual --- Date: {datetime.date.today()}>>"
        )
        msg = p[i:-1]  # get the message to be sent
        print(msg)
        server = smtplib.SMTP("apps.smtp.gov.bc.ca")
        server.sendmail("GNSS.check@gov.bc.ca", TYSON_EMAIL, f"\n{msg}")
        # server.sendmail("GNSS.check@gov.bc.ca", JORDAN_EMAIL, f"\n{msg}")
        server.sendmail("GNSS.check@gov.bc.ca", YASER_EMAIL, f"\n{msg}")
        server.close()

        # ezgmail.send(JORDAN_EMAIL, f'GNSS Backup Check - {datetime.date.today()}', msg, cc=JORDAN_GMAIL)

