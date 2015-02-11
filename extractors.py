from extraction.runnables import Extractor, RunnableError, ExtractorResult
import interfaces
import defusedxml.ElementTree as safeET
import xml.etree.ElementTree as ET
import xml.sax.saxutils as xmlutils
import requests
import re

class TEItoPlainTextExtractor(interfaces.PlainTextExtractor):
   @staticmethod
   def dependencies():
      return [interfaces.TEIExtractor]

   def extract(self, data, dependency_results):
      xml_root = dependency_results[interfaces.TEIExtractor].xml_result
      xml_string = ET.tostring(xml_root).decode('utf-8')

      remove_tags = re.compile(r'\s*<.*?>', re.DOTALL | re.UNICODE)
      plain_text = remove_tags.sub('\n', xml_string)
      # run this twice for weird situations where things are double escaped
      plain_text = xmlutils.unescape(plain_text, {'&apos;': "'", '&quot;': '"'})
      plain_text = xmlutils.unescape(plain_text, {'&apos;': "'", '&quot;': '"'})

      # create xml result file that just points towards file of plain text
      root=ET.Element('file')
      root.text = 'plain_text.txt'

      plain_text = plain_text.encode('utf-8')
      files = {'plain_text.txt': plain_text}

      return ExtractorResult(xml_result=root, files=files)
