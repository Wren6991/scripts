from selenium import webdriver
from datetime import datetime
import os
import smtplib

from sfe_credentials import credentials

csv_path = "sfe_correspondence.txt"
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

def write_correspondence(filename, data):
    ofile = open(filename, "w")
    ofile.write("\n".join(data))
    ofile.close()

def read_correspondence(filename):
    ifile = open(filename, "r")
    rows = ifile.read().split("\n")
    ifile.close()
    return rows

def send_email(new_correspondence = [], to = []):
    with smtplib.SMTP_SSL(credentials["smtp_server"]) as server:
        print(server.login(credentials["smtp_email"], credentials["smtp_password"]))
        correspondence_text = "\r\n".join(new_correspondence)
        message_body = message_template % (credentials["smtp_email"], ", ".join(to), correspondence_text)
        server.sendmail(credentials["smtp_email"], to, message_body)

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
print("Scraping data...")
rows = browser.find_element_by_class_name("document-list").find_elements_by_tag_name("li")
data = [r.text.replace("\n", "; ").replace("\r", "") for r in rows]

if os.path.isfile(csv_path):
    print(csv_path + " already exists. Loading and comparing...")
    old_data = read_correspondence(csv_path)
    write_correspondence(csv_path, data)
    new_correspondence = [r for r in data if not r in old_data]
    print(new_correspondence)
    if len(new_correspondence) > 0:
        print("New correspondence discovered, sending email.")
        send_email(new_correspondence, ["wren6991@gmail.com", "cncwren@aol.com"])
    else:
        print("No new correspondence discovered.")
else:
    print(csv_path + " does not exist. Saving and exiting.")
    write_correspondence(csv_path, data)

browser.close()
