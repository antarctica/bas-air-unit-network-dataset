/title 0.0.0 release

1. [x] create a release issue
1. [ ] update release issue title and associate with relevant milestone
1. [ ] create merge request from release issue
1. [ ] bump Python package version `poetry version [minor/patch]`
1. [ ] close release in `CHANGELOG.md`
1. [ ] push changes, merge into `main` and tag commit with version
1. [ ] create new [GitLab release](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/releases)
    - set title to related release
    - set release notes to change log entry
    - associate with relevant tag and milestone 
    - add link to [PyPi package](https://pypi.org/project/bas-air-unit-network-dataset/#history)
    - add link to the README from the relevant tag (to create a version specific link)
