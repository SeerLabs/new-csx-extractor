import web
import tempfile
import os
import subprocess
import shutil
from extraction.core import ExtractionRunner
from extraction.runnables import Extractor, RunnableError, Filter, ExtractorResult
import extractor.csxextract.extractors.grobid as grobid
import extractor.csxextract.extractors.pdfbox as pdfbox
import extractor.csxextract.extractors.tei as tei
import extractor.csxextract.extractors.parscit as parscit
import extractor.csxextract.extractors.figures as figures
import extractor.csxextract.extractors.algorithms as algorithms
import extractor.csxextract.filters as filters

ROOT_FOLDER="../" # there must be a trailing /

class Extraction:
	"""
	This class does the actual extraction by calling the relevant extraction methods
	Errors are caught in the calling class
	"""

	def __init__(self, util):
        self.utilities = util

	def extractHeaders(self,path):
		"""extract headers from pdf file"""
		runner = get_extraction_runner()
		runner.add_runnable(pdfbox.PDFBoxPlainTextExtractor)
   		runner.add_runnable(filters.AcademicPaperFilter)
  		runner.add_runnable(grobid.GrobidHeaderTEIExtractor)
  		runnable = grobid.GrobidHeaderTEIExtractor

  		results = runner.run_from_file_batch_no_output([path])
  		resultstxt = self.utilities.resultsToString(results, runnable)
  		web.debug(resultstxt)
  		return resultstxt

	def extractCitations(self,path):
		"""extract citations from pdf file"""
		runner = get_extraction_runner()
		runner.add_runnable(pdfbox.PDFBoxPlainTextExtractor)
   		runner.add_runnable(filters.AcademicPaperFilter)
  		runner.add_runnable(parscit.ParsCitCitationExtractor)
  		runnable = parscit.ParsCitCitationExtractor

  		results = runner.run_from_file_batch_no_output([path])
  		resultstxt = self.utilities.resultsToString(results, runnable)
  		web.debug(resultstxt)
  		return resultstxt

	def extractText(self, path):
		"""extract text from pdf file"""
		runner = get_extraction_runner()
		runner.add_runnable(pdfbox.PDFBoxPlainTextExtractor)
  		runnable = pdfbox.PDFBoxPlainTextExtractor

  		results = runner.run_from_file_batch_no_output([path])
  		resultstxt = self.utilities.resultsToString(results, runnable)
  		web.debug(resultstxt)
  		return resultstxt

	def get_extraction_runner(self):
		runner = ExtractionRunner()
		runner.enable_logging('~/logs/service/results', '~/logs/service/runnables')

		return runner
