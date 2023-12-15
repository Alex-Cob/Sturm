import datetime as dt
import os
import PyPDF2
from Misc import *
import PDFProcessor


class CSVWriter:

    def __init__(self, path: str):
        self.header = "Courier Reference,AWB,REPORT,IMPORTER2NAME,IMPORTERNAME2,ImporterAddress1,ImporterAddress2,ImporterAddress3,IMPORTERADDRESSCOUNTRY,NATIONALITY,NIC,PASSPORT,EMAILADDRESS,MOBILE,TAN,BRN,IMPORTERTYPE,MOBILE,DOB,COUNTRYOFCONSIGNMENT,DECLAREDFREIGHTFCYAMOUNT,DECLAREDFREIGHTFCYCODE,OTHERCHARGESFCYAMOUNT,OTHERCHARGESFCYCODE,INSURANCEFCYAMOUNT,INSURANCEFCYCODE,HSCODE,GOODSDESCRIPTION,QTY,ORIGIN,SUP1,SUP2,RESERVEVALUE,DECLAREDVALUEFCYAMT,FCYCODE,PURPOSEOFIMPORTATION,USEITEMFLAG,MARKETABLEFLAG,PROXYNAME,PROXYNIC,PROXYADD1,PROXYADD2,PROXYADD3,PROXYADDRESSCOUNTRY\n"
        self.file_log = list()
        csvpath = os.path.join(path, "worked.csv")
        if os.path.exists(csvpath):
            os.remove(csvpath)
        self.fileGenerated = csvpath
        self.NewHSItems = set()

    def enterRecord(self, structDecl: StructDeclaration, hsCodes: list[tuple]):
        """
        Enters a new line to the csv file by reading the lists and tuples given as args.
        :param structDecl: the structure containing all relevant info.
        :return:
        """
        lns = list()
        needHeader = False
        try:
            with open(self.fileGenerated, 'r') as file:
                lns = file.readlines()
        except FileNotFoundError:
            needHeader = True
        with open(self.fileGenerated, 'a') as file:
            if needHeader:
                file.write(self.header)
                lns.append(self.header)
            # assert len(manDetes) == 26 and len(repDetes) == 2 and len(custDetes) == 4 and len(itmDetes) == 5, manDetes[1]
            increment = 0
            for itm in structDecl.itemdetails:
                s = str(len(lns) + increment)  # Courier Ref
                s += ',' + structDecl.awb  # AWB
                s += ',' + structDecl.reportNo  # Report Number
                name = structDecl.cnee.replace(',', ';')
                name = name[:35] if len(name) >= 35 else name
                s += ',' + name  # Importer2Name
                s += ',' + name  # ImporterName2
                ad = str(structDecl.cneeAddr if structDecl.cneeAddr.find("Ã©") == -1 else structDecl.cneeAddr.replace("Ã©", "e"))
                if len(ad) > 34:
                    ad = ad[:35]
                s += ',' + str(ad)  # ImporterAddress1
                s += ',' + "Port Louis"  # ImporterAddress2
                s += ',' + ""  # ImporterAddress3
                s += ',' + "MU"  # ImporterAddressCountry
                s += ',' + "MAURITIAN"  # Nationality (Mauritian or Foreigner)
                s += ',' + structDecl.NIC.strip() if structDecl.NIC.strip() != "" else ""  # NIC (IDref or "")
                s += ',' + structDecl.passport.strip() if structDecl.passport.strip() == "" else ""  # Passport (passportRef or "")
                s += ',' + structDecl.cneeEmail  # emailaddress
                s += ',' + structDecl.cneeTel  # Mobile
                s += ',' + ""  # TAN (either TAN or "")
                s += ',' + ""  # BRN (either BRN or "")
                s += ',' + "INDIVIDUAL"  # ImporterType (Individual or Company)
                s += ',' + str(structDecl.cneeTel)  # Mobile (again!)
                s += ',' + structDecl.DOB  # DOB
                s += ',' + "HK"  # OriginCountry
                s += ',' + str(round(float(structDecl.frtAmt), 2))  # DeclaredFreightFCYAmt
                s += ',' + str(structDecl.frtCurr)  # DeclaredFreightFCYCurr
                s += ',' + str(round(float(structDecl.othAmt), 2))  # OtherChargesAmt
                s += ',' + str(structDecl.othCurr)  # OtherChargesCurr
                s += ',' + "0"  # InsuranceAmt
                s += ',' + "USD"  # InsuranceCurr
                s += ',' + str(self.defineHS(itm[0], hsCodes))  # HSCode
                s += ',' + str(itm[0])  # GoodsDescription
                s += ',' + str(itm[1])  # Qty
                s += ',' + "HK"  # CountryOfProduct
                s += ',' + "0"  # SUP1 (no idea what it is)
                s += ',' + "0"  # SUP2 (Still no idea)
                s += ',' + ""  # ReserveValue (another thing no idea)
                s += ',' + str(itm[3])  # DeclaredValueItem
                s += ',' + "USD"  # ItemCurrency
                s += ',' + "40000"
                s += ',' + "False"  # Used Item (True/False)
                s += ',' + "False"  # If not 'Personal Use', it will be marketable (True/False)
                s += ",,,,,,\n"  # all the proxies we will never use.
                increment += 1
                file.write(s)

    def convertStr2List(self, ln: str) -> list:
        """
        Converts a list lookalike (generally as a string in a file from a python ops return) into an actual list.
        This was designed to work with shein returns only.
        :param ln: (str) list look-alike
        :return: list
        """
        countOp = 0
        mainLst = list()
        sublist = ""
        endClause = False
        for char in ln.strip():
            if char in ("'", '"'):
                continue
            if char == '[' and countOp == 0:  # start only
                countOp += 1
                endClause = False
            elif char == '[':  # inner brackets
                countOp += 1
                sublist += char
                endClause = False
            elif char == ']' and countOp == 1:  # closing brackets of outermost array
                countOp -= 1
                if sublist != '':
                    mainLst.append(sublist)
                    sublist = ""
                endClause = True
            elif char == ']':
                countOp -= 1
                if countOp < 0:  # if the syntax is missing an opening bracket.
                    raise SyntaxError("Syntax somehow incorrect...")
                sublist += char
                mainLst.append(self.convertStr2List(sublist).copy())
                sublist = ""
                endClause = True
            else:
                if endClause:
                    if char in (' ', ','):
                        continue
                sublist += char
        if countOp == 0:
            retList = list()
            for elem in mainLst:
                if repr(type(elem)) == "<class 'str'>":
                    retList = [elm.strip() for elm in elem.split(',')]
                if repr(type(elem)) == "<class 'list'>":
                    retList.append(elem.copy())
            return retList.copy()
        else:
            raise SyntaxError("Syntax somehow incorrect...")  # meaning there was not enough closing brackets

    def defineHS(self, itmName: str, knownHS: list[tuple]):
        itnnm = itmName.lower().strip()
        for hs in knownHS:
            if itnnm == hs[0].lower().strip():
                return hs[1]
        self.NewHSItems.add(itmName)
        return "01012100"       # Literally pure-breed horses


if __name__ == '__main__':
    pass
