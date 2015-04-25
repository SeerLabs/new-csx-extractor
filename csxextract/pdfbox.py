from extraction.runnables import Extractor, RunnableError, ExtractorResult
import csxextract.interfaces as interfaces
import csxextract.config as config
import extraction.utils as utils
import subprocess32 as subprocess
import defusedxml.ElementTree as safeET
import xml.etree.ElementTree as ET
import os
import tempfile
import requests
import re


class PDFBoxPlainTextExtractor(interfaces.PlainTextExtractor):

   def extract(self, data, dep_results):
      file_path = utils.temp_file(data, suffix='.pdf')
      
      try:
         status, stdout, stderr = utils.external_process(['java', '-jar', config.PDF_BOX_JAR, 'ExtractText', '-console', '-encoding', 'UTF-8', file_path],
               timeout=30)
      except subprocess.TimeoutExpired as te:
         raise RunnableError('PDFBox timed out while processing document')
      finally:
         os.remove(file_path)

      if status != 0:
         raise RunnableError('PDFBox returned error status code {0}.\nPossible error:\n{1}'.format(status, stderr))

      plain_text = stdout

      # create xml result file that just points towards the file with plain text results
      files = {'.txt': stdout}

      return ExtractorResult(xml_result=None, files=files)
