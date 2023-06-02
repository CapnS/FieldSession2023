import unittest
import sys
import os
import pathlib
sys.path.insert(1, str(pathlib.Path(os.path.abspath(__file__)).parent.parent))
from main import replace, remove

def scrubPII(input, tokenDict=None):
    return replace(input, tokenDict)

class TestDetectionMethods(unittest.TestCase):
    def test_nodatabase(self):
        remove("Hello, my phone number is 713-392-8668")[0]
        tokenDict = {""}
        text =  ""

if __name__ == '__main__':
    unittest.main()