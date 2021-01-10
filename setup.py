from os.path import join as path_join, dirname
from setuptools import setup, find_packages

version = '0.1'
README = path_join(dirname(__file__), 'README.md')
long_description = open(README).read()
setup(
    name='gitlab-project-export',
    version=version,
    description=('Simple python project for exporting gitlab projects '
                 'with Export Project feature in GitLab API.'),
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
    ],
    author='Robert Vojcik',
    author_email='robert@vojcik.net',
    url='https://github.com/rvojcik/gitlab-project-export',
    download_url='https://github.com/rvojcik/gitlab-project-export/archive/master.tar.gz',
    packages=(['lib']),
    install_requires = [
        'pyyaml',
        'requests',
    ],
    scripts=[
        'gitlab-project-export.py',
        'gitlab-project-import.py',
    ],
)
