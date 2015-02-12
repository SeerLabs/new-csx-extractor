# New CiteSeerX Extraction Implementation #

Usage:

    python run_extraction.py /path/to/file.pdf [path/to/output/dir]

If a path to an output directory is not supplied, results will be put in the same directory
as the pdf file.

## Dependencies/Prerequisites ##
   * [extraction framework python library][1] (on python path (run `python setup.py install --user` from its root directory)
   * [defusedxml python library][2] (run `pip install defusedxml --user` to install)
   * [requests python library][3] (run `pip install requests --user` to install)
   * Grobid server running (run `mvn jetty:run-war` from `grobid-service` directory if not already running)
     URL for Grobid can be configured in `grobid.py`
   * PDFBox jar in ~/bin (location of jar can be configured in `pdfbox.py`)
[1]: https://github.com/SeerLabs/extractor-framework
[2]: https://pypi.python.org/pypi/defusedxml
[3]: http://docs.python-requests.org/en/latest/

