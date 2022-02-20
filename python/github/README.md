# GitHub scrits

## `./branches_per_repo.py -h`

```shell
usage: branches_per_repo.py [-h] [-t TOKEN] [-o ORGANIZATION]

Obtain github repositories and how many branches they each have

optional arguments:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        GitHub user token or use environment variable GITHUB_TOKEN
  -o ORGANIZATION, --organization ORGANIZATION
                        GitHub Organization name or use environment variable GITHUB_ORGANIZATION
```

## `./readonly_team.py -h`

```shell
usage: readonly_team.py [-h]
                        [-l {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
                        [-o ORGANIZATION]
                        [-t TOKEN]
                        [--team TEAM]

Give read only access to a given team in a GitHub Organization

options:
  -h, --help   show this help message and exit
  -l {CRITICAL,ERROR,WARNING,INFO,DEBUG}, --log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}
               Set the logging output level
  -o ORGANIZATION, --organization ORGANIZATION
               GitHub Organization name or use environment variable GITHUB_ORGANIZATION
  -t TOKEN, --token TOKEN
               GitHub user token or use environment variable GITHUB_TOKEN
  --team TEAM  Team name within GitHub org token or use environment variable GITHUB_TEAM
```
