from extraction.runnables import Extractor, RunnableError, ExtractorResult
import csxextract.interfaces as interfaces
import csxextract.config as config
import defusedxml.ElementTree as safeET
import xml.etree.ElementTree as ET
import xml.sax.saxutils as xmlutils
import requests
import re


class GrobidTEIExtractor(interfaces.FullTextTEIExtractor):
   result_file_name = '.tei'

   def extract(self, data, dep_results):
      url = '{0}/processFulltextDocument'.format(config.GROBID_HOST)
      files = {'input': data}
      vars = {}

      try:
         resp = requests.post(url, files=files, data=vars)
      except requests.exceptions.RequestException as ex:
         raise RunnableError('Request to Grobid server failed')

      if resp.status_code != 200:
         raise RunnableError('Grobid returned status {0} instead of 200\nPossible Error:\n{1}'.format(resp.status_code, resp.text))

      xml_text = resp.content
      # remove namespace info from xml string
      # this is hacky but makes parsing it much much nicer down the road
      remove_xmlns = re.compile(r'\sxmlns[^"]+"[^"]+"')
      xml_text = remove_xmlns.sub('', xml_text)

      xml = safeET.fromstring(xml_text)

      # grobid returns TEI xml file
      return ExtractorResult(xml_result=xml)
