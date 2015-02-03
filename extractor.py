from extraction.core import ExtractionRunner
from extraction.runnables import Extractor, RunnableError, Filter
import extraction.utils as utils
import subprocess32 as subprocess
import os
import requests
import re

class GrobidExtractor(Extractor):
   def extract(self, data, dep_results):

      files = {'input': data}
      vars = {'consolidate': 1}
      url = 'http://localhost:8080/processFulltextDocument'
      try:
         resp = requests.post(url, files=files, data=vars)
      except requests.exceptions.RequestException as ex:
         raise RunnableError('Request to Grobid server failed')

      if resp.status_code != 200:
         raise RunnableError('Grobid returned status {0}'.format(resp.status_code))
      results = resp.text
      result_str = '\n'.join(results.split('\n')[1:])
      return result_str

class PlainTextExtractor(Extractor):
   @staticmethod
   def dependencies():
      return [GrobidExtractor]

   def extract(self, data, dep_results):
      xml_text = dep_results[GrobidExtractor]
      remove_tags = re.compile(r'\s*<.*?>', re.DOTALL | re.UNICODE)
      plain_text = remove_tags.sub('\n', xml_text)
      return plain_text


class AcademicPaperFilter(Filter):
   @staticmethod
   def dependencies():
      return [PlainTextExtractor]

   def filter(self, data, dep_results):
      plain_text = dep_results[PlainTextExtractor]
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
   runner.add_runnable(GrobidExtractor, include_in_output=False)
   runner.add_runnable(PlainTextExtractor)
   runner.add_runnable(AcademicPaperFilter)
   runner.add_runnable(TableExtractor)

   file_path = os.path.expanduser('~/testpdfs/012.251.000.pdf')
   print runner.run_from_file(file_path, pretty=True)




