For this solution to work you first need to do the following things in the APIC controller

1) Inside the APIC dashboard
Go to Fabric -> Access Policies -> Interface Policies -> Link Level -> Actions -> Create a Link Level Policy
Values

Name: 1GB
Speed: 1 Gbps

Leave all other values to their default and then create

2) Inside the APIC dashboard
Go to Fabric -> Access Policies -> Interface Policies -> Port Channel Policies -> Actions -> Create port channel policy
Values

Name: LACP
Mode: LACP Active

Leave all other values to their default and then create

3) Inside this project
Go to fedex-hub -> app -> __init__

Change this values:

app.secret_key = ''
app.apic_url = ''
app.apic_user = ''
app.apic_password = ''

Values

app.secret_key -> This is a value that the web app uses to comunicate, just choose a random string of no less than 40
characters
app.apic_url -> IP or name of the APIC controller. Don't forget to put http or https!
app.apic_user -> APIC user name with permission to create and delete any kind of object (except users)
app.apic_password -> APIC password for the previous selected user