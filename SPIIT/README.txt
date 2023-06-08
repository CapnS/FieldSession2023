To install packages run:
pip3 install -r SPIIT/requirements.text
or 
python -m pip install -r SPIIT/requirements.txt

also need:
nltk.download('punkt')
python3 -m spacy download en_core_web_sm

To install javascript packages use the following:
npm install next
npm install nookies
npm install react
npm install react-modal
npm install winston
npm audit fix

Finally, you will have to change the way node parses pdfs like so:

go to node_modules/pdf-parse/lib/pdf-parse.js and on line 23 change
`text += item.str` to `text += item.str + ' '`