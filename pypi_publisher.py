import subprocess

if __name__ == '__main__':
    subprocess.run(["rm", "-rf", "dist"])
    subprocess.run(["python3", "-m", "build"])
    subprocess.run(["python3", "-m", "twine", "upload", "--repository", "pypi", "dist/*"])
