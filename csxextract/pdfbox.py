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


# Returns a plain text version of a PDF file
class PDFBoxPlainTextExtractor(interfaces.PlainTextExtractor):
   result_file_name = '.text_extraction'
   def extract(self, data, dep_results):
      # Write the pdf data to a temporary location so PDFBox can process it
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

      # We can use result from PDFBox directly, no manipulation needed
      pdf_plain_text = stdout
      files = {'.txt': pdf_plain_text}

      return ExtractorResult(xml_result=None, files=files)
