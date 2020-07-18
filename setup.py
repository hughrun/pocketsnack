from setuptools import setup, find_packages

setup(name='pocketsnack',
      version='3.0.0',
      url='https://hughrundle.net',
      license='GPL-3.0-or-later',
      packages=find_packages(),
      scripts=['bin/pocketsnack'],
      install_requires=['requests', 'pyyaml'],
      zip_safe=False,
      author='Hugh Rundle',
      author_email='hugh@hughrundle.net',
      description='KonMari your Pocket tsundoku from the command line',
      keywords='pocket, pocket api, cli',
      project_urls={
        'Source Code': 'https://github.com/hughrun/pocketsnack',
        'Documentation': 'https://github.com/hughrun/pocketsnack'
      }
)
