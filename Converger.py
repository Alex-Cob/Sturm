import datetime as dt
import os
import zipfile
import win32com.client

from Misc import *
import XLReader
import PDFProcessor
import GParser


class Converger:
    IDPLACEHOLDER = "A1111000000000"

    def __init__(self, xl_: XLReader.InvoiceReader, pdf_: PDFProcessor.PDFProcessor,
                 comm_: GParser.HSParser, ids_: GParser.IDParser):
        self.xl = xl_
        self.pdf = pdf_
        self.comm = comm_
        self.ids = ids_
        self.matchingWaybills = list()
        self.unpaired = list()              # Excels without an equivalent PDF.
        self.CustNotDeduced = list()
        self.workbench = list()
        self.ptrApp = win32com.client.Dispatch("Excel.Application")
        self.ptrApp.Visible = False
        log("Filtering mismatch first...")
        self._getMatchingXLandPDF()
        log("Laying bricks on the workbench...")
        self.layingBricks()
        log("Ready....")

    def __del__(self):
        try:
            self.ptrApp.Quit()
        except Exception as e:
            log(repr(e))

    def _getMatchingXLandPDF(self) -> None:
        """
        Catching all the matching waybills to work with and all the mismatched will be communicated.
        :return: None
        """
        for x in self.xl.data:
            if x in self.pdf.pdfPages.keys():       # file matches
                self.matchingWaybills.append(x)
            else:
                self.unpaired.append(x)              # file not founds

    def layingBricks(self):
        """
        Takes the output from the different sources and converge on a single workbench (StructDeclaration)
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
                clist = [currStruct.cnee, currStruct.cneeEmail, currStruct.cneeTel, Converger.IDPLACEHOLDER,
                         "", "", "", ""]
                candidates = list()
                candidates.append(clist.copy())     # appending to create a list of list
            else:
                k = len(candidates)
                identical = True
                for j in range(k):
                    if candidates[0][IndexIDRecord.NIC].strip() != candidates[j][3].strip():    # checking if NIC match.
                        identical = False
                        break
                if not identical:
                    candidates[0][IndexIDRecord.NIC] = Converger.IDPLACEHOLDER     # putting a placeholder to the NIC.

            if candidates[0][IndexIDRecord.NIC] not in ("", None):
                currStruct.NIC = candidates[0][IndexIDRecord.NIC]
                try:
                    currStruct.DOB = str(dt.datetime.strptime(candidates[0][IndexIDRecord.NIC][1:7], "%d%m%y").strftime("%d-%m-%Y"))
                except Exception as e:
                    currStruct.DOB = "01-01-2000"
                    log(f"{currStruct.awb}: couldn't strip DOB from NIC")
            elif candidates[0][IndexIDRecord.passport] not in ("", None):
                currStruct.passport = candidates[0][IndexIDRecord.passport]
                currStruct.DOB = candidates[0][IndexIDRecord.DOB]

            if currStruct.NIC == Converger.IDPLACEHOLDER:
                self.CustNotDeduced.append(currStruct.cnee)

            self.workbench.append(currStruct)  # saving the struct to the 'workbench'

    def renameExcelFiles(self, originPath, destPath):
        for path, dirs, files in os.walk(originPath):
            for struct in self.workbench:
                for file in files:
                    if file.find(struct.awb) > -1 and file.find("_SalesInvoice") == -1:     # meaning not the default ones
                        originFile = os.path.join(path, file)
                        destFile = os.path.join(destPath, struct.reportNo + "_" + file)
                        os.rename(originFile, destFile)
                        try:
                            self.convertExcelToPDF(destFile, destFile[:-5] + ".pdf")
                        except Exception as e:
                            print(repr(e), str(e))

    def convertExcelToPDF(self, WB_PATH, PATH_TO_PDF):
        # Path to original excel file
        try:
            log("Excel loaded...")
            # Open
            wbk = self.ptrApp.Workbooks.Open(WB_PATH)
            # Specify the sheet you want to save by index. 1 is the first (leftmost) sheet.
            sh = wbk.WorkSheets(1)
            # Save
            sh.PageSetup.Zoom = False
            sh.PageSetup.FitToPagesTall = False
            sh.PageSetup.FitToPagesWide = 1
            sh.ExportAsFixedFormat(0, PATH_TO_PDF)
        except Exception as e:
            print('failed.', repr(e), str(e))
        else:
            print('Succeeded.')
        finally:
            wbk.Close()

    def zipTogether(self, originFolder: str):
        compression = zipfile.ZIP_DEFLATED
        count = 0
        print("Zipping in progress...")
        for path, dirs, files in os.walk(originFolder):
            with zipfile.ZipFile(os.path.join(os.environ["USERPROFILE"], "Downloads/attachments.zip"), mode="w") as zf:
                for file in files:
                    if file.lower().find(".pdf") > -1:
                        zf.write(os.path.join(path, file),
                                 arcname=file,
                                 compress_type=compression)
                        count += 1
        print(count, "files were zipped")
