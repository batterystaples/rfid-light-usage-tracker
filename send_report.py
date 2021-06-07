#!/usr/bin/python3

import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
import ssl
from datetime import datetime

src_email = ""
dest_email = ""
host = ""
port = 465
password = ""
database = "electricity.db"


month = int(datetime.today().strftime("%m"))
year = int(datetime.today().strftime("%Y"))

if month == 1:
	year -= 1
	month = 12
else:
	month -= 1

month = 6

c = sqlite3.connect(os.path.dirname(__file__) + "/" + database)
cur = c.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS usage (name VARCHAR(255), month INT, year INT, time INT)")
cur.execute("SELECT name, time FROM usage WHERE month = ? AND year = ?", (month, year))
data = cur.fetchall()
c.commit()
c.close()

body = ""
if len(data) == 0:
	body += "No activity was observed over the last month."
else:
	body += '''This report indicates the length of time for which users used the light over the last month.\n'''
	for row in data:
		body += str(row[0])
		body += '''\n'''
		body += str(row[1]) + " seconds"
		body += '''\n\n'''

report = MIMEText(body)
report['Subject'] = 'Monthly light usage report'
report['From'] = src_email
report['To'] = dest_email

context = ssl.create_default_context()
with smtplib.SMTP_SSL(host, port, context=context) as server:
	server.login(src_email, password)
	server.sendmail(src_email, dest_email, report.as_string())
