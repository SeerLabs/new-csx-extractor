from extraction.runnables import Extractor, RunnableError, ExtractorResult
import defusedxml.ElementTree as safeET
import xml.etree.ElementTree as ET
import requests
import re

GROBID_HOST = 'http://localhost:8080'

class PlainTextExtractor(Extractor):
   def extract(self, data, dep_results):

      url = '{0}/processFulltextDocument'.format(GROBID_HOST)
      files = {'input': data}
      vars = {}

      try:
         resp = requests.post(url, files=files, data=vars)
      except requests.exceptions.RequestException as ex:
         raise RunnableError('Request to Grobid server failed')

      if resp.status_code != 200:
         raise RunnableError('Grobid returned status {0} instead of 200\nPossible Error:\n{1}'.format(resp.status_code, resp.text))

      xml_text = resp.text.encode('utf-8')

      # grobid returns TEI xml file
      # we will 'convert' it to plain text be removing all xml tags
      remove_tags = re.compile(r'\s*<.*?>', re.DOTALL | re.UNICODE)
      plain_text = remove_tags.sub('\n', xml_text)

      # create xml result file that just points towards file of plain text
      root=ET.Element('file')
      root.text = 'plain_text.txt'

      files = {'plain_text.txt': plain_text}

      return ExtractorResult(xml_result=root, files=files)

