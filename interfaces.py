from extraction.runnables import Extractor, Filter

class PlainTextExtractor(Extractor):
   # Contract:
   # Extractors extending this extractor should:
   # return an ExtractorResult such that
   #    xml_result is a node named 'file' with content 'plain_text.txt'
   #    files is a dict with a key 'plain_text.txt' and a value which is the plain text of the pdf
   def extract(self, data, dependency_results):
      raise NotImplementedError('Extend me!')
