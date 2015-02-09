from extraction.core import ExtractionRunner
from extraction.runnables import Extractor, RunnableError, Filter, ExtractorResult
import os
import sys
import grobid
import pdfbox

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

if __name__ == '__main__':
   # PlainTextExtractor = grobid.PlainTextExtractor
   PlainTextExtractor = pdfbox.PlainTextExtractor

   runner = ExtractionRunner()
   runner.add_runnable(PlainTextExtractor)
   runner.add_runnable(AcademicPaperFilter)

   argc = len(sys.argv)
   if argc == 2:
      runner.run_from_file(sys.argv[1])
   elif argc == 3:
      runner.run_from_file(sys.argv[1], output_dir = sys.argv[2])
   else:
      print("USAGE: python {0} path_to_pdf [output_directory]")


