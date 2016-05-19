**NCA Plus**

NCA Plus ( Network Centric Application Plus ) is an application designed for ACI to simplify the creation of L2 networks. Designed for 
customers that want a simple way to extend Layer2 VLANS into an ACI fabric, NCA Plus does everything from definition of Tenants, Bridge Domains
and End Point Groups (EPG's). 

The application runs on top of a Flask Application and uses Javascript (Sijax) and other constructs to create a simple HTML 
application that can be deployed in a production environment using Apache/NGINX with WSGI. 


Contacts:

* Rafael Muller ( rmuller@cisco.com )
* Santiago Flores ( sfloresk@cisco.com )
* Cesar Obediente ( cobedien@cisco.com )


**Installation**

As this is a Flask application you will need to either integrate the application in your production environment or you can 
get it operational in a virtual environment on your computer. In the distribution is a requirements.txt file that you can 
use to get the package requirements that are needed. The requirements file is located in the root directory of the distribution.

It might make sense for you to create a Python Virtual Environment before installing the requirements file. For information on utilizing
a virtual environment please read http://docs.python-guide.org/en/latest/dev/virtualenvs/. Once you have a virtual environment active then
install the packages in the requirements file.

`(virtualenv) % pip install -r requirements.txt
`

After you have installed the requirements you have to install the CobraSDK files related to your version of APIC. APIC provies you these
files directly via the URL:

http[s]://APIC_address/cobra/_downloads/

Download the two COBRA SDK files ( the models file and the sdk ). 

The instructions to install them would be:

`easy_install -Z {both files}
`

Once the SDK's are installed in the virtual environment, you can then change the application key in Flask

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
