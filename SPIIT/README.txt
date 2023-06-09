To install packages run:
pip3 install -r SPIIT/requirements.text
or 
python -m pip install -r SPIIT/requirements.txt

to download the spacy model run this:
python3 -m spacy download en_core_web_sm
or 
python -m spacy download en_core_web_sm

also need:
import nltk
nltk.download('punkt')


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
and change line 26
`text += '\n' + item.str;` to `text += '\n' + item.str + ' ';`


In order to run the app you will need two terminal windows, the first should have SPIIT as the CWD, and the other the main project file
For the one in the SPIIT folder, you will need to run:
`python -m flask --app main.py run`
and for the one in the main project file, you will run either `npm run ingest` for ingestion or `npm run dev` for the actual GPT window


Limitations:
