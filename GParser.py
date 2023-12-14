import re
import gspread

from Misc import *


class IndexIDRecord:
    name = 0
    email = 1
    telephone = 2
    NIC = 3
    passport = 4
    DOB = 5
    proxyName = 6
    proxyID = 7


class IDParser:
    CELLRANGE = "A2:H"

    def __init__(self, service: gspread.auth.Client = None):
        self.file_creds = FILESERVACC
        self.szCustDataFields = 8    # amount of columns per record where data is stored.
        if service is None:
            self.service = gspread.service_account(self.file_creds)
        else:
            self.service = service
        self.customerData = self.downloadClientData()

    def downloadClientData(self) -> list:
        """
        Retrieves the whole data from the Google sheet
        :return: list of personal details.
        """
        sh = self.service.open(SPREADSHEET_CUSTOMERS).worksheet(SHEET_CUSTOMER)
        rng = sh.range(IDParser.CELLRANGE)
        x = self._orderCustomersPulled(rng)
        return x.copy()

    def _orderCustomersPulled(self, rng: list) -> list[list]:
        """
        Takes the 1D list passed and converts it into a 2D list of the size
        of the columns.
        :return: list of list
        """
        lstCustomers = []
        sublst = []
        x = 0
        while x < len(rng):
            # checks if the first column (name) is empty. Pattern ensures this line falls on name.
            if rng[x].value in (None, ""):
                break
            for i in range(self.szCustDataFields):      # will iterate for each column in each entry/row.
                sublst.append(rng[x].value)
                x += 1      # iterating for the 'while' loop
            lstCustomers.append(sublst.copy())
            sublst.clear()
        return lstCustomers.copy()

    def _getCandidateFromSegmentName(self, segmentName: str) -> list:
        """
        Checks a single segment of name at a time to get corresponding values.
        :param segmentName: a segment of a fullname eg ('Alex' or 'Joseph')
        :return: list of lists of candidates filtered out.
        """
        retVals = []
        x = 0  # the second elem of the series

        while x < len(self.customerData):
            # Checks the lines that contain this segment
            if re.search(segmentName.lower(), self.customerData[x][0].lower()):
                retVals.append(self.customerData[x])
            x += 1  # so that it searches the next
        return retVals.copy()

    def guessCustomer(self, name_: str) -> list[list]:
        """
        Will take a full name and try to determine the customer that was expected.
        :param name_: Fullname being sought.
        :return: list of all the candidates worth.
        """
        sublstOfSets = list()
        nm = name_.replace(')', '').replace('(', '').replace('\\', '')  # because of Shein names containing these chars

        # Below breaks the full name into segments by splitting where a space is found.
        for seg in nm.split(' '):
            if seg != '':
                sublstOfSets.append(self._getCandidateFromSegmentName(seg))

        x = 0
        sz = len(sublstOfSets)
        mainLst = list()
        tempLst = list()

        # it works, don't touch.
        while x + 1 < sz:
            if len(mainLst) == 0:
                tempLst.clear()
                for res1 in sublstOfSets[x]:
                    for res2 in sublstOfSets[x + 1]:
                        if res1 == res2:
                            tempLst.append(res1)
                mainLst = tempLst.copy()
            else:
                tempLst.clear()
                for res1 in mainLst:
                    for res2 in sublstOfSets[x + 1]:
                        if res1 == res2:
                            tempLst.append(res1)
                mainLst = tempLst.copy()
            x += 1
        return mainLst


# noinspection PyMethodMayBeStatic
class HSParser:

    def __init__(self, service: gspread.auth.Client = None):
        self.file_creds = FILESERVACC
        if service is None:
            self.service = gspread.service_account(self.file_creds)
        else:
            self.service = service
        self.knownCommodities = self.retrieveKnownCommodities()      # list of tuples of commodity / HS code pairs.

    def retrieveKnownCommodities(self) -> list[tuple]:
        """
        Will retrieve the record from the google sheet and place in memory for easy use.
        :return: None
        """
        sh = self.service.open(SPREADSHEET_HSCODES).worksheet(SHEET_HSCODES)
        rng = sh.range("A2:B")
        x = self._sortPairs(rng)
        return x.copy()

    def _sortPairs(self, rng: list) -> list[tuple]:
        items = []
        pairs = []
        x = 0
        while x < len(rng):
            # checks if the first column (name) is empty. Pattern ensures this line falls on name.
            if rng[x].value in (None, ""):
                break
            for i in range(2):  # will iterate for each column in each entry/row.
                pairs.append(rng[x].value)
                x += 1  # iterating for the 'while' loop
            items.append(tuple(pairs))
            pairs.clear()
        return items.copy()


if __name__ == '__main__':
    pass
