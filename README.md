# New CiteSeerX Extraction Implementation #

## Usage ##

    python run_extraction.py /path/to/file.pdf [path/to/output/dir]

If a path to an output directory is not supplied, results will be put in the same directory
as the pdf file.

## Dependencies/Prerequisites ##

#### Python Libs ####
   * [extraction framework python library][1] (on python path (run `python setup.py install --user` from its root directory)
   * [defusedxml python library][2] (run `pip install defusedxml --user` to install)
   * [requests python library][3] (run `pip install requests --user` to install)
 
#### Grobid ####
[Grobid][4] is used to extract header information from the PDF files. Grobid should be running as a service somwhere. (Run `mvn jetty:run-war` from `grobid-service` directory if not already running. See Grobid's Github project for more complete [installation instructions][5].) The URL for Grobid can be configured in `csxextract/config.py`.

#### PDFBox ####
[PDFBox][6] is used to get a plain text representation of the PDF files. The PDFBox jar needs to be on the machine somewhere. The default expected location is `~/bin` but this can be configured in `csxextract/config.py`.

#### ParsCit ####
[ParsCit][7] is used to extract citation information from the PDF files. The path to it's `citeExtract.pl` script should be configured in `csxextract/config.py`. The default expected location is `~/bin/pars_cit/bin/citeExtract.pl`.

Installation of ParsCit can be tricky. See its [INSTALL doc][8] for full instructions details. Also important is the [Troubleshooting page][9] which has answers for common problems. 

A message like "Can't locate XML/Twig.pm in @INC (@INC contains: ...)" means that a Perl library is missing. Missing libraries can be installed with cpan. 

Also note the question "When running citeExtract.pl I get some errors complaining about the wrong ELF class of the binaries. How can I fix this?" After Step 1 in the install instructions, the following commands should be run:

```shell
$ cp -Rf * ../../.libs 
$ cp crf_learn ../../.libs/lt-crf_learn
$ cp crf_test ../../.libs/lt-crf_test
```

Finally, the step marked as "optional" in the install instructions might actually be necessary when installing ParsCit.

[1]: https://github.com/SeerLabs/extractor-framework
[2]: https://pypi.python.org/pypi/defusedxml
[3]: http://docs.python-requests.org/en/latest/
[4]: https://github.com/kermitt2/grobid
[5]: https://github.com/kermitt2/grobid/wiki/Grobid-service-quick-start
[6]: http://pdfbox.apache.org/
[7]: https://github.com/knmnyn/ParsCit
[8]: https://github.com/knmnyn/ParsCit/blob/master/INSTALL
[9]: http://wing.comp.nus.edu.sg/parsCit/#t

