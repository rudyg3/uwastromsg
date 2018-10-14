# -*- coding: utf-8 -*-
"""
Email script for pizza lunch and w(h)ine time warnings
======================================================

In the same directory as this script, you should create
an `assignments.txt` file. Each line will have a username
of a grad to receive an assignment (i.e. the part of their
@uw.edu email address before the @) and the date of the 
assignment (usually a Friday) separated by whitespace, like so: 

    bmmorris 9 26 2014
    eakruse 10 3 2014
    nmhw 10 10 2014 

This script will set up `at` jobs to email each grad in the 
assignments file twice before the assignment date (the user
can tweak the number of days before the assignment these two
emails will be sent). The contents of the emails should be stored
in two text files in the directory `messagecontents`. Note - we're
using HTML encoding to send out those files, so to render line breaks,
use <br> tags, etc.

To add new assignments, first update the `assignments.txt` file with
new assignments. Then run:

    $ python uwastromsg.py

which creates/updates the `scheduler.sh` file. Then, source the
`scheduler.sh` file to create the `at` jobs by running:

    $ source scheduler.sh

You can now check which `at` jobs are scheduled in the queue
by running:

    $ atq

For more help with `at` jobs, try:

    $ man at

The login information for the uwastrograd account should be 
saved in text files in this directory -- if you don't have 
that info, contact Brett at bmmorris@uw.edu, otherwise no
emails will be sent.

Created on Sep 27, 2014 by Brett Morris. Built upon the enduring
work of "THE LEGENDARY YUSRA ALSAYYAD" who wrote the original version on 
"JULY 6, 2013, WHILE LONELY AT MRO."

Jave Note:

If you run into issues, try the following in an ipython console:

from uwastromsg import send_email

send_email(from_address, to_address, cc_address, from_address, subject, message)

to see if emails can be properly sent!

"""

import datetime  # For handling dates
import smtplib   # For sending emails with Simple Mail Transfer Protocol
from email.mime.text import MIMEText # Email management object
from glob import glob # Search for file paths
import os        # Interface with file system
import sys       # For retrieving command line arguments

# Change this if you're trying the script out!
debug = True

# Paths to input files and settings
assignmentspath = 'assignments.txt'       # File with assignment usernames and dates
messagepaths = 'messagecontents/message*' # There should be two message file here

# Debug: send in now + minute

if debug:
	warningtime = datetime.datetime.now() + datetime.timedelta(seconds=120)
	warningtime = warningtime.strftime("%I:%M%p")
else:
	warningtime = '12:00pm'                    # Time to send email warnings, in local time for the running machine.

Ndays_firstwarning = 2                    # Number of days before assignment to send first email
Ndays_secondwarning = 1                   # Number of days before assignment to send second email
admin_emailaddress = 'tagordon@uw.edu'    # Person launching the script
astrogrademail = 'uwastrograds@gmail.com' # Astro grad email address
message_subject = "The W(h)ine Time Committee has selected you!" # Subject line of emails
#pythonpath = '/astro/apps6/anaconda2.0/bin/python'        # Which Python to use
pythonpath = "/astro/apps6/opt/anaconda2.4/bin/python"
thisfilepath = os.path.abspath(__file__)                  # Path to this file
logfilepath = os.path.abspath(os.path.join(os.path.dirname(__file__),'log.txt'))
logfile = open(logfilepath, 'a')
schedulerpath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             'scheduler.sh'))

def prepare_scheduler():
    '''
    Make a `scheduler.sh` script that can be sourced to prepare the `at` jobs. 
    Run the script with: 
        $ source scheduler.sh
    '''
    assignmentslist = open(assignmentspath, 'r').readlines()
    # Get absolute paths to the message content files
    firstmessagepath, secondmessagepath = [os.path.abspath(f)
                                           for f in sorted(glob(messagepaths))]

    scheduler = open(schedulerpath, 'w') # Open the scheduler file (output)
    
    for assignment in assignmentslist:
        # From the assignments list: get the user, and date of assignment, calculate
        # when to send the warning, and which warning to send
        emailusername = assignment.split()[0]
        month, day, year = map(int,assignment.split()[1:4])
        #words = [w.replace("\'", "") for w in assignment.split()[4:]]
        words = [w.replace("\"", "") for w in assignment.split()[4:]]
        words = "\\\"" + "\\\" \\\"".join(words) + "\\\""
        assignmentdate = datetime.datetime(year, month, day)
        firstwarningdate = assignmentdate - datetime.timedelta(days=Ndays_firstwarning)
        secondwarningdate = assignmentdate - datetime.timedelta(days=Ndays_secondwarning)
        
        scheduleline_firstwarning = ('echo \"{} {} {} {}@uw.edu {}\" | at {} {} \n'.format(pythonpath, 
                                                                                        thisfilepath, 
                                                                                        firstmessagepath, 
                                                                                        emailusername,
                                                                                        words, 
                                                                                        warningtime, 
                                                                                        firstwarningdate.strftime('%m%d%y')))
                                     
        scheduleline_secondwarning = ('echo \"{} {} {} {}@uw.edu {}\" | at {} {} \n'.format(pythonpath, 
                                                                                         thisfilepath, 
                                                                                         secondmessagepath, 
                                                                                         emailusername,
                                                                                         words, 
                                                                                         warningtime, 
                                                                                         secondwarningdate.strftime('%m%d%y')))
        scheduler.write(scheduleline_firstwarning)
        scheduler.write(scheduleline_secondwarning)
    
    scheduler.close()

def send_email(from_address, to_address, cc_address, reply_to_address, subject, message):
    '''
    Send an email!
    '''
    msg = MIMEText(message.encode('utf-8'), 'html', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = to_address
    msg['cc'] = cc_address
    msg.add_header('reply-to', reply_to_address)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    # Read u and p
    username = open(os.path.join(os.path.dirname(__file__), 'u'), 'r').read().strip()
    p = open(os.path.join(os.path.dirname(__file__), 'p'),'r').read().strip()
    s.login(username, p)
    s.sendmail(from_address, [to_address] + [cc_address], msg.as_string())
    s.quit()    

if __name__ == "__main__":

    # When this script is run via command line:
    nargs = len(sys.argv)

    # If the script is run with no command line arguments:
    if nargs == 1:
        print('Preparing the scheduler.')
        prepare_scheduler()
        logmessage = ' '.join([str(datetime.datetime.now()), 'preparing scheduler'])+'\n'
        print('Updating log file: {}'.format(logfilepath))
        print('\nOnce complete, run:\n    source scheduler.sh')

    # Otherwise, assume the script is being run by an `at` job
    else:
        thisfilename, messagecontentpath, emailaddress = sys.argv[:3]
        if nargs > 3:
            wordslist = sys.argv[3:]
            basemessage = open(messagecontentpath, 'r').read()
            try:
                messagecontent = basemessage.format(*wordslist)
            except: 
                logmessage = "number of blanks in base message does not match number of words"
                logfile.write(logmessage)
        else:
            messagecontent = open(messagecontentpath, 'r').read()
        logmessage = ' '.join([str(datetime.datetime.now()),emailaddress, messagecontentpath])+'\n'
        send_email(from_address=astrogrademail, 
                  to_address=emailaddress, 
                  cc_address=admin_emailaddress, 
                  reply_to_address=admin_emailaddress, 
                  subject=message_subject, 
                  message=messagecontent)
        logfile.write(logmessage)
        logfile.close()
