import yaml
import os

global initialize_yaml_set

def initialize_yaml_must_require(params):
    global initialize_yaml_set
    if 'basic_set' == params['type'] :
        if 'config_path' not in params:
            params['config_path']='framework_common/manshuo_draw/defalut_config.yaml'

        if not os.path.exists(params['config_path']):
            with open('framework_common/manshuo_draw/defalut_config.yaml', 'r') as file:
                origin_config_set_yaml = yaml.safe_load(file)
            with open(params['config_path'], 'w') as file:
                yaml.dump(origin_config_set_yaml, file)
            initialize_yaml_set=origin_config_set_yaml
        else:
            try:
                with open(params['config_path'], 'r') as file:
                    initialize_yaml_set = yaml.safe_load(file)
            except Exception as e:
                with open('framework_common/manshuo_draw/defalut_config.yaml', 'r') as file:
                    origin_config_set_yaml = yaml.safe_load(file)
                with open(params['config_path'], 'w') as file:
                    yaml.dump(origin_config_set_yaml, file)
                initialize_yaml_set = origin_config_set_yaml

    if params['type'] not in initialize_yaml_set:
        return [], {}
    if params['type'] in initialize_yaml_set :
        if 'subtype' in params and params['subtype'] not in initialize_yaml_set[params['type']]:
            return [], {}

    if 'subtype' not in params:
        initialize_yaml_load=initialize_yaml_set[f"{params['type']}"]
    else:
        initialize_yaml_load=initialize_yaml_set[f"{params['type']}"][f"{params['subtype']}"]

    must_required_keys = []
    if initialize_yaml_load is None:
        return [], must_required_keys
    if 'must_required_keys' in initialize_yaml_load:#寻找本模块必要的按键，若没有，则为空
        must_required_keys=initialize_yaml_load['must_required_keys']
        initialize_yaml_load.pop('must_required_keys')

    return initialize_yaml_load,must_required_keys

