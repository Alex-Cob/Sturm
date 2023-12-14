
import uuid

import PyPDF2
from tkinter.filedialog import askopenfilename

from Misc import *


# noinspection PyMethodMayBeStatic
class PDFProcessor:

    def __init__(self):
        self.pdfPages = dict()      # contains tuple of textual struct and binary content, tuple[StructDeclaration, io]
        self.currentPDF = None
        self.uuid = uuid.uuid4().hex
        self.getPdfFile()

    def __del__(self):
        pass

    def getPdfFile(self) -> None:
        """
        Prompts user to select the NOA file.
        :return: None
        """
        filepath = askopenfilename(defaultextension=".pdf", title="Select the NOA file")
        self.currentPDF = None      # resetting attribute before proceeding.

        if filepath == "":
            log("No file has been selected...", LogLevel.WARNING)
            return
        self.currentPDF = PyPDF2.PdfReader(filepath)        # assigning the attribute to the file object
        self._parseCurrentNoaPdf()

    def _parseCurrentNoaPdf(self) -> None:
        """
        Takes pages from a downloaded NOA PDF file and memorizes them as a struct and binary form in self.pdfPages
        :return: None
        """
        if self.currentPDF is None:
            log("Need to select a PDF first...", LogLevel.WARNING)
            return

        for pg in self.currentPDF.pages:    # iterate through pages and get content
            v = self.getPDFPageContent(pg)
            if v != "":
                w = self._generateDeclarationStruct(v)
                self.pdfPages[w.awb] = (w, pg)

    def getPDFPageContent(self, pageObj: PyPDF2.PageObject) -> str:
        """
        Retrieves the content of a page and saves both the binary and textual form.
        :param pageObj: instance of a page.
        :return: text containing value.
        """
        t = ""
        mytext = pageObj.extract_text().encode("UTF-8")  # encode binary to UTF8 then decode as ansi.
        mytext = mytext.decode("ANSI")

        # Extracting characters by comparing their numerical value to get only relevant chars.
        for char in mytext:
            if 47 < ord(char) < 123 or ord(char) == 32 or ord(
                    char) == 46 or char == '\n':  # removes all residual data.
                t += char
        return t

    def _transposePage(self, tup: tuple[StructDeclaration, PyPDF2.PageObject]) -> None:
        """
        Reads a tuple containing a single page from the NOA PDF file and into create a new PDF of a single page.
        :param tup: a tuple of a StructDeclaration and a PageObject.
        :return: None
        """

        folderpath = os.path.join(os.environ["USERPROFILE"], "Downloads\\" + self.uuid)
        if not os.path.exists(folderpath):
            os.makedirs(folderpath)

        pageObj = tup[1]
        decl = tup[0]
        writer = PyPDF2.PdfWriter()
        writer.add_page(pageObj)

        # Creating a destination file with convention renaming.
        with open(
                os.path.join(folderpath, decl.reportNo + "_" + decl.awb + "_OTHER_upload-noa.pdf"), 'wb'
        ) as dest_file:
            writer.write(dest_file)

    def transposeAllPages(self) -> None:
        """
        Reads all pages saved in memory and creates a new PDF with the correct naming convention for each page.
        :return: None
        """
        for key in self.pdfPages.keys():
            self._transposePage(self.pdfPages[key])     # where page is a tuple[StructDeclaration, PyPDF2.PageObject]

    def _generateDeclarationStruct(self, content: str) -> StructDeclaration:
        """
        Takes a string content of the PDF page read and extract the essential information into a struct.
        The StructDeclaration will later be further populated using the Chronopost invoices.
        :param content: string content of a NOA PDF page.
        :return: StructDeclaration
        """
        struct = StructDeclaration()

        struct.shpr = content[content.find("Shipper ") + 8:content.find("Date ")].strip()
        struct.mawb = content[content.find("MAWB ") + 5:content.find("CHRONOPOST  MAURITIUS  LTD")].strip()
        struct.awb = content[content.find("HAWB ") + 5:content.find(" Goods Landed At DPDL")].strip()
        struct.reportNo = content[content.find("Report No ") + 10:content.find("Report No ") + 18].strip()
        pos = content.find("Declared Value ") + 15
        struct.custCurr = content[pos:pos + 3]
        struct.custAmt = eval(content[pos+3:content.find('\n', pos+3)].strip())
        pos = content.find("\nFreight Cost")
        struct.weight = eval(content[content.find(' ', pos - 8):pos].strip())   # stripping the charg weight.
        pos = content.rfind("Consignee") + 9
        struct.cnee = content[pos:content.find('\n', pos)].strip()
        pos = content.find('\n', pos) + 1
        struct.cneeAddr = content[pos:content.rfind('\n')].strip()
        struct.cneeEmail = content[content.rfind('\n') + 1:].strip()
        struct.cneeTel = ""
        struct.NIC = ""
        struct.passport = ""
        struct.DOB = None
        struct.TAN = ""
        struct.BRN = ""
        struct.customerType = "INDIVIDUAL" if struct.BRN == "" else "COMPANY"
        struct.frtAmt = 35.00
        struct.frtCurr = "USD"
        struct.othAmt = 0.0
        struct.othCurr = "USD"

        return struct


if __name__ == '__main__':
    pass
