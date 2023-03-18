""" 
download IGS precise ephemeries from NASA CDDIS

typical functionality:
>> python main.py "albert.a.webb@proton.me" "gnss"

file name formatting here
https://files.igs.org/pub/resource/guidelines/Guideline%20for%20the%20transition%20of%20the%20IGS%20products%20to%20IGS20%20and%20long%20filenames%20-%20v1.0.pdf
or
http://acc.igs.org/repro3/Long_Product_Filenames_v1.0.pdf

we want 
AAA -IGS - analysis center
V - any -  version number
PPP - OPS - Operational IGS product
TTT - FIN - Final product

which will look like IGS0OPSFIN_YYYYDDDHHMM_01D_15M_ORB.SP3.gz
IGS0OPSFIN - product type
YYYYDDDHHMM - Date and time of session
01D_15M - Duration and sample frequency
ORB.SP3 - product type
.gz - zipped

this will search for "IGS0OPSFIN*ORB.SP3.gz"


DEPENDANCIES
    ndg-httpsclient
    pyopenssl
    pyasn1
"""

from ftplib import FTP_TLS
from fnmatch import fnmatch
from time import sleep


def login(ftp_password):
    """logs in using anonymous login credentials, and supplying email."""
    ftps = FTP_TLS(host='gdc.cddis.eosdis.nasa.gov')
    ftps.login(user='anonymous', passwd=ftp_password)
    ftps.prot_p()  # setup secure connection
    return ftps


def download_file(ftps_server, file_name):
    """
    Download binary file. writes to 'file_name' in working directory 
    RETR is added as a prefix to the file that is to be downloaded
    """
    ftps_server.retrbinary(cmd="RETR "+file_name,
                           callback=open(file_name, 'wb').write)


def find_files(ftps_server, search_term):
    """searches the current directory for files 
    matching the search terms with the ability to use wildcards"""
    files_found = []
    all_files = ftps_server.nlst()
    for file in all_files:
        # matches search term (has IGS0OPSSNX prefix and .orb.sp3 suffix)
        if fnmatch(file, search_term):
            files_found.append(file)
    return files_found


def download_week(ftps_server):
    """ preps download of each file from the GNSS week number 
    folder and calls the download file function"""
    files_to_download = find_files(
        ftps_server=ftps_server, search_term="IGS0OPSFIN*ORB.SP3.gz")

    for file in files_to_download:
        download_file(ftps_server=ftps_server, file_name=file)


def spacer():
    """ a line of dashes and new lines to space out blocks of text"""
    print("-----------------------------------------------------------------------\n\n\n\n\n")


def main():
    """main function to download all IGS precise ephemerids"""

    print("""\n\nPrecise ephemrids downloader by Albert Webb
\nThis downloader only downloads final solutions from International GNSS Service (IGS)\n\n""")

    email = input("Please enter your email address: ")
    spacer()
    ftps = login(email)

    print(ftps.getwelcome())  # show welcome message from server
    sleep(5)
    spacer()

    # change working directory to the products folder
    print(ftps.cwd(r"gnss/products"))
    spacer()

    # change working dir to week that is to be downloaded
    gnss_weeks = input(
        """enter the week you wish to download ephemerids for\n
(if multiple, seperate them by spaces)\n--> :""").split()

    for gnss_week in gnss_weeks:
        try:
            ftps.cwd(gnss_week)
            print(f"downloading week {gnss_week}")

            download_week(ftps_server=ftps)

            ftps.cwd("..")  # go to parent directory

        except Exception as ex:  # pylint: disable = W0718
            print(type(ex))
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            print(f"the week '{gnss_week}' was not found")

    print("Download complete\nDisconnecting from 'CDDIS Anonymous FTP Archive'")
    ftps.quit()


if __name__ == "__main__":
    main()
