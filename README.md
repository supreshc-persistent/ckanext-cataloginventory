## ckanext-cataloginventory
extension to list the metadata of datasets in a resource of a dataset named 'dataset-of-datasets'


## Requirements

**This plugin is compatible with CKAN 2.7 or later**

This plugin uses CKAN [background jobs](http://docs.ckan.org/en/latest/maintaining/background-tasks.html) that was introduced in CKAN 2.7

This plugin need an existing dataset with name 'dataset-of-datasets'


## Installation

To install ckanext-cataloginventory, ensure you have installed ckanext-scheming:

1. Activate your CKAN virtual environment:
```
. /usr/lib/ckan/default/bin/activate
```

2. Download the extension's github repository:
```
cd /usr/lib/ckan/default/src
git clone https://github.com/supreshc-persistent/ckanext-cataloginventory.git
```

3. Install the extension into your virtual environment:
```
cd ckanext-cataloginventory
python setup.py develop
```

4. Add/Update an existing dataset and run the background job command to trigger adding of metadata of datasets for a resource under dataset-of-datasets 


## Background Jobs
**Development**

Workers can be started using the [Run a background job worker](http://docs.ckan.org/en/latest/maintaining/paster.html#paster-jobs-worker) command:

paster --plugin=ckan jobs worker --config=/etc/ckan/default/development.ini

**Production**

In a production setting, the worker should be run in a more robust way. One possibility is to use Supervisor.

For more information on setting up background jobs using Supervisor click [here](http://docs.ckan.org/en/latest/maintaining/background-tasks.html#using-supervisor).

