#!/usr/bin/env python
# vim: ts=4 sw=4 et ai:
import os

from setuptools import setup


def read_file(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        text = f.read()
    return text


if __name__ == "__main__":
    setup(
        name="tftpy",
        use_scm_version=True,
        description="Python TFTP library",
        long_description=read_file("README.rst"),
        long_description_content_type="text/x-rst; charset=UTF-8",
        author="Michael P. Soulier",
        author_email="msoulier@digitaltorque.ca",
        url="http://github.com/msoulier/tftpy",
        packages=["tftpy"],
        scripts=["bin/tftpy_client.py", "bin/tftpy_server.py"],
        project_urls={
            "Documentation": "http://tftpy.sourceforge.net/sphinx/index.html",
            "Source": "https://github.com/msoulier/tftpy/",
            "Tracker": "https://github.com/msoulier/tftpy/issues",
        },
        setup_requires=[
            "setuptools_scm[toml]",
            "setuptools_scm_git_archive >= 1.0",
        ],
        python_requires=">=3.6",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Development Status :: 4 - Beta",
            "Environment :: Console",
            "Environment :: No Input/Output (Daemon)",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Topic :: Internet",
        ],
    )
