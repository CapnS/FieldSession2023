import unittest
import sys
import os
import pathlib
sys.path.insert(1, str(pathlib.Path(os.path.abspath(__file__)).parent.parent))
from main import replace, remove

def scrubPII(input):
    return replace(input)

class TestDetectionMethods(unittest.TestCase):
    def test_simplereplace(self):
        text = remove("Hello, my phone number is 713-392-8668")[2]
        replaced = replace(text)
        self.assertEqual(replaced,"Hello, my phone number is 713-392-8668")

    def test_hard_replace(self):
        text = '''
        In the charming town of Anytown, USA, John Smith resides at 123 Elm Street, a cozy home adorned with a white picket fence and a beautifully landscaped front yard. With a passion for photography, John spends his evenings capturing the picturesque scenes that surround his neighborhood. You can reach him at johnsmith@email.com if you're interested in his stunning portfolio.

        Just a few blocks away, at 456 Oak Avenue in the bustling Cityville, Sarah Johnson calls her quaint Victorian-style house her home. With a green thumb and a love for gardening, Sarah's front yard bursts with vibrant flowers and meticulously trimmed hedges. If you're interested in her gardening tips or would like to chat, feel free to reach out to her at sarah.johnson@email.com.

        Meanwhile, in the peaceful neighborhood of Townsville, Mark Davis resides at 789 Maple Drive. Mark is an avid collector of antique books and rare vinyl records, which fill his shelves and create an inviting atmosphere in his cozy library. If you share his love for vintage treasures or simply want to discuss literature, send him an email at markdavis@email.com.

        Over in the picturesque Villageland, USA, Emily Roberts has made her home at 321 Pine Street. Nestled amidst tall, swaying trees, Emily's cottage-style house exudes warmth and charm. With a passion for baking, she often fills her kitchen with the sweet aroma of freshly baked cookies and pies. If you're in need of a delightful recipe or simply want to share your love for all things culinary, feel free to get in touch with her at emily.roberts@email.com.

        Each of these individuals brings their unique passions and interests to their neighborhoods, fostering a sense of community and connection. Whether it's photography, gardening, collecting, or baking, the residents of these homes are always eager to share their joy and build new connections with like-minded individuals.
        '''
        tokenized = remove(text)[2]
        #print(tokenized)
        replaced = replace(tokenized)
        #print(replaced)
        self.assertEqual(replaced, text)
        

if __name__ == '__main__':
    unittest.main()