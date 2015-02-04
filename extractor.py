from extraction.core import ExtractionRunner
from extraction.runnables import Extractor, RunnableError, Filter, ExtractorResult
import defusedxml.ElementTree as safeET
import xml.etree.ElementTree as ET
import extraction.utils as utils
import subprocess32 as subprocess
import os
import requests
import re

class GrobidExtractor(Extractor):
   def extract(self, data, dep_results):

      files = {'input': data}
      vars = {}
      url = 'http://localhost:8080/processFulltextDocument'
      try:
         resp = requests.post(url, files=files, data=vars)
      except requests.exceptions.RequestException as ex:
         raise RunnableError('Request to Grobid server failed')

      if resp.status_code != 200:
         raise RunnableError('Grobid returned status {0}'.format(resp.status_code))
      xml_snippet = safeET.fromstring(resp.text.encode('utf-8'))
      return ExtractorResult(xml_snippet)

class PlainTextExtractor(Extractor):
   @staticmethod
   def dependencies():
      return [GrobidExtractor]

   def extract(self, data, dep_results):
      xml_doc = dep_results[GrobidExtractor].xml_result
      xml_text = ET.tostring(xml_doc)
      remove_tags = re.compile(r'\s*<.*?>', re.DOTALL | re.UNICODE)
      plain_text = remove_tags.sub('\n', xml_text)

      root=ET.Element('file')
      root.text = 'plain_text.txt'

      return ExtractorResult(xml_result = root, files = {'plain_text.txt': plain_text})


class AcademicPaperFilter(Filter):
   @staticmethod
   def dependencies():
      return [PlainTextExtractor]

   def filter(self, data, dep_results):
      plain_text = dep_results[PlainTextExtractor].files['plain_text.txt']
      return  ('REFERENCES' in plain_text or
               'References' in plain_text or
               'Bibliography' in plain_text or
               'BIBLIOGRAPHY' in plain_text
              )

class TableExtractor(Extractor):
   @staticmethod
   def dependencies():
      return [AcademicPaperFilter]

   def extract(self, data, dep_results):
      return 'TODO'


if __name__ == '__main__':
   runner = ExtractionRunner()
   runner.add_runnable(GrobidExtractor )
   runner.add_runnable(PlainTextExtractor)
   runner.add_runnable(AcademicPaperFilter)
   runner.add_runnable(TableExtractor)

   file_path = os.path.expanduser('~/testpdfs/012.251.000.pdf')
   runner.run_from_file(file_path)




