import datetime as dt


class CSVWriter:

    def __init__(self, usr: str):
        self.user = usr
        self.header = "Courier Reference,AWB,REPORT,IMPORTER2NAME,IMPORTERNAME2,ImporterAddress1,ImporterAddress2,ImporterAddress3,IMPORTERADDRESSCOUNTRY,NATIONALITY,NIC,PASSPORT,EMAILADDRESS,MOBILE,TAN,BRN,IMPORTERTYPE,MOBILE,DOB,COUNTRYOFCONSIGNMENT,DECLAREDFREIGHTFCYAMOUNT,DECLAREDFREIGHTFCYCODE,OTHERCHARGESFCYAMOUNT,OTHERCHARGESFCYCODE,INSURANCEFCYAMOUNT,INSURANCEFCYCODE,HSCODE,GOODSDESCRIPTION,QTY,ORIGIN,SUP1,SUP2,RESERVEVALUE,DECLAREDVALUEFCYAMT,FCYCODE,PURPOSEOFIMPORTATION,USEITEMFLAG,MARKETABLEFLAG,PROXYNAME,PROXYNIC,PROXYADD1,PROXYADD2,PROXYADD3,PROXYADDRESSCOUNTRY\n"
        self.file_log = list()
        self.fileGenerated = ""

    def enterRecord(self, manDetes: tuple | list, custDetes: tuple | list, repDetes: tuple | list,
                    itmDetes: tuple | list):
        """
        Enters a new line to the csv file by reading the lists and tuples given as args.
        :param manDetes: Details of the manifest.
        :param custDetes: Details of the customer from the Gsheet ID folder.
        :param repDetes: Memorizes all the reports relative to the MAWBs read.
        :param itmDetes: The list of items coming from a commercial invoice.
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
            assert len(manDetes) == 26 and len(repDetes) == 2 and len(custDetes) == 4 and len(itmDetes) == 5, manDetes[
                1]
            s = str(len(lns))  # Courier Ref
            s += ',' + str(manDetes[1])  # AWB
            s += ',' + str(repDetes[1])  # Report Number
            name = str(custDetes[0].replace(',', ';'))
            name = name[:35] if len(name) >= 35 else name
            s += ',' + name  # Importer2Name
            s += ',' + name  # ImporterName2
            ad = str(manDetes[18] if manDetes[18].find("Ã©") == -1 else manDetes[18].replace("Ã©", "e"))
            if len(ad) > 34:
                ad = ad[:35]
            s += ',' + str(ad)  # ImporterAddress1
            s += ',' + str(manDetes[20])  # ImporterAddress2
            s += ',' + ""  # ImporterAddress3
            s += ',' + "MU"  # ImporterAddressCountry
            s += ',' + "MAURITIAN"  # Nationality (Mauritian or Foreigner)
            s += ',' + str(custDetes[1] if str(custDetes[1]).strip() != "" else "")  # NIC (IDref or "")
            s += ',' + str(custDetes[2] if str(custDetes[1]).strip() == "" else "")  # Passport (passportRef or "")
            s += ',' + "no_email@yahoo.com"  # emailaddress
            s += ',' + str(manDetes[19])  # Mobile
            s += ',' + ""  # TAN (either TAN or "")
            s += ',' + ""  # BRN (either BRN or "")
            s += ',' + "INDIVIDUAL"  # ImporterType (Individual or Company)
            s += ',' + str(manDetes[19])  # Mobile (again!)
            s += ',' + str(dt.datetime.strptime(custDetes[1][1:7], "%d%m%y").strftime("%d-%m-%Y"))  # DOB
            s += ',' + "HK"  # OriginCountry
            s += ',' + str(round(float(manDetes[23]), 2))  # DeclaredFreightFCYAmt
            s += ',' + str(manDetes[22])  # DeclaredFreightFCYCurr
            s += ',' + str(round(float(manDetes[25]), 2))  # OtherChargesAmt
            s += ',' + str(manDetes[24])  # OtherChargesCurr
            s += ',' + "0"  # InsuranceAmt
            s += ',' + "USD"  # InsuranceCurr
            s += ',' + str(itmDetes[1])  # HSCode
            s += ',' + str(itmDetes[0])  # GoodsDescription
            s += ',' + str(itmDetes[2])  # Qty
            s += ',' + "HK"  # CountryOfProduct
            s += ',' + "0"  # SUP1 (no idea what it is)
            s += ',' + "0"  # SUP2 (Still no idea)
            s += ',' + ""  # ReserveValue (another thing no idea)
            s += ',' + str(itmDetes[4])  # DeclaredValueItem
            s += ',' + "USD"  # ItemCurrency
            s += ',' + "40000"
            s += ',' + "False"  # Used Item (True/False)
            s += ',' + "False"  # If not 'Personal Use', it will be marketable (True/False)
            s += ",,,,,,\n"  # all the proxies we will never use.

            file.write(s)

    def searchWBinF(self, wbDetails: str, lns: list | tuple) -> tuple:
        for ln in lns:
            if str(wbDetails).strip() == ln.split(',')[1]:
                return tuple(ln.split(',')[:-1])

    def searchReportinF(self, mawb: str, lns: tuple | list) -> tuple:
        for ln in lns:
            if str(mawb).strip() == ln[0]:
                return ln

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
