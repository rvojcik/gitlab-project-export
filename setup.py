from os.path import join as path_join, dirname
from setuptools import setup, find_packages

version = '0.1'

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_reqs = fh.read().split()

setup(
    name='gitlab-project-export',
    version=version,
    description=('Simple python project for exporting gitlab projects '
                 'with Export Project feature in GitLab API.'),
    long_description=long_description,
    author='Robert Vojcik',
    author_email='robert@vojcik.net',
    url='https://github.com/rvojcik/gitlab-project-export',
    download_url='https://github.com/rvojcik/gitlab-project-export/archive/master.tar.gz',
    packages=find_packages(),
    install_requires = install_reqs,
    scripts=[
        'gitlab-project-export.py',
        'gitlab-project-import.py',
    ],
    keywords=['gitlab-backup', 'gitlab-export', 'export', 'gitlab', 'backup'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
