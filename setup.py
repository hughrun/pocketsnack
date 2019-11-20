from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
  name="pocketsnack",
  version="2.0.1",
  author="Hugh Rundle",
  author_email="hugh@hughrundle.net",
  description="When your Pocket list is overwhelming, pocket-snack lets you see just what you can read today. A script for managing your getpocket.com list.",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/hughrun/pocket-snack",
  packages=find_packages(),
  install_requires=["requests"],
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GPL-3.0-or-later",
    "Operating System :: OS Independent"
  ],
  entry_points={
        'console_scripts': [
          'pocketsnack = pocketsnack:main_func'
        ]
  }
)