from flask import Blueprint, render_template

mod_test = Blueprint('test', __name__)

@mod_test.route("/")
def index():
    return render_template("test.html")