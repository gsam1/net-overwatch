import os, sys
import json

def save_to_json(filename, data):
    file = filename + '.json'
    with open(file, 'w') as outfile:
        json.dump(data, outfile)
    

def config(modules):
    '''
        Search the folder for the applications and export them for their full paths.
    '''
    main = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    
    module_location_map = {}
    for module in modules:
        module_path = os.path.join(main, module)
        module_location_map[module] = module_path

    return module_location_map
        

if __name__ == '__main__':
    module_config_map = config(['bot','cli','netmonitor','db'])
    save_to_json('module_map', module_config_map)

