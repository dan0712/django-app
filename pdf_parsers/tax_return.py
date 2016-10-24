#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
required packages to install
linux: apt-get install tesseract
python3: pip-install pyPdf2
"""

import argparse
from PyPDF2 import PdfFileReader
import os
import shutil
import sys
import json
import subprocess
import logging

logger = logging.getLogger('pdf_parsers.tax_return')


def get_pdf_content_lines(pdf_file_path):
    with open(pdf_file_path, 'rb') as f:
        pdf_reader = PdfFileReader(f)
        for page in pdf_reader.pages:
            for line in page.extractText().splitlines():
                yield line


# for each item to extract its string, the value is found between
# the pairs in the list e.g. SSN is found between "SSN:", "SPOUSE SSN:"
keywords = {
    "SSN": ["SSN:", "SPOUSE SSN:"],
    "SPOUSE SSN": ["SPOUSE SSN:", "NAME(S)"],
    "NAME": ["RETURN:", "ADDRESS:"],
    "SPOUSE NAME": ["RETURN:", "ADDRESS:"],
    "ADDRESS": ["ADDRESS:", "FILING STATUS:"],
    "FILING STATUS": ["FILING STATUS:", "FORM NUMBER:"],
    "TOTAL INCOME": ["TOTAL INCOME:", "TOTAL INCOME PER COMPUTER:"]
}

output = {
    "sections": [
        {
            "name": "Introduction",
            "fields": {
                "SSN": "",
                "SPOUSE SSN": "",
                "NAME": "",
                "SPOUSE NAME": "",
                "ADDRESS": "",
                "FILING STATUS": ""
            }
        },
        {
            "name": "Income",
            "fields": {
                "TOTAL INCOME": "",

            }
        }
    ]
}


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def parse_item(key, s):
    sub_str = keywords[key]
    start = sub_str[0]
    end = sub_str[1]
    result = find_between(s, start, end)
    if key == "NAME" and "&" in result:
        result = result.split("&")[0]
    if key == 'SPOUSE NAME':
        if "&" in result:
            result = result.split("&")[1]
            if "\n" in result:
                for i in result.splitlines()[1:]:
                    if i and "\n" not in i:
                        output["sections"][0]["fields"]["ADDRESS"] = i
                        break

                result = result.splitlines()[0]
        else:
            result = ''

    return result.lstrip().rstrip().lstrip('.').rstrip('.').rstrip('\n')


def parse_text(string):
    i = 0
    for section in output["sections"]:
        for k, v in section["fields"].items():
            res = parse_item(k, string)
            if output["sections"][i]["fields"][k] == "":
                output["sections"][i]["fields"][k] = res
            else:
                if k == "ADDRESS":
                    output["sections"][i]["fields"][k] += " " + res
        i += 1
    return output


def parse_vector_pdf(fl):
    res = get_pdf_content_lines(fl)
    return parse_text(', '.join(res))


def parse_scanned_pdf(fl):
    tmp_pdfs = "temp"
    if not os.path.exists(tmp_pdfs):
        os.makedirs(tmp_pdfs)

    os.system("convert -density 300 -alpha Off {0} {1}/img.tiff".format(fl, tmp_pdfs))
    os.system("tesseract {0}/img.tiff {0}/out".format(tmp_pdfs))
    cmd = "sed -i -e 's/—/-/g' {0}/out.txt".format(tmp_pdfs)
    os.system(cmd)
    with open("{0}/out.txt".format(tmp_pdfs), 'r') as f:
        txt = f.read()

    shutil.rmtree(tmp_pdfs)
    txt = ''.join(txt)
    return parse_text(txt)


def parse_pdf(filename):
    try:
        # check if pdf is searchable, pdffonts lists fonts used in pdf, if scanned (image), list is empty
        cmd_out = subprocess.getstatusoutput("pdffonts {} | wc -l".format(filename))
        if int(cmd_out[1]) > 2:
            result = parse_vector_pdf(filename)
        else:
            result = parse_scanned_pdf(filename)

        logger.info('Tax Return PDF parsed OK')
        return result
    except Exception as e:
        logger.error(e)
        return


def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', '--file', type=str, help='Input pdf file', required=True)

        args = parser.parse_args()

        # check if pdf is searchable, pdffonts lists fonts used in pdf, if scanned (image), list is empty
        cmd_out = subprocess.getstatusoutput("pdffonts {} | wc -l".format(args.file))
        if int(cmd_out[1]) > 2:
            result = parse_vector_pdf(args.file)
        else:
            result = parse_scanned_pdf(args.file)

        print(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')))
        return result
    except KeyboardInterrupt:
        print('Keyboard interrupt!')
        return 0
    except Exception as e:
        print(e)
        raise e


if __name__ == "__main__":
    sys.exit(main())
