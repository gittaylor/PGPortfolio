import json
import os
import logging
from tools import configprocess
import csv
from copy import deepcopy

def add_packages(config, repeat=1):
    train_dir = "train_package"
    package_dir = os.path.realpath(__file__).replace('pgportfolio/autotrain/generate.pyc',train_dir)\
        .replace("pgportfolio\\autotrain\\generate.pyc", train_dir)\
                  .replace('pgportfolio/autotrain/generate.py',train_dir)\
        .replace("pgportfolio\\autotrain\\generate.py", train_dir)
    all_subdir = [int(s) for s in os.listdir(package_dir) if os.path.isdir(package_dir+"/"+s)]
    if all_subdir:
        max_dir_num = max(all_subdir)
    else:
        max_dir_num = 0
    indexes = []

    for i in range(repeat):
        max_dir_num += 1
        directory = package_dir+"/"+str(max_dir_num)
        config["random_seed"] = i
        os.makedirs(directory)
        indexes.append(max_dir_num)
        with open(directory + "/" + "net_config.json", 'w') as outfile:
            json.dump(config, outfile, indent=4, sort_keys=True)
    logging.info("create indexes %s" % indexes)
    return indexes

def parameter_sweep(config_variables):
    """Creates packages for each combination of variables included in config_variables
    If a variable is presented as a single value, e.g. {'training': {'learning_rate': 0.00028}},
    then the single variable is kept across all training runs.  If a variable is presented as an array,
    e.g. {'training': {'learning_rate': [0.028, 0.0028, 0.00028]}}, each one is tried combinatorically
    with other parameters
    """
    default_config = configprocess.load_default_config()
    var_parameters = configprocess.find_var_differences(config_variables, default_config)
    parameters = [default_config]
    for combined_key, values in var_parameters:
        new_parameters = []
        for value in values:
            current_parameters = [deepcopy(i) for i in parameters]
            for param_set in current_parameters:
                configprocess._set_path(param_set, combined_key, value)
            new_parameters.extend(current_parameters)
            print("key %s adds value %s to %s param_sets" % (combined_key, value, len(current_parameters)))
        parameters = new_parameters
    return parameters
    for param_set in parameters:
        add_packages(param_set, repeat=1)


def add_parameter(config, combined_parameter, values):
    if type(values) == list:
        configprocess._set_path(config, combined_parameter, values)
    else:
        raise ValueError("parameter additions must be lists. type {} is not supported".format(type(values)))

def parameters_to_csv(parameters, filename):
    canonical = parameters[0]
    cols = []
    for key in canonical:
        if type(canonical[key]) == dict:
            for subkey in canonical[key]:
                cols.append(configprocess._construct_path(key, subkey))
        else:
           cols.append(key)
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        for param_set in parameters:
            writer.writerow([configprocess._get_path(param_set, col) for col in cols])
