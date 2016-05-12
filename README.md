Contacts:

Rafael Muller ( rmuller@cisco.com )
Santiago Flores ( sfloresk@cisco.com )
Cesar Obediente ( cobedien@cisco.com )


For this solution to work you first need to do the following steps

1) Inside this project
Go to app -> __init__

Assign this variable:

app.secret_key = ''

This is a flask parameter, just choose a random string of no less than 40 characters.
E.g:
'A0Zr4FhJASD1LFmw0918jHH!jm84$#ssaWQsif!1'

2) Install the requirements listed in requirements.txt
Remember to install ACI cobra egg files. Those must be the same version that the APIC software

To run the the application just execute the run.py file.
E.g. for a linux machine will be sudo python run.py

If you need to make the application visible outside your computer, change the run.py file with your own
 IP. You can also change the port that the application will be listening.