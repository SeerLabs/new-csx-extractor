Repo for extraction code for CiteSeerX

Usage:

    python run_extraction.py /path/to/file.pdf [path/to/output/dir]

If a path to an output directory is not supplied, results will be put in the same directory
as the pdf file.

Dependencies:
   * extraction framework library on python path (run `python setup.py install --user` from its root directory)
   * defusedxml python library (run `pip install defusedxml --user` to install)
   * requests python library (run `pip install requests --user` to install)
   * Grobid server running (run `mvn jetty:run-war` from `grobid-service` directory if not already running)
     URL for Grobid can be configured in grobid.py
   * PDFBox jar in ~/bin (location can be configured in pdfbox.py)
