import unittest
import sys
import os
import pathlib
sys.path.insert(1, str(pathlib.Path(os.path.abspath(__file__)).parent.parent))
from main import replace, remove

def scrubPII(input):
    return replace(input)

class TestDetectionMethods(unittest.TestCase):

    def test_multiple_replace(self):
        text = '''"Yesterday, on June 5th, 2023, I met my friend for lunch. We had a great time reminiscing about our childhood memories. 
        Then, on 2023/06/10, we planned to visit a historical museum together. The museum showcased artifacts from the 18th century, 
        and it was fascinating to learn about the events that took place so long ago. Next week, on the 15th of June, we have a special
        event to celebrate our school's founding anniversary. It's incredible to think that our school has been around since 1965. Lastly,
        I have an important appointment on July 1, 2023. I have been eagerly waiting for this day as it marks the start of my summer vacation.
        I can't wait to relax and enjoy the warm weather!"
        '''
        tokenized = remove(text)[2]
        print("\nORIGINAL:\n", text)
        print("\nTOKENIZED:\n", tokenized)
        replaced = replace(tokenized)
        print("\nDETOKENIZED:\n", replaced)
        
        self.assertEqual(replaced, text)

if __name__ == '__main__':
    unittest.main()