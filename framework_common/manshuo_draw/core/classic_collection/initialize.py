import yaml
import os
from framework_common.manshuo_draw.core.util import *
global initialize_yaml_set

def initialize_yaml_must_require(params):
    global initialize_yaml_set
    if 'basic_set' == params['type'] :
        if 'config_path' not in params:
            params['config_path']=get_abs_path('framework_common/manshuo_draw/defalut_config.yaml')
        config_abs_path = get_abs_path(params['config_path'])
        if not os.path.exists(params['config_path']):
            with open(get_abs_path('framework_common/manshuo_draw/defalut_config.yaml'), 'r', encoding='utf-8') as file:
                origin_config_set_yaml = yaml.safe_load(file)
            with open(config_abs_path, 'w', encoding='utf-8') as file:
                yaml.dump(origin_config_set_yaml, file)
            initialize_yaml_set=origin_config_set_yaml
        else:
            try:
                with open(config_abs_path, 'r', encoding='utf-8') as file:
                    initialize_yaml_set = yaml.safe_load(file)
            except Exception as e:
                with open('framework_common/manshuo_draw/defalut_config.yaml', 'r', encoding='utf-8') as file:
                    origin_config_set_yaml = yaml.safe_load(file)
                with open(config_abs_path, 'w', encoding='utf-8') as file:
                    yaml.dump(origin_config_set_yaml, file)
                initialize_yaml_set = origin_config_set_yaml



    if params['type'] not in initialize_yaml_set:
        return [], {}
    if params['type'] in initialize_yaml_set :
        if 'subtype' in params and params['subtype'] not in initialize_yaml_set[params['type']]:
            return initialize_yaml_set[f"{params['type']}"], {}

    must_required_keys = []
    if 'subtype' not in params:
        initialize_yaml_load=initialize_yaml_set[f"{params['type']}"]
    else:
        initialize_yaml_load_check=initialize_yaml_set[f"{params['type']}"]
        initialize_yaml_load_check_reload,initialize_yaml_load_reload={},{}
        for per_yaml in initialize_yaml_load_check:
            if 'must_required_keys' == per_yaml:must_required_keys = initialize_yaml_load_check['must_required_keys']
            if isinstance(initialize_yaml_load_check[per_yaml], dict): continue
            initialize_yaml_load_check_reload[per_yaml]=initialize_yaml_load_check[per_yaml]


        initialize_yaml_load=initialize_yaml_set[f"{params['type']}"][f"{params['subtype']}"]
        for per_yaml in initialize_yaml_load_check_reload:
            initialize_yaml_load_reload[per_yaml]=initialize_yaml_load_check_reload[per_yaml]
        for per_yaml in initialize_yaml_load:
            initialize_yaml_load_reload[per_yaml]=initialize_yaml_load[per_yaml]
        initialize_yaml_load=initialize_yaml_load_reload



    if initialize_yaml_load is None:
        return [], must_required_keys

    if 'must_required_keys' in initialize_yaml_load:#寻找本模块必要的按键，若没有，则为空
        must_required_keys=initialize_yaml_load['must_required_keys']
        initialize_yaml_load.pop('must_required_keys')

    return initialize_yaml_load,must_required_keys

if __name__ == '__main__':
    initialize_yaml_must_require({'type': 'img', 'subtype': 'common'})