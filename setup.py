#!/usr/bin/python3

from distutils.core import setup

__version__ = "0.8"

setup(name="abuse-clinic",
      version=__version__,
      description="Test discovery and reporting tool",
      long_description=open("README"),
      author="Jordan Bettis",
      author_email="jordanb@hafdconsulting.com",
      scripts=["abuse-clinic/abuse-clinic"],
      url=["http://hafdconsulting.com/libre/abuse-clinic/"]
      download_url=\
          "http://hafdconsulting.com/libre/abuse-clinic/abuse-clinic-{0}.tar.gz"\
          .format(__version__)
      data_files=[('/usr/local/man/man1', 'doc/abuse-clinic.1.gz')])


