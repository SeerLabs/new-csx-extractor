from extraction.runnables import Extractor, RunnableError, ExtractorResult
import interfaces
import utils
import defusedxml.ElementTree as safeET
import xml.etree.ElementTree as ET
import requests
import re


class TEItoPlainTextExtractor(interfaces.PlainTextExtractor):
   @staticmethod
   def dependencies():
      return [interfaces.FullTextTEIExtractor]

   def extract(self, data, dependency_results):
      xml_root = dependency_results[interfaces.FullTextTEIExtractor].xml_result
      xml_string = ET.tostring(xml_root).decode('utf-8')

      plain_text = utils.xml_to_plain_text(xml_string)

      # create xml result file that just points towards file of plain text
      root=ET.Element('file')
      root.text = 'plain_text.txt'

      plain_text = plain_text.encode('utf-8')
      files = {'plain_text.txt': plain_text}

      return ExtractorResult(xml_result=root, files=files)

class TEItoHeaderExtractor(interfaces.CSXHeaderExtractor):
   @staticmethod
   def dependencies():
      return [interfaces.FullTextTEIExtractor]

   def extract(self, data, dep_results):
      tei_root = dep_results[interfaces.FullTextTEIExtractor].xml_result
      result_root = ET.Element('algorithm', {'name': 'Grobid Header Extraction', 'version': '0.1'})

      # Retreive title from TEI doc
      title = tei_root.find('./teiHeader//titleStmt/title')
      if title is not None:
         ET.SubElement(result_root, 'title').text = title.text
      else:
         raise RunnableError('No title found in TEI document')

      # Retreive author names from TEI doc
      authors = tei_root.findall('./teiHeader//biblStruct//author')
      authors_node = ET.SubElement(result_root, 'authors')
      if authors is not None and len(authors):
         for author in authors:
            author_node = ET.SubElement(authors_node, 'author')
            name_tags = []
            name_tags.extend(author.findall(".//forename"))
            name_tags.append( author.find('.//surname') )

            name_parts = [name.text for name in name_tags if name is not None]
            name = ' '.join(name_parts)
            ET.SubElement(author_node, 'name').text = name
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
         abstract_node = abstracts[0]
         xml_string = ET.tostring(abstract_node)
         remove_heading = re.compile(r'\s*<head.*?>.*?<\s*/\s*head>', re.DOTALL | re.UNICODE)
         xml_string = remove_heading.sub('', xml_string)
         abstract_string = utils.xml_to_plain_text(xml_string)

         ET.SubElement(result_root, 'abstract').text = abstract_string
      else:
         self.log('No abstract found')

      # CSX style xml document of header information
      return ExtractorResult(xml_result=result_root)


