"""
:todo:
    1. In PDFProcessor.py, will need to allow the invoices from XLReader.py to populate saved StructDeclarations.
    2. To have a zip compressor in the end to ease process.
    3. To dump all the commodities, NICs & HS Code in a single gsheet where it will retrieve them when encountered.
    4. Check if declared value is less than 1k using rates.
    5. To convert Excel files to PDF: https://stackoverflow.com/questions/52326782/python-converting-xlsx-to-pdf
    6. To have the new entries (HS Codes) filtered before appending to GSheet.
    7. In Converger, to cater for passport rather than NIC cards.
    8. To fix bug where the excel quit closes the whole app + what is the worked and attachments are opened.
"""
import Converger
import GParser
import XLReader
import PDFProcessor
import CSVWriter
from Misc import *


def main():
    xl = XLReader.InvoiceReader()
    pdf = PDFProcessor.PDFProcessor()
    comm = GParser.HSParser()
    ids = GParser.IDParser()
    converger = Converger.Converger(xl, pdf, comm, ids)
    csv = CSVWriter.CSVWriter(os.path.join(os.environ["USERPROFILE"], "Downloads"))
    log("Filling CSV and transposing PDFs...")
    y = 1
    for elem in converger.workbench:
        log(f"Reading: {y}. {elem.awb}")
        csv.enterRecord(elem, comm.knownCommodities)
        pdf._transposePage((elem, pdf.pdfPages[elem.awb][1]))
        y += 1
    log("Now Renaming and converting excels")
    converger.renameExcelFiles(xl.foldername[:-4], os.path.join(os.environ["USERPROFILE"], "Downloads/" + pdf.uuid))
    try:
        converger.zipTogether(os.path.join(os.environ["USERPROFILE"], "Downloads/" + pdf.uuid))
    except Exception:
        print(

        )
    log("Now filling in the narrator...")
    finalLog = XLReader.EndNarrator()
    finalLog.transposeDeductions(converger.CustNotDeduced, converger.unpaired, csv.NewHSItems)
    log("Done!")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log("Error occured:" + str(e))
    os.system("PAUSE")
