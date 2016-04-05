For this solution to work you first need to do the following step

1) Inside this project
Go to fedex-hub -> app -> __init__

Assign this variable:

app.secret_key = ''

This is a flask parameter, just choose a random string of no less than 40 characters.
E.g:
'A0Zr4FhJASD1LFmw0918jHH!jm84$#ssaWQsif!1'

Remember to install ACI cobra egg files. Those must be the same version that the APIC software