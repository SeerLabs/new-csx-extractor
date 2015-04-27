from os import system
from extraction.core import ExtractionRunner
from extraction.runnables import Extractor, RunnableError, Filter, ExtractorResult
import os
import sys
import csxextract.grobid as grobid
import csxextract.pdfbox as pdfbox
import csxextract.extractors as extractors
import csxextract.filters as filters
from datetime import datetime

runner = ExtractionRunner()
runner.enable_logging('~/logs/results', '~/logs/runnables')
runner.add_runnable(grobid.GrobidHeaderTEIExtractor)
runner.add_runnable(extractors.TEItoHeaderExtractor)
runner.add_runnable(pdfbox.PDFBoxPlainTextExtractor)
runner.add_runnable(extractors.ParsCitCitationExtractor)

#Takes about 54 seconds
NUM_FILES = 50 
MAX_PROCS = 1
file_paths = ['~/testpdfs/012.251.{0:0>3d}.pdf'.format(i) for i in range(0,NUM_FILES)]
output_dirs = ['~/testpdfs/results_batch'] * NUM_FILES
file_prefixes = [str(i) for i in range(0, NUM_FILES)]

# d1 = datetime.now()
# for i in range(0,NUM_FILES):
   # runner.run_from_file(file_paths[i], '~/testpdfs/results', file_prefix=str(i))
# dlta = datetime.now()-d1
# comb = dlta.seconds + dlta.microseconds/1E6
# print("Time: {0}".format(comb))

for i in range(MAX_PROCS,MAX_PROCS+1):
   d1 = datetime.now()
   runner.run_from_file_batch(file_paths, output_dirs, file_prefixes=file_prefixes, num_processes=i)
   dlta = datetime.now()-d1
   comb = dlta.seconds + dlta.microseconds/1E6
   print("Time proc={0}: {1}".format(i,comb))

