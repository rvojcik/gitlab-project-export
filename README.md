# gitlab-project-export

Simple Python project for exporting gitlab projects with Export Project feature in GitLab API.

Primarily useful for remote backup of projects in GitLab.com to private storage server.

## Breaking Changes

### 05-2020

Code was modified to work with Python3, not longer compatible with Python2.

## Prerequisite

* Configured Gitlab API Token, https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html

## Install

Simply install via pip:

`pip install gitlab-project-export`

or

`pip install git+https://github.com/rvojcik/gitlab-project-export`

or clone the project and install manually:

```bash
git clone https://github.com/rvojcik/gitlab-project-export
cd gitlab-project-export/
sudo python3 setup.py install
```

or use it without installing to your environment (install only requirements):

```bash
git clone https://github.com/rvojcik/gitlab-project-export
cd gitlab-project-export/
pip install -f requirements.txt
```

## Usage

```bash
usage: gitlab-project-export.py [-h] [-c CONFIG] [-d] [-f]

optional arguments:
  -h, --help  show this help message and exit
  -c CONFIG   config file
  -d          Debug mode
  -f          Force mode - overwrite backup file if exists
  -n          Only print what would be done, without doing it
```

```bash
usage: gitlab-project-import.py [-h] [-c CONFIG] [-f FILEPATH] [-p PROJECT_PATH] [-d]

optional arguments:
  -h, --help       show this help message and exit
  -c CONFIG        config file
  -f FILEPATH      Path to gitlab exported project file
  -p PROJECT_PATH  Project path
  -d               Debug mode
```

Prepare and edit your config file

`mv config-example.yml config.yml`

Simply run the script with optional config parameter

`./gitlab-project-export.py -c /path/to/config.yml`

## Configuration

System uses simple yaml file as configuration.

Example below

```
gitlab:                                                   - gitlab configuration
  access:
    gitlab_url: "https://gitlab.com"                      - GitLab url, official or your instance
    token: "MY_PERSONAL_SECRET_TOKEN"                     - personal access token
  projects:                                               - list of projects to export
    - rvojcik/example-project

backup:                                                   - backup configuration
  destination: "/data/backup"                             - base backup dir
  project_dirs: True                                      - store projects in separate directories
  backup_name: "gitlab-com-{PROJECT_NAME}-{TIME}.tar.gz"  - backup file template
  backup_time_format: "%Y%m%d"                            - TIME template, use whatever compatible with
                                                            python datetime - date.strftime()
  retention_period: 3                                     - purge files in the destination older than the specified value (in days)
  ```

### Backup use-case in cron

Create cron file in `/etc/cron.d/gitlab-backup`

With following content

```bash
MAILTO=your_email@here.tld

0 1 * * * root /path/to/cloned-repo/gitlab-project-export.py -c /etc/gitlab-export/config.yml

```

### Migration use-case

First create two config files

`config1.yml` for exporting our project from gitlab.com

```
gitlab:                                                   - gitlab configuration
  access:
    gitlab_url: "https://gitlab.com"                      - GitLab url, official or your instance
    token: "MY_PERSONAL_SECRET_TOKEN"                     - personal access token
  projects:                                               - list of projects to export
    - rvojcik/project1
    - rvojcik/project2

backup:                                                   - backup configuration
  destination: "/data/export-dir"                         - base backup dir
  backup_name: "gitlab-com-{PROJECT_NAME}-{TIME}.tar.gz"  - backup file template
  backup_time_format: "%Y%m%d"                            - TIME template, use whatever compatible with
                                                            python datetime - date.strftime()
```

and `config2.yml` where we need only gitlab access part for importing projects to private gitlab instance

```
gitlab:                                                   - gitlab configuration
  access:
    gitlab_url: "https://gitlab.privatedomain.tld"        - GitLab url, official or your instance
    token: "MY_PERSONAL_SECRET_TOKEN"                     - personal access token
```

Now it's time to export our projects

```bash
./gitlab-project-export.py -c ./config1.yml -d
```

Your projects are now exported in `/data/export-dir`

After that we use `gitlab-project-import.py` with `config2.yml` for importing into our pricate gitlab instance.

```bash
./gitlab-project-import.py -c ./config2.yml -f ./gitlab-com-rvojcik-project1-20181224.tar.gz -p "rvojcik/project1"
./gitlab-project-import.py -c ./config2.yml -f ./gitlab-com-rvojcik-project2-20181224.tar.gz -p "rvojcik/project2"
```

Done ;)
