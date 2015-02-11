from extraction.core import ExtractionRunner
from extraction.runnables import Extractor, RunnableError, Filter, ExtractorResult
import os
import sys
import grobid
import pdfbox
import extractors
import filters

def get_extraction_runner():

   runner = ExtractionRunner()

   # Option 1
   runner.add_runnable(grobid.GrobidTEIExtractor)
   runner.add_runnable(extractors.TEItoPlainTextExtractor)
   # OR
   # Option 2
   # runner.add_runnable(pdfbox.PDFBoxPlainTextExtractor)

   runner.add_runnable(filters.AcademicPaperFilter)

   return runner


if __name__ == '__main__':
   runner = get_extraction_runner()

   argc = len(sys.argv)
   if argc == 2:
      runner.run_from_file(sys.argv[1])
   elif argc == 3:
      runner.run_from_file(sys.argv[1], output_dir = sys.argv[2])
   else:
      print("USAGE: python {0} path_to_pdf [output_directory]")


