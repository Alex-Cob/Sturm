import os
import re
import gspread


FOLDERCREDS = os.path.abspath("aoth")
FILESERVACC = os.path.join(FOLDERCREDS, "service_account.json")


class GSheetParse:
    FOLDERCREDS = ""

    def __init__(self):
        self.file_creds = os.path.join(FOLDERCREDS, "service_account.json")
        self.service = gspread.service_account(self.file_creds)
        self.customerData = self.downloadClientData()
        self.szCustDataFields = 6    # amount of columns per record where data is stored.

    def downloadClientData(self) -> list:
        """
        Retrieves the whole data from the google sheet
        :return: list of personal details.
        """
        sh = self.service.open("ClientRecord").worksheet("Record")
        rng = sh.range("A2:F")
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

    def guessCustomer(self, name_: str):
        # tries to guest customer from name.
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


if __name__ == '__main__':
    pass
