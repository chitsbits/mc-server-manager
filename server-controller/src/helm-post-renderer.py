import sys
import yaml

def modify_manifest(yaml_manifest, server_name):
    resources = yaml.safe_load_all(yaml_manifest)
    modified_resources = []
    for resource in resources:
        if resource is not None:
            # Add or modify labels and names
            if 'metadata' in resource:
                resource['metadata']['labels'] = resource.get('metadata', {}).get('labels', {})
                resource['metadata']['labels']['serverName'] = server_name
            modified_resources.append(resource)
    return yaml.dump_all(modified_resources)

if __name__ == '__main__':
    server_name = sys.argv[1]
    yaml_input = sys.stdin.read()
    modified_output = modify_manifest(yaml_input, server_name)
    sys.stdout.write(modified_output)