import os

__VERSION__ = "0.2.0"

FOLDERCREDS = os.path.abspath(".")
FILESERVACC = os.path.join(FOLDERCREDS, "chrono-sturm-creds.json")
SPREADSHEET_CUSTOMERS = "ID Database"
SHEET_CUSTOMER = "ID Data"
SPREADSHEET_HSCODES = "HSMapping"
SHEET_HSCODES = "Items"


class LogLevel:
    """Defines the type of information being logged in func 'log'"""
    INFO = 0
    WARNING = 1
    ERROR = 2


def log(msg: str, level=LogLevel.INFO) -> None:
    """
    Centralized method of logging info.
    :param msg: Message to be transmitted (string)
    :param level: LogLevel, defines the type of message logged.
    :return: None (could be Any)
    """
    print(msg)


class IndexIDRecord:
    name = 0
    telephone = 1
    email = 2
    NIC = 3
    passport = 4
    DOB = 5
    proxyName = 6
    proxyID = 7


class StructDeclaration:

    def __init__(self):
        self.shpr = ""
        self.cnee = ""
        self.mawb = ""
        self.awb = ""
        self.reportNo = ""
        self.custCurr = ""
        self.custAmt = 0.0
        self.weight = 0.0
        self.cneeAddr = ""
        self.cneeTel = ""
        self.cneeEmail = ""
        self.NIC = ""
        self.passport = ""
        self.DOB = None
        self.TAN = ""
        self.BRN = ""
        self.customerType = "INDIVIDUAL"      # company or individual
        self.frtAmt = 35.00
        self.frtCurr = "USD"
        self.othAmt = 0.00
        self.othCurr = "USD"
        self.itemdetails = None    # Specific invoice details such as description, item value, item qty and HS code to be added on spot.


if __name__ == '__main__':
    pass
