from __future__ import absolute_import, division, print_function
import sys
import time
from datetime import datetime
import json
import os

# two directories above the current directory
rootpath = os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0]

try:
    unicode        # Python 2
except NameError:
    unicode = str  # Python 3


def preprocess_config(config):
    fill_default(config)
    if sys.version_info[0] == 2:
        return byteify(config)
    else:
        return config


def fill_default(config):
    set_missing(config, "random_seed", 0)
    set_missing(config, "agent_type", "NNAgent")
    fill_layers_default(config["layers"])
    fill_input_default(config["input"])
    fill_train_config(config["training"])


def fill_train_config(train_config):
    set_missing(train_config, "fast_train", True)
    set_missing(train_config, "decay_rate", 1.0)
    set_missing(train_config, "decay_steps", 50000)


def fill_input_default(input_config):
    set_missing(input_config, "save_memory_mode", False)
    set_missing(input_config, "portion_reversed", False)
    set_missing(input_config, "market", "poloniex")
    set_missing(input_config, "norm_method", "absolute")
    set_missing(input_config, "is_permed", False)
    set_missing(input_config, "fake_ratio", 1)


def fill_layers_default(layers):
    for layer in layers:
        if layer["type"] == "ConvLayer":
            set_missing(layer, "padding", "valid")
            set_missing(layer, "strides", [1, 1])
            set_missing(layer, "activation_function", "relu")
            set_missing(layer, "regularizer", None)
            set_missing(layer, "weight_decay", 0.0)
        elif layer["type"] == "EIIE_Dense":
            set_missing(layer, "activation_function", "relu")
            set_missing(layer, "regularizer", None)
            set_missing(layer, "weight_decay", 0.0)
        elif layer["type"] == "DenseLayer":
            set_missing(layer, "activation_function", "relu")
            set_missing(layer, "regularizer", None)
            set_missing(layer, "weight_decay", 0.0)
        elif layer["type"] == "EIIE_LSTM" or layer["type"] == "EIIE_RNN":
            set_missing(layer, "dropouts", None)
        elif layer["type"] == "EIIE_Output" or\
                layer["type"] == "Output_WithW" or\
                layer["type"] == "EIIE_Output_WithW":
            set_missing(layer, "regularizer", None)
            set_missing(layer, "weight_decay", 0.0)
        elif layer["type"] == "DropOut":
            pass
        else:
            raise ValueError("layer name {} not supported".format(layer["type"]))


def set_missing(config, name, value):
    if name not in config:
        config[name] = value


def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return str(input)
    else:
        return input


def parse_time(time_string):
    try: 
        return time.mktime(datetime.strptime(time_string, "%Y/%m/%d").timetuple())
    except ValueError:
        return time.mktime(datetime.strptime(time_string, "%Y/%m/%d %H:%M:%S").timetuple())


def load_config(index=None):
    """
    @:param index: if None, load the default in pgportfolio;
     if a integer, load the config under train_package
    """
    if index:
        with open(rootpath+"/train_package/" + str(index) + "/net_config.json") as file:
            config = json.load(file)
    else:
        with open(rootpath+"/pgportfolio/" + "net_config.json") as file:
            config = json.load(file)
    return preprocess_config(config)

def load_default_config():
    """
    load the default configuration net_config.json
    """
    filename = os.path.join(rootpath,"pgportfolio", "net_config.json")
    with open(filename) as file:
        config = json.load(file)
    print("returning %s contents %s" % (filename, config))
    return preprocess_config(config)    

def check_input_same(config1, config2):
    input1 = config1["input"]
    input2 = config2["input"]
    if input1["start_date"] != input2["start_date"]:
        return False
    elif input1["end_date"] != input2["end_date"]:
        return False
    elif input1["test_portion"] != input2["test_portion"]:
        return False
    else:
        return True

def find_var_differences(config_variables, default_config):
    differences = []
    def find_differences(obj, path):
        if type(obj) == dict:
            for key in obj.keys():
                combined_key = _construct_path(path, key)
                find_differences(obj[key], combined_key)
        else:
            if not(_get_path(default_config, path) == obj):
                if type(obj) == list:
                    differences.append([path, obj])
                else:
                    raise ValueError("difference from default_config detected at %s, but type %s not supported" % (path, type(obj)))
    find_differences(config_variables, '')
    return differences
                             
def _construct_path(path, key):
    if len(path) == 0:
        return key
    return '{}|{}'.format(path, key)
                             
def _get_path(config, combined_key):
    keys = combined_key.split('|')
    obj = config
    for key in keys:
        obj = obj[key]
    return obj

def _set_path(config, combined_key, value):
    keys = combined_key.split('|')
    obj = config
    for key in keys[:-1]:
        obj = obj[key]
    obj[keys[-1]] = value
