import unittest
import sys
sys.path.insert(1, 'C:\\Users\\zacha\\Documents\\Python\\GPT4 LangChain PII Tokenization\\Project-2-Secure-PII-Tokenization-for-LLMs\\SPIIT')
from main import remove
import PyPDF2

def tokenizePII(input):
    return remove(input)[1]

class TestTokenizationMethods(unittest.TestCase):

    def test_consistency(self):
        text = '''Notes:
        these passports have specific passport numbers for each and they tie into specific peoples ids:
        Jeffery App -> E91247812 -> 125-25-2623
        That was for one, i will no list all of the other ones.
        Jacob Smith -> A12420291 -> 251-51-2513
        Blake Jones -> J01417521 -> 824-12-6234
        Jill Withers -> O92942124 -> 591-62-1241
        And finally we have the last passport's information:
        John Johnson -> K85129283 -> 912-15-7475
        Blake Jones -> J01417521 -> 824-12-6234
        Terms:
        Jeffery App -> E91247812 -> 125-25-2623
        DL-9123471023
        Jeffery App -> E91247812 -> 125-25-2623
        Now for some terms of the document, these passports must be used by the same people they are named for, no illegal
        passport usage. In order to make sure of this, we have put chips in them that track with specific drivers licenses. The
        number for these licenses is as follows and in order of how I listed them before: 175819278, J1323633, E912848,
        1241395133, DL-9123471023
        Blake Jones -> J01417521 -> 824-12-6234
        The number for these licenses is as follows and in order of how I listed them before: 175819278, J1323633, E912848,
        1241395133, DL-9123471023
        '''

        tokenList = tokenizePII(text)
        tokenDict = dict()

        for token in tokenList:
            if token[1] not in tokenDict:
                self.assertTrue(token[2] not in tokenDict.values())
                tokenDict.update({token[1]:token[2]})
            else:
                print(token[1], token[2], tokenDict[token[1]])
                self.assertTrue(tokenDict[token[1]] == token[2])
    
    def test_consistency_across_runs(self):
        '''eventually when we integrate with the database, we will use this to ensure that across all pdfs the same token
            will relate to the same PII. If not, the detokenization will break.'''
        pass

    
    def test_randomness(self):
        text = '''List of People and Their SSNs:

        Jackson Stein: 124-53-1345
        Max Johnson: 156-24-1582
        Jim Jimmy: 982-63-6324
        Sean Goldman: 609-15-6314


        List of Those People and Their Favorite Ice Cream:

        Jackson Stein: Chocolate
        Max Johnson: Vanilla
        Jim Jimmy: Strawberry
        Sean Goldman: Rocky Road


        List of Those People and Their Email Addresses:

        Jackson Stein: jstein@gmail.com
        Max Johnson: maxwjohnson@yahoo.com
        Jim Jimmy: jimster01@gmail.com
        Sean Goldman: seangold@hotmail.com


        List of Those People and Their Hair Color:

        Jackson Stein: Brown
        Max Johnson: Brown
        Jim Jimmy: Blonde
        Sean Goldman: Red


        List of Those People and Their Home Address:

        Jackson Stein: 8190 Elmora Street
        Max Johnson: 1020 Illinois St.
        Jim Jimmy: 834 Jim blvd.
        Sean Goldman: 5 Waverly Ct.

        List of Those People and Their Favorite Board Game:

        Jackson Stein: Monopoly
        Max Johnson: Chutes and Ladders
        Jim Jimmy: Sorry
        Sean Goldman: Settlers of Catan
        '''
        allTokens = []
        for i in range(100):
            tokenList = tokenizePII(text)
            for token in tokenList:
                self.assertTrue(token[2] not in allTokens)
                allTokens.append(token[2])
        






if __name__ == "__main__":
    unittest.main()