#import snowflake
import sys
from nltk import tokenize
import nltk
import spacy
import phonenumbers
import re
import uuid
import PyPDF2
from transformers import pipeline

from dotenv import load_dotenv
import os

# N - Name 
# A - Address 
# O - Organization name 
# U - Undefined PII 
# P - Phone number 
# R - Passport
# D - Driver's license
# B - ID number
# S - SSN
# I - IP address 
# C - CC

def remove(text):
    ner_model = "dslim/bert-base-NER"

    punc_list = '''!()[]{};*:'"\,<>./?_~-'''
    ssn_validate_pattern = "^(?!666|000|9\\d{2})\\d{3}-(?!00)\\d{2}-(?!0{4})\\d{4}$"
    email_validate_pattern = r"^\S+@\S+\.\S+$"
    ip_validate_pattern = "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
    mac_validate_pattern = "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})|([0-9a-fA-F]{4}\\.[0-9a-fA-F]{4}\\.[0-9a-fA-F]{4})$"
    passport_pattern_old = r"^[A-Z0-9]{9}$"
    passport_pattern_new = r"^[A-Z]\d{8}$"
    # we can add more cc types
    amex_validate_pattern = "^3[47][0-9]{13}$"
    visa_validate_pattern = "^4[0-9]{12}(?:[0-9]{3})?$"
    master_card_validate_pattern = "^(5[1-5][0-9]{14}|2(22[1-9][0-9]{12}|2[3-9][0-9]{13}|[3-6][0-9]{14}|7[0-1][0-9]{13}|720[0-9]{12}))$"

    #read pdf and store it as a string 
    '''
    p = open('Invoice  with lots of Passport Numbers, names, ssns, and drivers license numbers.pdf', 'rb')
    pdf = PyPDF2.PdfReader(p)
    text = pdf.pages[0].extract_text() + "\n"
    text = " ".join(text.replace(u"\xa0", " ").strip().split())
    '''
    text2 = text 
    text4 = text 
    

    #load text in nlp
    ner = pipeline("ner", model=ner_model, grouped_entities=True)
    output = ner(text)

    #print(output)

    #print("Original string: ")
    #print(text)
    text3 = text

    #key words lists
    undetected_pii_list = ["DL", "driver's license", "driving permit", "driver license", "drivers license", "dl#","dls#", "lic#","lics#", "ID", "passport", "bank account", "account number", "Passport number"]
    passport_words = ["passport number" , "passport#"]
    dl_words = ["DL", "driver's license", "driving permit", "driver license", "drivers license", "dl#","dls#", "lic#","lics#", "licenses"]
    id_words = ["ID", "ID#", "ID number", "identification documents", "ID card"]

    #empty lists will be used to collect all the data associated with it and further stored in one nested loop to keep all the pii
    # in one place for easier tokenization
    people_list = []
    address_list = []
    ssn_list = []
    other_list = []
    email_list = []
    phone_list = []
    date_list = []
    undefined = []
    org_list = []
    ip_list = []
    cc_list = []
    passport_list = []
    all_pii = []

    #parts of the addresses sometimes wrongfully identified as names, so addresses needs to extracted first to avoid that 
    for entity_group in output:
        entity_label = entity_group["entity_group"]  
        if entity_label == "LOC":
            temp = entity_group["word"]
            start_ind = text.find(temp)
            end_ind = start_ind + len(temp)
            if not text[end_ind].isspace() and text[end_ind] not in punc_list:
                end_ind = text.find(" ", end_ind)
                temp = text[start_ind:end_ind]
            
            #print("Here is a substring ")
            # Find the previous word and check if it is numeric to identify if it is part of the address 
            previous_word = text.rfind(" ", 0, start_ind-1)
            #print(previous_word)
            # Extract the previous word using string slicing
            p_word = text[previous_word + 1:start_ind-1]
            isDigit = True;
            for x in p_word:
                if x.isdigit() == False:
                    isDigit == False;
            # if it is numeric combine with the rest of address 
            if isDigit and len(p_word) < 5:
                start_ind = previous_word
                temp = p_word + " " + temp 
            address_list.append(temp)
            #mask it with xxx for testing purposes 
            x = 'x';
            for n in range (len(temp)-1):
                x = x + 'x';             
            text = text[:start_ind] + x + text[start_ind+len(x):]
    #print(text)

    # extract punctuation for better performance of the libraries 
    for i in text4:
        if i in punc_list:
            if i == '.':
                text4 = text4.replace(i, " ")
            else:
                text4 = text4.replace(i, "")

    # detect passport number and replace it with xxx
    # only new passports have a format that unique from other 
    for word in text4.split():
        #edge case: make sure that there is no punctuation after the passport number; otherwise, it will not be detected
        if word[-1] in punc_list:
            word = word[:-1]
        if (re.match(passport_pattern_new, word)):

            passport_list.append(word)
            x = 'x';
            for n in range (len(word)-1):
                x = x + 'x'; 
            text = text.replace(word, x)
            
    new_list = []
    new_list.append("R")
    new_list.append(passport_list)
    all_pii.append(new_list)


    # load data from nlp into lists associated with it 
    for entity_group in output:
        
        entity_label = entity_group["entity_group"]  

        if entity_label == "PER":
            # check if the word is complete since the model sometimes tempts to grab just the beginning of the name 
            temp = entity_group["word"]
            start_ind = text.find(temp)
            end_ind = start_ind + len(temp)
            if not text[end_ind].isspace() and text[end_ind] not in punc_list:
                end_ind = text.find(" ", end_ind)
                temp = text[start_ind:end_ind]
            people_list.append(temp)
            #mask it with xxx for testing purposes 
            x = 'x';
            for n in range (len(temp)-1):
                x = x + 'x';             
            text = text[:start_ind] + x + text[start_ind+len(x):]
        elif entity_label == "MISC":
            # check if the word is complete since the model sometimes tempts to grab just the beginning of the name 
            temp = entity_group["word"]
            start_ind = text.find(temp)
            end_ind = start_ind + len(temp)
            if not text[end_ind].isspace() and text[end_ind] not in punc_list:
                end_ind = text.find(" ", end_ind)
                temp = text[start_ind:end_ind]
            undefined.append(temp)
            #mask it with xxx for testing purposes 
            x = 'x';
            for n in range (len(temp)-1):
                x = x + 'x';             
            text = text[:start_ind] + x + text[start_ind+len(x):]
        elif entity_label == "ORG":
            org_list.append(entity_group["word"])

            

    # create temporary new lists that will hold the char associated with pii and a list of all piis 
    # then append each list in one nested list all_pii 
    # so we end up getting something like this:
    # all_pii = [['N', ['Chris Johnson']], ['O', ['Diamond Star International', 'Diamond Star']], ['P', ['713-832-1234']]]

    new_list = []
    new_list.append("N")
    new_list.append(people_list)
    all_pii.append(new_list)

    new_list = []
    new_list.append("A")
    new_list.append(address_list)      
    all_pii.append(new_list)

    new_list = []
    new_list.append("O")
    new_list.append(org_list)      
    all_pii.append(new_list)

    new_list = []
    new_list.append("U")
    new_list.append(undefined)      
    all_pii.append(new_list)

    # mask all the pii detected by nlp with xxx for testing purposes 
    for entity_group in output:
    
        if text.find(entity_group["word"]) > -1:
            temp = entity_group["word"]
            for word in temp.split():       
                if text.find(word) > -1:
                    index = text.find(word)
                    x = 'x';
                    for n in range (len(word)-1):
                        x = x + 'x';             
                    text = text[:index] + x + text[index+len(x):]
                

    # The code below will handle all the pii that NLP did not detect
    #--------------------------------------------------------------------
    # Extract sentences that have keywords and insert them into new_list 

    new_list = []
    tok_text = tokenize.sent_tokenize(text2)
    for sentence in tok_text:
        for word in undetected_pii_list:        
            if word in sentence:
                if sentence not in new_list:
                    new_list.append(sentence)

    # get rid of the sentences that have keywords but don't have digits 
    for sentence in new_list:
        isDigit = False;
        for word in sentence: 
            if word.isdigit() == True:
                isDigit = True;
        if isDigit == False:
            new_list.remove(sentence)

    #create a nested list that will hold char of the pii and the value
    clean_undetected_list = [] 

    for sentence in new_list:
        #print(sentence)
        sentence_list = []
        #check if there is only one type of the document mentioned in the sentence 
        #if there id more than one, the pii will go into undefined list
        one_type = 0;
        # assign char depending on the type of pii
        for word in id_words:
            if word.lower() in sentence.lower():
                one_type = one_type + 1
                char = "B"
        for word in dl_words:
            if word.lower() in sentence.lower():
                one_type = one_type + 1
                char = "D"
        #trace the the numeric pii 
        for word in sentence.split():
            isDigit = False;
            for char in word:
                if char.isdigit() == True:
                    isDigit = True; 
            if isDigit == True and len(word) > 5 and word[0] != "$":
                # sometimes it will grab pii with punctuation, so we need to make sure to get rid of it before passing into the list 
                if word[-1] in punc_list:
                    word = word[:-1]
                if one_type == 1:
                    clean_undetected_list.append(char)
                    sentence_list.append(word)
                else:
                    undefined.append(word)
                #replace pii with xxx
                if text.find(word) > -1:
                    index = text.find(word)
                    x = 'x';
                    for n in range (len(word)-1):
                        x = x + 'x';             
                    text = text[:index] + x + text[index+len(x):]
        if len(sentence_list) > 0 :
            clean_undetected_list.append(sentence_list)
    #if len(clean_undetected_list) > 0:
        #all_pii.append(clean_undetected_list)

    # detect ssn and replace it with xxx
    for word in text.split():
        #edge case: make sure that there is no punctuation after the ssn; otherwise, it will not be detected
        #all the punctuation can not be extracted at this point because "-" are part of the ssn
        if word[-1] in punc_list:
            word = word[:-1]
        if (re.match(ssn_validate_pattern, word)):
            # append ssn to ssn_list
            ssn_list.append(word)
            x = 'x';
            for n in range (len(word)-1):
                x = x + 'x'; 
            text = text.replace(word, x)
            
    new_list = []
    new_list.append("S")
    new_list.append(ssn_list)
    all_pii.append(new_list)

    # detect phone numbers and replace them with xxx       
    for match in phonenumbers.PhoneNumberMatcher(text, "US"):
        for word in text.split():
            if word == match.raw_string:
            #append phone numbers to phone_list
                phone_list.append(word)
                x = 'x';
                for n in range (len(word)-1):
                    x = x + 'x'; 
                text = text.replace(word, x)
                
    new_list = []
    new_list.append("P")
    new_list.append(phone_list)
    all_pii.append(new_list)

    # detect email and replace it with xxx
    for word in text.split():
        if (re.match(email_validate_pattern, word)):
            #edge case: make sure that there is no punctuation after the email; otherwise, it will be grabbed and considered as a part of the email
            #all the punctuation can not be extracted at this point because "@" and "." are part of the email
            if word[-1] in punc_list:
                word = word[:-1]
            email_list.append(word)
            x = 'x';
            for n in range (len(word)-1):
                x = x + 'x'; 
                
            text = text.replace(word, x)

    new_list = []
    new_list.append("E")
    new_list.append(email_list)
    all_pii.append(new_list)

    # detect ip address and replace it with xxx
    for word in text.split():
        if (re.match(ip_validate_pattern, word) or re.match(mac_validate_pattern, word)):
            #edge case: make sure that there is no punctuation after the ip address; otherwise, it will be grabbed and considered as a part of the address
            #all the punctuation can not be extracted at this point because "." is part of the address 
            if word[-1] in punc_list:
                word = word[:-1]
            ip_list.append(word)
            x = 'x';
            for n in range (len(word)-1):
                x = x + 'x'; 
                
            text = text.replace(word, x)

    new_list = []
    new_list.append("I")
    new_list.append(ip_list)
    all_pii.append(new_list)

    # detect cc and replace it with xxx
    for word in text.split():
        if (re.match(amex_validate_pattern, word) or re.match(visa_validate_pattern, word) or re.match(master_card_validate_pattern, word)):
            #edge case: make sure that there is no punctuation after the cc
            if word[-1] in punc_list:
                word = word[:-1]
            cc_list.append(word)
            x = 'x';
            for n in range (len(word)-1):
                x = x + 'x'; 
                
            text = text.replace(word, x)

    new_list = []
    new_list.append("C")
    new_list.append(cc_list)
    all_pii.append(new_list)

    #second nlp that we are using for dates 
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)            
    
    # using spacy library to detect dates
    for entity in doc.ents:
        #print(entity.label_ +": " + entity.text)
        if entity.label_ == "DATE":
            temp = entity.text
            for punct in punc_list:
                if punct in temp:
                    temp = temp.replace(punct, " ")
            date_list.append(temp)
            for word in temp.split():       
                if text.find(word) > -1:
                    index = text.find(word)
                    x = 'x';
                    for n in range (len(word)-1):
                        x = x + 'x';             
                    text = text[:index] + x + text[index+len(x):]
    new_list = []
    new_list.append("D")

    token_list = []

    #sub the pii with uuid to pass it to chat gpt
    for pii_list in all_pii:
        if len(pii_list[1]) != 0:
            char = pii_list[0][0]
            for element in pii_list[1]:
                temp = []
                temp.append(char)
                temp.append(element)
                index = text3.find(element)
                str = uuid.uuid4() 
                temp.append(str.hex)
                text3 = text3[:index] + char + "-" + str.hex + text3[index+len(element):]
                token_list.append(temp)
                
        
    print(token_list)            
    #print("String with UUID pii: ")

    # TODO: Write to file
    
    return (text, token_list)
    

    

def replace(text):
    # new_text = replace_with_pii(text)
    # write to file 
    pass

#Database 

def database_creation():
    import snowflake.connector
    load_dotenv()
    SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")

    con_def = snowflake.connector.connect(user='BRENDANMORONEY',
                                        account='ydpcciy-xn91624',
                                        password =SNOWFLAKE_PASSWORD,
                                        database='PII_TOKENIZATION',        
                                        schema ='PUBLIC',
                                        autocommit=True)         

    db_cursor_def = con_def.cursor()

    db_cursor_def.execute("CREATE WAREHOUSE IF NOT EXISTS pii_warehouse")
    db_cursor_def.execute("USE WAREHOUSE pii_warehouse")

    db_cursor_def.execute("CREATE DATABASE IF NOT EXISTS PII_TOKENIZATION")
    db_cursor_def.execute("USE DATABASE PII_TOKENIZATION")

    db_cursor_def.execute("CREATE SCHEMA IF NOT EXISTS PUBLIC")
    db_cursor_def.execute("USE SCHEMA PII_TOKENIZATION.PUBLIC")

    #Creates table with PII_value, PII_type and ID

    db_cursor_def.execute("""CREATE OR REPLACE TABLE 
    PII_TOKENIZATION.PUBLIC.PII_Token_XREF (Token TEXT, PII_VALUE 
    VARCHAR(16777216),PII_TYPE VARCHAR(16777216), rec_created_date TIMESTAMP, 
    user_added TEXT, updated_date TIMESTAMP, PRIMARY KEY(Token))""")

    #Creates log table

    db_cursor_def.execute("""CREATE OR REPLACE TABLE PII_TOKENIZATION.PUBLIC.log 
    (time TIMESTAMP, user TEXT, document TEXT, PII_type TEXT, override 
    boolean)""")
                        
    #Practice insert
    #TODO when PII is matched to Token, add functionality to store and remove from database

    db_cursor_def.execute("INSERT INTO PII_Token_XREF(Token, PII_VALUE, PII_TYPE) VALUES('c2783f59-743e-403c-beac-21cb67076292','Rick Owens', 'N')")

    db_cursor_def.close()


if __name__ == "__main__":
    text = sys.argv[1]
    remove(text) if sys.argv[2] == "1" else replace(text)

