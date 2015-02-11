from extraction.runnables import Filter
import interfaces

class AcademicPaperFilter(Filter):
   @staticmethod
   def dependencies():
      return [interfaces.PlainTextExtractor]

   def filter(self, data, dep_results):
      plain_text = dep_results[interfaces.PlainTextExtractor].files['plain_text.txt'].decode('utf-8')
      return  ('REFERENCES' in plain_text or
               'References' in plain_text or
               'Bibliography' in plain_text or
               'BIBLIOGRAPHY' in plain_text
              )


