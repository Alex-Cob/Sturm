import datetime as dt
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
        self.workbench = list()
        self._getMatchingXLandPDF()
        self.layingBricks()

    def _getMatchingXLandPDF(self) -> None:
        """
        Catching all the matching waybills to work with and all the mismatched will be communicated.
        :return: None
        """
        for x in self.xl.data:
            if x in self.pdf.pdfPages.keys():       # file matches
                self.matchingWaybills.append(x)
            else:
                self.unfound.append(x)              # file not founds

    def layingBricks(self):
        """
        Takes the output from the different sources and
        :return:
        """
        for matchingwb in self.matchingWaybills:
            currStruct = self.pdf.pdfPages[matchingwb][0]           # Extract the construct
            currStruct.cneeTel = self.xl.data[matchingwb][0][1]     # Consignee telephone
            currStruct.itemdetails = self.xl.data[matchingwb][1]    # appending list of items to struct
            candidates = self.ids.guessCustomer(currStruct.cnee)

            if len(candidates) == 1:
                # if customer found, proceed...
                pass
            elif len(candidates) == 0:
                clist = [currStruct.cnee, currStruct.cneeEmail, currStruct.cneeTel, "A1111000000000",
                         "", "", "", ""]
                candidates = list()
                candidates.append(clist.copy())     # appending to create a list of list
            else:
                k = len(candidates)
                identical = True
                for j in range(k):
                    if candidates[0][3].strip() != candidates[j][3].strip():    # checking if NIC match.
                        identical = False
                        break
                if not identical:
                    candidates[0][3] = "A1111000000000"     # putting a placeholder to the NIC.

            if candidates[0][3] not in ("", None):
                currStruct.NIC = candidates[0][3]
                try:
                    currStruct.DOB = str(dt.datetime.strptime(candidates[0][3][1:7], "%d%m%y").strftime("%d-%m-%Y"))
                except Exception as e:
                    log(f"{currStruct.awb}: couldn't strip DOB from NIC")
            elif candidates[0][4] not in ("", None):
                currStruct.passport = candidates[0][4]
                currStruct.DOB = candidates[0][5]

            self.workbench.append(currStruct)  # saving the struct to the 'workbench'
