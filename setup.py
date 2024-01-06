"""
Create pii-transform as a Python package
"""

import io
import sys
import re
from pathlib import Path
from collections import defaultdict

from setuptools import setup, find_packages

from typing import Dict, List

from src.pii_transform import VERSION

PKGNAME = "pii-transform"
GITHUB_URL = "https://github.com/piisa/" + PKGNAME

# --------------------------------------------------------------------

PYTHON_VERSION = (3, 8)

if sys.version_info < PYTHON_VERSION:
    sys.exit(
        "**** Sorry, {} {} needs at least Python {}".format(
            PKGNAME, VERSION, ".".join(map(str, PYTHON_VERSION))
        )
    )


def requirements(filename="requirements.txt"):
    """Read the requirements file"""
    with io.open(filename, "r") as f:
        return [line.strip() for line in f if line and line[0] != "#"]


def requirements_extra(filename: str = 'requirements.txt') -> Dict[str, List[str]]:
    '''Read the requirements file, separating "extra" requirements'''
    pathname = Path(__file__).parent / filename
    req = defaultdict(list)
    sp = lambda s: s.strip().split(':')
    fl = lambda s: s[0] and s[0][0] != '#'
    with open(pathname, 'r') as f:
        for item in filter(fl, map(sp, f)):
            req[None if len(item) == 1 else item[0]].append(item[-1])
    return req


def long_description() -> str:
    """
    Take the README and remove markdown hyperlinks
    """
    readme = Path(__file__).parent / "README.md"
    with open(readme, "rt", encoding="utf-8") as f:
        desc = f.read()
        desc = re.sub(r"^\[ ! \[ [\w\s]+ \] .+ \n", "", desc, flags=re.X | re.M)
        desc = re.sub(r"^\[ ([^\]]+) \]: \s+ \S.*\n", "", desc, flags=re.X | re.M)
        return re.sub(r"\[ ([^\]]+) \]", r"\1", desc, flags=re.X)


# --------------------------------------------------------------------


setup_args = dict(
    # Metadata
    name=PKGNAME,
    version=VERSION,
    author="Paulo Villegas",
    author_email="paulo.vllgs@gmail.com",
    description="Transform recognized PII instances in a document",
    long_description_content_type="text/markdown",
    long_description=long_description(),
    license="Apache",
    url=GITHUB_URL,
    download_url=GITHUB_URL + "/tarball/v" + VERSION,
    # Locate packages
    packages=find_packages("src"),  # [ PKGNAME ],
    package_dir={"": "src"},
    # Requirements
    python_requires=">=3.8",
    # Optional requirements
    extras_require={
        "test": ["pytest", "nose", "coverage"],
    },
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "pii-transform = pii_transform.app.transform:main",
            "pii-process = pii_transform.app.process:main",
            "pii-process-jsonl = pii_transform.app.multi:main",
        ]
    },
    include_package_data=False,
    package_data={
        'pii_transform': ['resources/*.json'],
    },
    # Post-install hooks
    cmdclass={},
    keywords=["PIISA, PII"],
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)

if __name__ == "__main__":
    # Add requirements
    reqs = requirements_extra()
    setup_args['install_requires'] = reqs[None]
    for k in filter(None, reqs):
        setup_args['extras_require'][k] = reqs[k]
    # Setup
    setup(**setup_args)
