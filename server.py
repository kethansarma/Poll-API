"""
Main module of the server file
"""

# 3rd party moudles
from flask import render_template

# Local modules
import config


# Get the application instance
connex_app = config.connex_app

# Read the swagger.yml file to configure the endpoints
connex_app.add_api("swagger.yml")


# Create a URL route in our application for "/people"
@connex_app.route("/")
def home():
    """
    This function just responds to the browser URL
    localhost:5000/

    :return:        the rendered template "home.html"
    """
    return render_template("home.html")


@connex_app.route("/poll")
@connex_app.route("/poll/create")
@connex_app.route("/poll/<int:pollid>")
@connex_app.route("/poll/getrequest/<int:pollid>")
@connex_app.route("/poll/getresponse/<int:responseid>")
@connex_app.route("/poll/submit")

def poll(data=""):
    """
    This function just responds to the browser URL
    localhost:5000/people

    :return:        the rendered template "people.html"
    """

    return data

if __name__ == "__main__":
    connex_app.run(debug=True,host="127.0.0.1",port=5555)
