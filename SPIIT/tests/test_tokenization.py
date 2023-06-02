import unittest
import sys
import pathlib
import os
sys.path.insert(1, str(pathlib.Path(os.path.abspath(__file__)).parent.parent))
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
        text = '''
        In the charming town of Anytown, USA, John Smith resides at 123 Elm Street, a cozy home adorned with a white picket fence and a beautifully landscaped front yard. With a passion for photography, John spends his evenings capturing the picturesque scenes that surround his neighborhood. You can reach him at johnsmith@email.com if you're interested in his stunning portfolio.

        Just a few blocks away, at 456 Oak Avenue in the bustling Cityville, Sarah Johnson calls her quaint Victorian-style house her home. With a green thumb and a love for gardening, Sarah's front yard bursts with vibrant flowers and meticulously trimmed hedges. If you're interested in her gardening tips or would like to chat, feel free to reach out to her at sarah.johnson@email.com.

        Meanwhile, in the peaceful neighborhood of Townsville, Mark Davis resides at 789 Maple Drive. Mark is an avid collector of antique books and rare vinyl records, which fill his shelves and create an inviting atmosphere in his cozy library. If you share his love for vintage treasures or simply want to discuss literature, send him an email at markdavis@email.com.

        Over in the picturesque Villageland, USA, Emily Roberts has made her home at 321 Pine Street. Nestled amidst tall, swaying trees, Emily's cottage-style house exudes warmth and charm. With a passion for baking, she often fills her kitchen with the sweet aroma of freshly baked cookies and pies. If you're in need of a delightful recipe or simply want to share your love for all things culinary, feel free to get in touch with her at emily.roberts@email.com.

        Each of these individuals brings their unique passions and interests to their neighborhoods, fostering a sense of community and connection. Whether it's photography, gardening, collecting, or baking, the residents of these homes are always eager to share their joy and build new connections with like-minded individuals.
        '''
        tokenDict = dict()
        tokenList1 = tokenizePII(text)
        for token in tokenList1:
            tokenDict.update({token[1]: token[2]})
        tokenList2 = tokenizePII(text)
        for token in tokenList2:
            print(token[1],token[2],tokenDict[token[1]])
            self.assertTrue(tokenDict[token[1]] == token[2])
        tokenList3 = tokenizePII(text)
        for token in tokenList3:
            print(token[1],token[2],tokenDict[token[1]])
            self.assertTrue(tokenDict[token[1]] == token[2])

    
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
        for i in range(2):
            tokenList = tokenizePII(text)
            for token in tokenList:
                self.assertTrue(token[2] not in allTokens)
                allTokens.append(token[2])
        






if __name__ == "__main__":
    unittest.main()