from xml.dom.minidom import parseString
import urllib2 as url
import ConfigParser
import MySQLdb as mdb
import utils
import os
import sys

class Wrapper:

    #get_document_batch()
    #Purpose: retrieves batch of documents to process from server
    def get_document_batch(self):
        raise NotImplementedError('Extend me!')

    #get_document_ids()
    #
    #Purpose: parses the ids of all documents in a batch
    #Returns: list of string ids
    def get_document_ids(self):
        raise NotImplementedError('Extend me!')

    #get_document_paths()
    #
    #Purpose: parses the paths of all documents in a batch
    #Returns: list of document paths as strings
    def get_document_paths(self):
        raise NotImplementedError('Extend me!')

    #update_state(ids, state)
    #
    #Purpose: updates the extraction state of the given documents in the database
    #Parameters: ids - list of documents ids, state - the int state to assignt to each document
    def update_state(self, ids, state):
        raise NotImplementedError('Extend me!')

    #on_stop()
    #
    #Purpose: performs any necessary closing statements to free up connections and such
    def on_stop(self):
        raise NotImplementedError('Extend me!')

class FileSystemWrapper(Wrapper):
    'Wrapper using file system and does not communicate with database'

    #Constructor
    #
    #Parameters: rootPath - path to directory that should be proccessed
    #               batchSize - number of documents to process at a time
    def __init__(self, rootPath, batchSize):
        self.batchSize = batchSize
        self.allDocs = []   #stores a list of paths to the documents to process
        self.rootPath = rootPath
        for path, subdirs, files in os.walk(rootPath):
            for name in files:
                if name[-3:] == 'pdf':
                    self.allDocs.append(os.path.join(path, name))
        self.batch = [] #stores a list of paths to the documents to process

    #get_document_batch()
    #Purpose: retrieves batch of documents to process from server
    def get_document_batch(self):
        self.batch = []
        for i in range(0, self.batchSize):
            if len(self.allDocs) > 0:
                self.batch.append(self.allDocs.pop())

    #get_document_ids()
    #
    #Purpose: parses the ids of all documents in a batch
    #Returns: list of string ids
    def get_document_ids(self):
        ids = []
        for docPath in self.batch:
            ids.append(utils.file_name_to_id(docPath[docPath.rfind('/') + 1 : docPath.rfind('.pdf') + 4]))
        return ids

    #get_document_paths()
    #
    #Purpose: parses the paths of all documents in a batch
    #Returns: list of document paths as strings
    def get_document_paths(self):
        paths = []
        for docPath in self.batch:
            paths.append(docPath.replace(self.rootPath, ''))
        return paths

    #update_state(ids, state)
    #
    #Purpose: updates the extraction state of the given documents in the database
    #Parameters: ids - list of documents ids, state - the int state to assignt to each document
    def update_state(self, ids, state):
        return

    #on_stop()
    #
    #Purpose: performs any necessary closing statements to free up connections and such
    def on_stop(self):
        return

#get_connection(host, dbName, user, pass)
#
#Purpose: gets a connection to the database that stores metadata
#Parameters: hostName - hostname that database is on, dbName - name of database,
#                       username, password
#Returns: MySQLConnection object
def get_connection(hostName, dbName, username, password):
    try:
        #con = mdb.connect(user=username, passwd=password, host=hostName, db=dbName)
        con = mdb.connect(hostName, username, password, dbName)
        return con
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    print 'error'
    return None

class MySQLWrapper(Wrapper):
    'Wrapper using mySQL API'

    #Constructor
    #
    #Parameters: config - dict that holds configurations for a database connection,
    #               states - dict that holds map of state values
    def __init__(self, config, states):
        self.connection = get_connection(config['host'], config['database'], config['username'], config['password'])
        self.batchSize = int(config['batchsize'])
        self.startID = config['startid']
        self.states = states
        self.batch = None   #stores a list of document ids

    #on_stop()
    #
    #Purpose: performs any necessary closing statements to free up connections and such
    #Behavior: closes database connection
    def on_stop(self):
        self.connection.close()

    #get_document_batch()
    #
    #Purpose: retrieves batch of documents to process from server
    def get_document_batch(self):
        cursor = self.connection.cursor()
        query = 'SELECT id from main_crawl_document WHERE id> %s and state = %s ORDER BY id LIMIT %s;'

        cursor.execute(query, (self.startID, self.states['crawled'], self.batchSize))

        ids = []
        docs = cursor.fetchall()
        for doc in docs:
            for idnum in doc:
                ids.append(str(idnum))

        self.batch = ids
        cursor.close()

    #get_document_ids()
    #
    #Purpose: parses the ids of all documents in a batch
    #Returns: list of string ids
    def get_document_ids(self):
        return self.batch

    #get_document_paths(docs)
    #
    #Purpose: parses the paths of all documents in a batch
    #Returns: list of document paths as strings
    def get_document_paths(self):
        paths = []
        for ID in self.batch:
            paths.append(utils.id_to_path(ID) + utils.id_to_file_name(ID) + '.pdf')
        return paths

    #update_state(ids, state)
    #
    #Purpose: updates the extraction state of the given documents in the database
    #Parameters: ids - list of document ids, state - the int state to assignt to each document
    def update_state(self, ids, state):
        cursor = self.connection.cursor()
        statement = 'UPDATE main_crawl_document SET state = {0} where id in ({1});'

        idString = ''

        for doc in ids:
            if len(idString) != 0:
                idString += ','
            idString += str(doc)

        statement = statement.format(state, idString)
            
        cursor.execute(statement)

        self.connection.commit()

class HTTPWrapper(Wrapper):
    'Wrapper using the RESTful API'

    #Constructor
    #
    #Parameters: config - dict that holds configurations for a database connection
    def __init__(self, config):
        self.host = config['host']
        self.key = config['key']
        self.batchSize = int(config['batchsize'])
        self.batch = None #stores a DOM with ids and paths

    #get_document_batch()
    #
    #Purpose: retrieves batch of documents to process from server
    def get_document_batch(self):
        request = 'http://' + self.host + '/api/getdocs.xml?key=' + self.key + '&n=' + str(self.batchSize)
        responseString = url.urlopen(request).read()
        response = parseString(responseString)
        docs = response.getElementsByTagName('doc')
        self.batch = docs

    #get_document_ids()
    #
    #Purpose: parses the ids of all documents in a batch
    #Returns: list of string ids
    def get_document_ids(self):
        ids = []
        for element in self.batch:
            ids.append(element.getAttribute('id'))
        return ids

    #get_document_paths(docs)
    #
    #Purpose: parses the paths of all documents in a batch
    #Returns: list of document paths as strings
    def get_document_paths(self):
        paths = []
        for element in self.batch:
            paths.append(element.firstChild.nodeValue)
        return paths

    #update_state(ids, state)
    #
    #Purpose: updates the extraction state of the given documents in the database
    #Parameters: ids - list of documents ids, state - the int state to assignt to each document
    def update_state(self, ids, state):
        idString = ''
        for doc in ids:
            idString = idString + str(doc) + ','
        if len(idString) > 0:
            idString = idString[:-1]
            request = 'http://' + self.host + '/api/setdocs.xml?key=' + self.key + '&ids=' + idString + '&state=' + str(state)
            response = url.urlopen(request).getcode()

    #on_stop()
    #
    #Purpose: perform necessary closing statements
    #Behavior: nothing to do 
    def on_stop(self):
        print 'closed'