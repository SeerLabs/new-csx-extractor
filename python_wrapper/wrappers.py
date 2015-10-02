from xml.dom.minidom import parseString
import urllib2 as url
import ConfigParser
import mysql.connector
from mysql.connector import errorcode
import utils

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

class MySQLWrapper(Wrapper):
    'Wrapper using mySQL API'

    #Constructor
    #
    #Parameters: config - dict that holds configurations for a database connection,
    #               states - dict that holds map of state values
    def __init__(self, config, states):
        self.connection = get_connection(config['host'], config['database'], config['username'], config['password'])
        self.batchSize = config['batchSize']
        self.startID = config['startID']
        self.states = states
        self.batch = None   #stores a list of document ids

    #get_connection(host, dbName, user, pass)
    #
    #Purpose: gets a connection to the database that stores metadata
    #Parameters: host - hostname that database is on, dbName - name of database,
    #                       username, password
    #Returns: MySQLConnection object
    def get_connection(self, host, dbName, username, password):
        try:
            con = mysql.connector.connect(user=username, pass=password, host=host, database=dbName)
            return con
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        return null

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
        cursor = connection.cursor()
        query = 'SELECT id from main_crawl_document WHERE id> %s and state = %s ORDER BY id LIMIT %s;'

        cursor.execute(query, (self.startID, self.states['CRAWLED'], self.batchSize))

        ids = []
        for doc in cursor:
            ids.append(str(doc))

        print ids

        self.batch = ids
        cursor.close()

    #get_document_ids()
    #
    #Purpose: parses the ids of all documents in a batch
    #Returns: list of string ids
    def get_document_ids(self):
        return batch

    #get_document_paths(docs)
    #
    #Purpose: parses the paths of all documents in a batch
    #Returns: list of document paths as strings
    def get_document_paths(self):
        paths = []
        for ID in self.batch:
            paths.append(utils.id_to_path(ID) + util.id_to_file_name(ID) + '.pdf')
        return paths

    #update_state(ids, state)
    #
    #Purpose: updates the extraction state of the given documents in the database
    #Parameters: ids - list of document ids, state - the int state to assignt to each document
    def update_state(self, ids, state):
        cursor = connection.cursor()
        statement = 'UPDATE main_crawl_document SET state = %s where id in (%s);'

        idString = ''

        for doc in ids:
            if len(idString) != 0:
                idString += ','
            idString += doc

        cursor.execute(statement, (state, idString))

        connection.commit()
        cursor.close()

class HTTPWrapper(Wrapper):
    'Wrapper using the HTTP API'

    #Constructor
    #
    #Parameters: config - dict that holds configurations for a database connection
    def __init__(self, config):
        self.host = config['host']
        self.key = config['key']
        self.batchSize = config['batchSize']
        self.batch = None #stores a DOM with ids and paths

    #get_document_batch()
    #
    #Purpose: retrieves batch of documents to process from server
    def get_document_batch(self):
        request = 'http://' + self.host + '/api/getdocs.xml?key=' + self.key + '&n=' + self.batchSize
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
        print ids
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
        for id in ids:
            idString = idString + str(id) + ','
        if len(idString) > 0:
            idString = idString[:-1]
            request = 'http://' + self.host + '/api/setdocs.xml?key=' + self.key + '&ids=' + idString + '&state=' + str(state)
            response = url.urlopen(request).getcode()
            print response

    #on_stop()
    #
    #Purpose: perform necessary closing statements
    #Behavior: nothing to do 
    def on_stop(self):
        print 'closed'