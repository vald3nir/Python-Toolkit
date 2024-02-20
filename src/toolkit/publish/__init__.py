import subprocess


def publish_package(install_libs: bool = False):
    if install_libs:
        subprocess.run(["pip3", "install", "build", "twine"])
    subprocess.run(["rm", "-rf", "dist"])
    subprocess.run(["python3", "-m", "build"])
    subprocess.run(["python3", "-m", "twine", "upload", "--repository", "pypi", "dist/*"])
