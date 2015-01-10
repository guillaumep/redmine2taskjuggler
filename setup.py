import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md")).read()


setup(name='redmine2taskjuggler',
      version='1.0',
      description='Project management with TaskJuggler with Redmine data',
      long_description=README,
      url='https://github.com/guillaumep/redmine2taskjuggler',
      keywords='redmine,taskjuggler',
      packages=['redmine2taskjuggler', 'redmine2taskjuggler.users', 'redmine2taskjuggler.issues'],
      include_package_data=True,
      entry_points="""\
      [console_scripts]
      redmineusers2sqlite = redmine2taskjuggler.users.redmineusers2sqlite:main
      sqliteusers2taskjuggler = redmine2taskjuggler.users.sqliteusers2taskjuggler:main
      """,
      )
