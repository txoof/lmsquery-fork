from lmsquery import const

#try:
#    from setuptools import setup
#except ImportError:
#    from distutils.core import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="LMSQuery-fork",
    version=const.LMSQUERY_VERSION,
    author="Robert Einhausi, Aaron Ciuffo",
    author_email="aaron.ciuffo@gmail.com",
    description=("Query library for Logitech Media Server"),
    license="MIT",
    keywords="logitech media server lms",
    url="https://github.com/txoof/lmsquery",
    packages=setuptools.find_packages(),
    install_requires=['requests'],
    long_description = long_description,
    long_description_content_type = "text/markdown",
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
    python_requries='>3.6'
)
