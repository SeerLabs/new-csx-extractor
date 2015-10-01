import os

#file_name_to_id(fileName)
#
#Purpose: converts a xxx.xxx.xxx.pdf to xxxxxxxxx
#Parameters: fileName - string in xxx.xxx.xxx.pdf format
def file_name_to_id(fileName):
    id = fileName.replace('.', '')[:-3]
    return id

#id_to_file_name(id)
#
#Purpose: converts xxxxxxxxx to xxx.xxx.xxx
#Parameters: id - id string of file
def id_to_file_name(id):
    fileName = id[:3] + '.' + id[3:6] + '.' + id[6:]
    return fileName

#id_to_path(id)
#
#Purpose: converts xxxxxxxxx to xxx/xxx/xxx/
#Parameters: id - id string of document
def id_to_path(id):
    path = id[:3] + '/' + id[3:6] + '/' + id[6:] + '/'

#expand_path(path)
#
#Purpose: converts ~ to absolute path
#Parameters: path - path to convert
#Returns: absolute path
def expand_path(path):
   return os.path.abspath(os.path.expanduser(path))