import subprocess

_user = "vald3nir"
_password = "pypi-AgEIcHlwaS5vcmcCJGQ1ZWFiNDJmLTg1N2QtNDAwNC1iYWUxLTNiYWEyYzk0NDFkNwACKlszLCJiMWQ0NTViMy0xYjI5LTRhYjQtOGNlZi0wN2QxMTY1YmEzZjEiXQAABiDHPAa6kCpCCvhijpUbz-tjzJwQ_su5Z4QrEikZci9-9g"


def publish_package():
    subprocess.run(["rm", "-rf", "dist"])
    subprocess.run(["python3", "-m", "build"])
    subprocess.run(["python3", "-m", "twine", "upload", "-u", _user, "-p", _password, "--repository", "pypi", "dist/*"])
