from pickle import dump, load, HIGHEST_PROTOCOL
from os import path
import traceback
import imp

from pgportfolio.test.functiondev import *

cur_dir = path.split(__file__)[0]

def dump_to_file(pystruct, filename):
    with open(filename, 'wb') as dump_file:
        dump(pystruct, dump_file, HIGHEST_PROTOCOL)
    return filename

def load_from_file(filename):
    with open(filename, 'rb') as load_file:
        pystruct = load(load_file)
    return pystruct

def save_state(object, object_name):
    object_class = '{}.{}'.format(type(object).__module__, object.__class__.__name__)
    return dump_to_file(object, path.join(cur_dir, '{}|{}.pickle'.format(object_name, object_class)))

def load_state(filename):
    object = load_from_file(path.join(cur_dir,filename))
    object_name, object_class = filename.split('|')
    object_class = object_class[:-7]
    if object_class_function(object_class) in globals():
        globals()[object_class_function(object_class)](object)
    return object_name, object

def object_class_function(object_class):
    return 'update' + object_class.replace('.', '_')

def pdb_try_again(function, *args, **kwargs):
    from pgportfolio.test import functiondev
    try:
        return function(*args, **kwargs)
    except Exception:
        traceback.print_exc()
        try_again = True
        import pdb; pdb.set_trace()
        imp.reload(functiondev)
        function = getattr(functiondev, function.__name__)
        if try_again:
            pdb_try_again(function, *args, **kwargs)
