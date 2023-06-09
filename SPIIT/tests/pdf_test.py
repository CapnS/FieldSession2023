import unittest
import sys
import os
import pathlib
sys.path.insert(1, str(pathlib.Path(os.path.abspath(__file__)).parent.parent))
from main import replace, remove

def scrubPII(input):
    return replace(input)

class TestDetectionMethods(unittest.TestCase):

    def test_pdf(self):
        text = '''"INVOICE # 3 James James Bill To : Hunter Gold Ship To : 1249 Real Street, Golden, CO, 80401 May 30, 2023 $5,000.00 
        Date : Balance Due : Item Quantity Rate Amount Huge, Big, Absolutely Massive Cheeseburgers 5 $1,000.00 $5,000.00 $5,000.00 $0.00 
        $5,000.00 Subtotal : Tax (0%) : Total : Notes : Once upon a time in the bustling town of Oakwood, there existed a legendary burger
        joint known as "The Flaming Grill." Their mouthwatering burgers were the talk of the town, and people from far and wide would flock 
        to savor their delectable creations. However, there was one particular customer named Hunter Gold who held a special status at the restaurant.
        Hunter Gold was a renowned food enthusiast, with a palate that could discern the finest flavors and textures in any dish. 
        His love for burgers was unmatched, and he had an uncanny ability to identify the subtlest nuances that made each burger truly exceptional. 
        The Flaming Grill recognized Hunter's discerning taste and had a surprise in store for him. One fine day, the restaurant manager, Mr. Thompson, 
        received a mysterious invoice for a special order of burgers. The invoice listed Hunter Gold as the only authorized recipient. Intrigued, 
        Mr. Thompson meticulously examined the document and noticed something unusual. Alongside Hunter's name, there were indeed personal details provided 
        to ensure a flawless burger handoff. The invoice listed Hunter Gold's phone number as 714-215-1234, his email as huntergold@email.com, 
        and even included 
        his driver's license number: DL 123456. Mr. Thompson marveled at the thoroughness of the information provided, acknowledging that no stone had been left
        unturned to ensure the burgers reached their rightful recipient. Curiosity piqued, Mr. Thompson decided to call Hunter Gold to discuss the unique order.
        As he dialed the number, he couldn't help but wonder what made Hunter so special that the burgers were exclusively designated for him. 
        "Hello?" a voice answered on the other end of the line. "
        '''
        tokenized = remove(text)[2]
        print("\nORIGINAL:\n", text)
        print("\nTOKENIZED:\n", tokenized)
        replaced = replace(tokenized)
        print("\nDETOKENIZED:\n", replaced)
        
        self.assertEqual(replaced, text)

if __name__ == '__main__':
    unittest.main()