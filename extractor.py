from extraction.core import ExtractionRunner
from extraction.runnables import Extractor, RunnableError, Filter
import extraction.utils as utils
import tempfile
import os
import glob
import subprocess32 as subprocess
import requests

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

class AcademicPaperFilter(Filter):
   @staticmethod
   def dependencies():
      return [GrobidExtractor]

   def filter(self, data, dep_results):
      plain_text = dep_results[GrobidExtractor]
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
   runner.add_runnable(GrobidExtractor)
   runner.add_runnable(AcademicPaperFilter)
   runner.add_runnable(TableExtractor)

   file_path = os.path.expanduser('~/testpdfs/012.251.000.pdf')
   print runner.run_from_file(file_path, pretty=True)




