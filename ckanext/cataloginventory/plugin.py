import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanapi
from ckanext.scheming import helpers
try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config


PACKAGE_ID = config.get('ckan.datasetofdatasets_name', 'dataset-of-datasets')

class CataloginventoryPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController,inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'cataloginventory')

    def after_create(self, context, pkg_dict):
        if pkg_dict.get('private') is False:
            if pkg_dict.get('name') != PACKAGE_ID:
                addupdate_datasetlist(pkg_dict)

    def after_update(self, context, pkg_dict):
        if pkg_dict.get('private') is False:
            if pkg_dict.get('name') != PACKAGE_ID:
                addupdate_datasetlist(pkg_dict)
        else:
            delete_datasetlist_record(pkg_dict)

    def after_delete(self, context, pkg_dict):
        if pkg_dict.get('name') != PACKAGE_ID:
            delete_datasetlist_record(pkg_dict)

def addupdate_datasetlist(pkg_dict):
    dataset_fields = get_dataset_fields()
    lc = ckanapi.LocalCKAN()  # running as site user
    try:
        list_pkg_dict = lc.action.package_show(id=PACKAGE_ID)
    except:
        return

    resources = list_pkg_dict['resources']

    if len(resources) == 0:
        #create resource and upsert metadata metadata
        plugins.toolkit.enqueue_job(add_dataset_resource, [list_pkg_dict])
    else:
        #upsert dataset metadata in resource
        resource_exits = False
        for resource in resources:
            if resource.get('name') == 'Datasets List':
                resource_exits = True
                res_id = resource.get('id')
                records = []
                record_data = {}
                for key in dataset_fields:
                    if key in pkg_dict or key == 'tag_string':
                        if key == 'tag_string':
                            record_data[dataset_fields[key]] = get_package_tags(pkg_dict.get('tags'))
                        elif key == 'owner_org':
                            if pkg_dict['owner_org'] is not None:
                                record_data[dataset_fields[key]] = get_organization_data(pkg_dict['owner_org'])['title']
                            else:
                                record_data[dataset_fields[key]] = ''
                        else:
                            record_data[dataset_fields[key]] = pkg_dict[key]
                    else:
                        record_data[dataset_fields[key]] = ''

                records.append(record_data)
                upsert_record = lc.action.datastore_upsert(resource_id=res_id,records=records)

        #if resource with title 'Datasets List' does not exist then create the resource
        if resource_exits is False:
            plugins.toolkit.enqueue_job(add_dataset_resource, [list_pkg_dict])

#function to create a new resource for dataset and add all the metadata of datasets for the resource
def add_dataset_resource(list_pkg_dict):
    dataset_fields = get_dataset_fields()
    site_packages = get_packages_data()
    records = []
    for site_package in site_packages:
        record_data = {}
        for key in dataset_fields:
            if key in site_package or key == 'tag_string':
                if key == 'tag_string':
                    record_data[dataset_fields[key]] = get_package_tags(site_package.get('tags'))
                elif key == 'owner_org':
                    if site_package['owner_org'] is not None:
                        record_data[dataset_fields[key]] = site_package['organization']['title']
                    else:
                        record_data[dataset_fields[key]] = ''
                else:
                    record_data[dataset_fields[key]] = site_package[key]
            else:
                record_data[dataset_fields[key]] = ''
        records.append(record_data)

    lc = ckanapi.LocalCKAN()
    resource = {'package_id':list_pkg_dict['name'],'name':'Datasets List','resource_type':'csv'}
    upsert_record = lc.action.datastore_create(resource=resource,records=records,primary_key=['URL'])

#function to delete the record from the resource when dataset is deleted or made private
def delete_datasetlist_record(pkg_dict):
    lc = ckanapi.LocalCKAN()
    try:
        list_pkg_dict = lc.action.package_show(id=PACKAGE_ID)
    except:
        return

    resources = list_pkg_dict['resources']
    dataset_fields = get_dataset_fields()

    if len(resources) > 0:
        for resource in resources:
            if resource.get('title') == 'Datasets List':
                res_id = resource.get('id')
                filters={dataset_fields.get('name'):pkg_dict.get('name')}
                delete_record = lc.action.datastore_delete(resource_id=res_id,filters=filters)




#function to get the schema dataset fields
def get_dataset_fields():
    try:
        lc = ckanapi.LocalCKAN()
        schema_dataset_fields = lc.action.scheming_dataset_schema_show(type='dataset')['dataset_fields']
    except:
        schema_dataset_fields = helpers.scheming_get_dataset_schema("dataset")['dataset_fields']
    dataset_fields = {}
    for schema_dataset_field in schema_dataset_fields:
        dataset_fields[schema_dataset_field['field_name']] = schema_dataset_field['label']
    return dataset_fields

#function to get the package tags as comma seperated string
def get_package_tags(tags_dict):
    """
    Build out the tag names comma separated string
    """
    tags = [tag.get('display_name') for tag in tags_dict]
    return ",".join(tags)

#function to get the organization details
def get_organization_data(org_id):
    try:
        lc = ckanapi.LocalCKAN()
        org_data = lc.action.organization_show(id=org_id)
    except:
        org_data = []
    return org_data

#function to fetch all the sites datasets
def get_packages_data():
    response=[]
    lc = ckanapi.LocalCKAN()
    package_list = lc.action.package_list()

    for package in package_list:
        if package == PACKAGE_ID:
            continue
        package_data = lc.action.package_show(id=package)

        if package_data.get('private') is False:
            response.append(package_data)

    return response

