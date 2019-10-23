from lmsquery import const

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="LMSQuery-fork",
    version=const.LMSQUERY_VERSION,
    author="Robert Einhausi, Aaron Ciuffo",
    author_email="aaron.ciuffo@gmail.com",
    description=("Query library for Logitech Media Server"),
    license="MIT",
    keywords="logitech media server lms",
    url="https://github.com/txoof/lmsquery",
    packages=['lmsquery'],
    install_requires=['requests'],
    long_description="This library provides easy to use functions to send \
                      queries to a Logitech Media Server \
                      (https://github.com/Logitech/slimserver)",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requries='>3.2'
)
