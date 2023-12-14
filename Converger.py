from Misc import *
import XLReader
import PDFProcessor
import GParser


class Converger:

    def __init__(self, xl_: XLReader.InvoiceReader, pdf_: PDFProcessor.PDFProcessor,
                 comm_: GParser.HSParser, ids_: GParser.IDParser):
        self.xl = xl_
        self.pdf = pdf_
        self.comm = comm_
        self.ids = ids_
        self.matchingWaybills = list()
        self.unfound = list()
        self._getMatchingXLandPDF()

    def _getMatchingXLandPDF(self) -> None:
        """
        Catching all the matching waybills to work with and all the mismatched will be communicated.
        :return: None
        """
        for x in self.xl.data:
            if x in self.pdf.pdfPages.keys():
                self.matchingWaybills.append(x)
            else:
                self.unfound.append(x)
                print(x)

