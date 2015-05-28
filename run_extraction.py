from extraction.core import ExtractionRunner
from extraction.runnables import Extractor, RunnableError, Filter, ExtractorResult
import os
import sys
import csxextract.grobid as grobid
import csxextract.pdfbox as pdfbox
import csxextract.extractors as extractors
import csxextract.filters as filters

def get_extraction_runner():

   runner = ExtractionRunner()
   runner.enable_logging('~/logs/results', '~/logs/runnables')

   # Option 1
   runner.add_runnable(pdfbox.PDFBoxPlainTextExtractor)
   runner.add_runnable(filters.AcademicPaperFilter)
   runner.add_runnable(grobid.GrobidHeaderTEIExtractor)
   runner.add_runnable(extractors.TEItoHeaderExtractor)
   runner.add_runnable(extractors.ParsCitCitationExtractor)
   # OR
   # Option 2
   # But the plain text isn't that good this way
   # runner.add_runnable(extractors.TEItoPlainTextExtractor)

   # runner.add_runnable(filters.AcademicPaperFilter)

   return runner


if __name__ == '__main__':
   runner = get_extraction_runner()

   argc = len(sys.argv)
   if argc == 2:
      file_name = os.path.splitext(os.path.basename(sys.argv[1]))[0]
      runner.run_from_file(sys.argv[1], file_prefix=file_name)
   elif argc == 3:
      file_name = os.path.splitext(os.path.basename(sys.argv[1]))[0]
      runner.run_from_file(sys.argv[1], output_dir = sys.argv[2], file_prefix=file_name)
   else:
      print("USAGE: python {0} path_to_pdf [output_directory]".format(sys.argv[0]))


