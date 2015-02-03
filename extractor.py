from extraction.core import ExtractionRunner
from extraction.runnables import Extractor, RunnableError
import extraction.utils as utils
import tempfile
import os
import glob
import subprocess32 as subprocess
import requests

# This Grobid Extractor uses the jar to process files
class GrobidExtractor(Extractor):
   def extract(self, data, dep_results):
      print len(data)
      temp_dir = tempfile.mkdtemp()
      temp_fd, temp_file_path = tempfile.mkstemp(suffix='.pdf', dir=temp_dir)
      temp_file = os.fdopen(temp_fd, 'w')
      temp_file.write(data)
      temp_file.close()

      grobid_core = os.path.expanduser('~/bin/grobid-core')
      grobid_home = os.path.expanduser('~/grobid/grobid-home/')
      results_dir = os.path.join(temp_dir, 'results')
      convert_jar = os.path.expanduser('~/bin/CreateCSXFiles.jar')

      os.mkdir(results_dir)

      try:
         status, out, err = utils.external_process('', ['java', '-Xmx2048m', '-jar', grobid_core, '-gH', grobid_home, '-dIn', temp_dir, '-dOut', results_dir, '-exe', 'processFullText'], timeout=60)
      except subprocess.TimeoutExpired:
         raise RunnableError('grobid timeout')

      results = glob.glob('{0}/*.xml'.format(results_dir))
      # remove xml header line from results
      result_str = '\n'.join(open(results[0], 'rb').readlines()[1:])
      return result_str


# This Grobid extractor is easier and cleaner!
# It uses the service variant of Grobid
class GrobidExtractor2(Extractor):
   def extract(self, data, dep_results):

      files = {'input': data}
      url = 'http://localhost:8080/processFulltextDocument'
      try:
         resp = requests.post(url, files=files)
      except requests.exceptions.RequestException as ex:
         raise RunnableError('Request to Grobid server failed')

      if resp.status_code != 200:
         raise RunnableError('Grobid returned status {0}'.format(resp.status_code))
      results = resp.text
      result_str = '\n'.join(results.split('\n')[1:])
      return result_str


if __name__ == '__main__':
   runner = ExtractionRunner()
   runner.add_runnable(GrobidExtractor2)

   file_path = os.path.expanduser('~/testpdfs/012.251.000.pdf')
   print runner.run_from_file(file_path, pretty=True)




