from app import app
# If you need to make the application visible outside, change the
# ip address to your own ip. You can also change the port that
# the application will be listening.
app.run(host='127.0.0.1', debug=True, port=5005)
