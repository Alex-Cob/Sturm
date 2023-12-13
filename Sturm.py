"""
:todo:
    1. To have a zip decompressor for the excel invoices in XLReader.py.
    2. In PDFProcessor.py, will need to allow the invoices from XLReader.py to populate saved StructDeclarations.
    3. To have a zip compressor in the end to ease process.
    4. To dump all the commodities & HS Code in a single gsheet where it will retrieve them when encountered.
"""

import Misc
import XLReader
import PDFProcessor

if __name__ == '__main__':
    pdf = PDFProcessor.PDFProcessor()
    pdf.getPdfFile()
    pdf.transposeAllPages()
