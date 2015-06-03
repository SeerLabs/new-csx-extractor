from extraction.runnables import Extractor, RunnableError, ExtractorResult
import extraction.utils
import config
import interfaces
import filters
import utils
import defusedxml.ElementTree as safeET
import xml.etree.ElementTree as ET
import subprocess32 as subprocess
import requests
import os
import glob
import re
import tempfile

# Takes a plain text version of a PDF and uses ParsCit to extract citations
# Returns an xml document of citation info in CSX format
class ParsCitCitationExtractor(interfaces.CSXCitationExtractor):
   dependencies = frozenset([interfaces.PlainTextExtractor, filters.AcademicPaperFilter])

   result_file_name = '.cite'

   def extract(self, data, dependency_results):
      # Get the plain text file of the PDF and write it to a temporary location
      pdf_text = dependency_results[interfaces.PlainTextExtractor].files['.txt']
      text_file_path = extraction.utils.temp_file(pdf_text)

      # Run parscit on the text file to extract citations
      try:
         status, stdout, stderr = extraction.utils.external_process(['perl', config.PARSCIT_PATH, text_file_path], timeout=20)
      except subprocess.TimeoutExpired as te:
         raise RunnableError('ParsCit timed out while processing document')
      finally:
         os.remove(text_file_path)

      if status != 0:
         raise RunnableError('ParsCit Failure. Possible error:\n' + stderr)

      # ParsCit will give us a string representing an xml doc
      # convert from string type  into an xml object
      xml = safeET.fromstring(stdout)

      return ExtractorResult(xml_result=xml)

class PDFFiguresExtractor(Extractor):
   dependencies = frozenset([filters.AcademicPaperFilter])
   result_file_name = '.figures'

   def extract(self, data, dependency_results):
      results_dir = tempfile.mkdtemp() + '/'
      temp_pdf_file = extraction.utils.temp_file(data)

      try:
         command_args = [config.PDFFIGURES_PATH, '-o', results_dir, '-j', results_dir, temp_pdf_file]
         status, stdout, stderr = extraction.utils.external_process(command_args, timeout=20)
      except subprocess.TimeoutExpired:
         shutil.rmtree(results_dir)
         raise RunnableError('PDFFigures timed out while processing document')
      finally:
         os.remove(temp_pdf_file)

      if status != 0:
         raise RunnableError('PDFFigures Failure. Possible error:\n' + stderr)

      # Handle png results
      files = {}
      for path in glob.glob(results_dir + '*.png'):
         # basename looks something like this: -Figure-X.png
         # remove the hyphen and replace with a '.', because framework will add filename prefix later
         filename = '.' + os.path.basename(path)[1:]
         files[filename] = open(path, 'rb').read()

      # Handle json results
      for path in glob.glob(results_dir + '*.json'):
         filename = '.' + os.path.basename(path)[1:]
         files[filename] = open(path, 'r').read()

      return ExtractorResult(xml_result=None, files=files)



      

# Takes a TEI xml file of a document (at least containing header info)
# and outputs an xml file containing header info in CSX format
class TEItoHeaderExtractor(interfaces.CSXHeaderExtractor):
   dependencies = frozenset([interfaces.HeaderTEIExtractor])
   result_file_name = '.header'

   # Essentilly this whole method just finds the relative info in the Grobid xml file
   # and writes it into the CSX format xml file
   def extract(self, data, dep_results):
      tei_root = dep_results[interfaces.HeaderTEIExtractor].xml_result
      result_root = ET.Element('algorithm', {'name': 'Grobid Header Extraction', 'version': '0.1'})

      # Retrieve title from TEI doc
      title = tei_root.find('./teiHeader//titleStmt/title')
      if title is not None:
         ET.SubElement(result_root, 'title').text = title.text
      else:
         raise RunnableError('No title found in TEI document')

      # Find document-level affiliations
      affiliations = tei_root.findall('./teiHeader//sourceDesc/biblStruct/analytic/affiliation')
      if affiliations:
         affiliation_str = " | ".join(map(_get_affiliation_str, affiliations))
         ET.SubElement(result_root, 'affiliation').text = affiliation_str
         

      # Retreive author names from TEI doc
      authors = tei_root.findall('./teiHeader//biblStruct//author')
      authors_node = ET.SubElement(result_root, 'authors')
      if authors is not None and len(authors):
         for author in authors:
            author_node = ET.SubElement(authors_node, 'author')

            # Find and output name-related info
            name_tags = []
            name_tags.extend(author.findall("./persName/forename"))
            name_tags.extend(author.findall('./persName/surname'))

            name_parts = [name.text for name in name_tags if name is not None]
            name = ' '.join(name_parts)
            ET.SubElement(author_node, 'name').text = name

            # Find and output affilliation-related info
            affiliations = author.findall('./affiliation')
            if affiliations:
               # Use a pipe to delimit seperate affiliations
               affiliation_str = " | ".join(map(_get_affiliation_str, affiliations))
               ET.SubElement(author_node, 'affiliation').text = affiliation_str

      else:
         self.log('No authors found')


      # Retreive keywords from TEI doc
      keywords = tei_root.findall('./teiHeader//keywords//item/term')
      keywords_node = ET.SubElement(result_root, 'keywords')
      if keywords is not None and len(keywords):
         for term in keywords:
            ET.SubElement(keywords_node, 'keyword').text = term.text
      else:
         self.log('No keywords found')

      # Try and find an abstract
      divs = tei_root.findall('./text//div')
      abstracts = [div for div in divs if div.get('type') == 'abstract']
      if abstracts:
         abstract = abstracts[0]
         xml_string = ET.tostring(abstract)
         remove_heading = re.compile(r'\s*<head.*?>.*?<\s*/\s*head>', re.DOTALL | re.UNICODE)
         xml_string = remove_heading.sub('', xml_string)
         abstract_string = utils.xml_to_plain_text(xml_string)

         ET.SubElement(result_root, 'abstract').text = abstract_string
      else:
         self.log('No abstract found')


      # CSX style xml document of header information
      return ExtractorResult(xml_result=result_root)

# Takes a TEI xml file of a document and tries to generate a plain text version of the document
# Right now it does this by simplying stripping out all xml tags
# This isn't very accurate or good
class TEItoPlainTextExtractor(interfaces.PlainTextExtractor):
   dependencies = frozenset([interfaces.FullTextTEIExtractor])

   def extract(self, data, dependency_results):
      xml_root = dependency_results[interfaces.FullTextTEIExtractor].xml_result
      body_node = xml_root.find('./text/body')

      if body_node is None:
         return RunnableError('Could not find body text in TEI xml file')

      xml_string = ET.tostring(body_node).decode('utf-8')

      plain_text = utils.xml_to_plain_text(xml_string)

      plain_text = plain_text.encode('utf-8')
      files = {'.txt': plain_text}

      return ExtractorResult(xml_result=None, files=files)



# Helper method, takes an affiliation node from Grobid TEI format and
# generates a plain text string representing the content
def _get_affiliation_str(affiliation_node):
   org_name_nodes = affiliation_node.findall('./orgName')

   # orders org_name nodes
   def comparator(n1, n2):
      # types of orgNames in order from least to most important this means
      # institution nodes should come first, then department, then laboratory, then any others
      types = ['laboratory', 'department', 'institution']
      score1 = (0 if not n1.get('type') in types else types.index(n1.get('type')))
      score2 = (0 if not n2.get('type') in types else types.index(n2.get('type')))
      score = -cmp(score1, score2)

      if score != 0: 
         return score
      # if same type or orgName nodes, then order by the key attribute
      else:
         return cmp(n1.get('key', ''), n2.get('key', ''))

   org_name_nodes.sort(comparator)
   return ', '.join([n.text for n in org_name_nodes])




