import subprocess

_user = "vald3nir"
_password = "pypi-AgEIcHlwaS5vcmcCJDBjYmU4OGNjLWU0NmItNDJmNC1iYjc2LWQzMWMyOTc2ZDhkMwACKlszLCJiMWQ0NTViMy0xYjI5LTRhYjQtOGNlZi0wN2QxMTY1YmEzZjEiXQAABiBYoQ0zY_W_zJe2wrMeWbhjhK5WLNaveQQDpqKSscy9ig"


def publish_package():
    subprocess.run(["rm", "-rf", "dist"])
    subprocess.run(["python3", "-m", "build"])
    subprocess.run(["python3", "-m", "twine", "upload", "-u", _user, "-p", _password, "--repository", "pypi", "dist/*"])
