from selenium import webdriver
from datetime import datetime
import os
import csv
import smtplib

from sfe_credentials import credentials

csv_path = "sfe_correspondence.csv"
sfe_date_format = "%d/%m/%Y"

message_template = """\
From: %s
To: %s
Subject: New SFE Correspondence

SFE Bot noticed new correspondence today:

%s

This has been an automated message from SFE Bot :)
Have a nice day!
"""

def write_csv(filename, array2d):
    ofile = open(filename, "w")
    writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in array2d:
        writer.writerow(row)
    ofile.close()

def read_csv(filename):
    ifile = open(filename, "r")
    reader = csv.reader(ifile, delimiter=',', quotechar='"')
    return [row for row in reader if len(row) > 0]

def send_email(new_correspondence = [], to = []):
    with smtplib.SMTP_SSL(credentials.smtp_server) as server:
        print(server.login(credentials.smtp_email, credentials.smtp_password))
        correspondence_text = "\r\n".join([", ".join(r) for r in new_correspondence])
        message_body = message_template % (credentials.smtp_email, ", ".join(to), correspondence_text)
        server.sendmail(credentials.smtp_email, to, message_body)

# Set working directory to script directory:
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Navigating to SFE...")
browser = webdriver.PhantomJS(executable_path="./phantomjs/bin/phantomjs.exe")
browser.set_window_size(1000, 1000)
browser.get("https://logon.slc.co.uk/cas/login?_locale=en_GB")

print("Logging in...")
un = browser.find_element_by_id("cred1")
un.send_keys(credentials["un"])
pw = browser.find_element_by_id("cred2")
pw.send_keys(credentials["pw"])
pw.submit()

print("Answering secret answer challenge...")
for i in range(3):
    label = browser.find_element_by_id("securityAnswerLabel%d" % (i + 1))
    sbox = browser.find_element_by_id("securityChar%d" % (i + 1))
    secret_letter_no = int(label.text.split(" ")[1])
    sbox.send_keys(credentials["secret"][secret_letter_no - 1])
    if i == 2:
        sbox.submit()

print("Navigating to correspondence...")
browser.get("https://www.student-finance.service.gov.uk/customer/home/pages/correspondence/index")
browser.switch_to.frame(browser.find_element_by_id("miniAppIframe"))
# Chuck away the first and last rows of the table: these are the header and the navigation links
print("Scraping data...")
rows = browser.find_element_by_id("correspondenceTable").find_elements_by_tag_name("tr")[1:-1]
data = [[td.text for td in tr.find_elements_by_tag_name("td")] for tr in rows]

if os.path.isfile(csv_path):
    print(csv_path + " already exists. Loading and comparing...")
    old_data = read_csv(csv_path)
    write_csv(csv_path, data)
    last_known_date = datetime.strptime(old_data[0][0], sfe_date_format)
    new_correspondence = []
    for r in data:
        if datetime.strptime(r[0], sfe_date_format) > last_known_date:
            new_correspondence.append(r)
    print(new_correspondence)
    if len(new_correspondence) > 0:
        print("New correspondence discovered, sending email.")
        send_email(new_correspondence, ["wren6991@gmail.com", "cncwren@aol.com"])
    else:
        print("No new correspondence discovered.")
else:
    print(csv_path + " does not exist. Saving and exiting.")
    write_csv(csv_path, data)

browser.close()
