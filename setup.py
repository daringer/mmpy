import os
from setuptools import setup

install_requires = ["requests"]

base_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name = "mmpy",
    version = "0.0.1.dev",
    description = "Smart python util-collection",
    #long_description="\n\n".join([
    #    open(os.path.join(base_dir, "README.md"), "r").read(),
    #    open(os.path.join(base_dir, "CHANGELOG.md"), "r").read()
    #]),
    url = "https://github.com/daringer/mmpy",
    author = "Markus 'Daringer' Meissner",
    author_email = "coder@safemailbox.de",
    packages = ["mmpy"],
    zip_safe = False,
)
