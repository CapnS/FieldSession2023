import snowflake
import sys
from nltk import tokenize
import nltk
import spacy
import phonenumbers
import re
import uuid
import PyPDF2
from transformers import pipeline
import snowflake.connector
from dotenv import load_dotenv
import os
from flask import Flask
from flask import request
from flask_cors import CORS



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
# E - Email
# L - Date




#model that worked the best with pdf 
#link to the hub that have banch of traned models, data sets, etc. if you want to check it out 
#https://huggingface.co/

def remove(text):

    ner_model = "dslim/bert-base-NER"

    punc_list = '''!()[]{};*:'"\,<>./?_~-'''
    #for dates as for right following patterns should be recognized: dd/mm/yyyy, dd.mm.yyyy, mm/dd/yyyy, mm.dd.yyyy, mm/yyyy, mm/yy, mm.yy,mm.yyyy 
    date_pattern = ["(0[1-9]|[12][0-9]|3[01])(\/|-)(0[1-9]|1[1,2])(\/|-)(19|20)\d{2}","(0[1-9]|1[1,2])(\/|-)(0[1-9]|[12][0-9]|3[01])(\/|-)(19|20)\d{2}", "^(19|20)\d{2}\/(0[1-9]|1[1,2])\/(0[1-9]|[12][0-9]|3[01])$", r"^(0[1-9]|1[0-2])[\/\.]\d{2}$", r"^(0[1-9]|1[0-2])[\./]\d{4}$" ]
    ssn_validate_pattern = "^(?!666|000|9\\d{2})\\d{3}-(?!00)\\d{2}-(?!0{4})\\d{4}$"
    email_validate_pattern = r"^\S+@\S+\.\S+$"
    ip_validate_pattern = "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
    mac_validate_pattern = "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})|([0-9a-fA-F]{4}\\.[0-9a-fA-F]{4}\\.[0-9a-fA-F]{4})$"
    passport_pattern_old = r"^[A-Z0-9]{9}$"
    passport_pattern_new = r"^[A-Z]\d{8}$"
    Dl_pattern = ["^[0-9]{7}$","^[A-Z]{1}[0-9]{8}$", "^[0-9]{9}", "^[0-9]{8}$", "^[A-Z]{1}[0-9]{7}$", "(^[A-Z]{1}[0-9]{3,6}$)|(^[A-Z]{2}[0-9]{2,5}$)", "^[A-Z]{1}[0-9]{12}$", "^[A-Z]{2}[0-9]{6}[A-Z]{1}$", "^[A-Z]{1}[0-9]{11,12}$","^[0-9]{10}", "^([0-9]{9}|([0-9]{3}[A-Z]{2}[0-9]{4}))$","^[A-Z]{2}[0-9]{6-7}$", "^[A-Z]{1}[0-9]{9-10}$", "(^[A-Z]{1}[0-9]{5,9}$)|(^[A-Z]{1}[0-9]{6}[R]{1}$)|(^[0-9]{3}[A-Z]{1}[0-9]{6}$)|(^[0-9]{8}[A-Z]{2}$)|(^[0-9]{9}[A-Z]{1}$)","(^[A-Z]{1}[0-9]{8}$)|(^[0-9]{13}$)|(^[0-9]{14}$)", "(^[0-9]{2}[A-Z]{3}[0-9]{5}$)|(^[A-Z]{3}[0-9]{8}$)","^[A-Z]{1}[0-9]{14}$","^[0-9]{12}$","^[A-Z]{3}[0-9]{6}$", "^[0-9]{7}[A-Z]$"]
    # we can add more cc types. So far we have amex, visa, and master card which can be detected either in the right format or with no spaces (Ex. 5123 4567 8901 2346, 5123456789012346)
    cc_validate_pattern = ["^3[47][0-9]{13}$", r"^(?:4\d{3}(\s\d{4}){3})$", "^4[0-9]{12}(?:[0-9]{3})?$", "^(5[1-5][0-9]{14}|2(22[1-9][0-9]{12}|2[3-9][0-9]{13}|[3-6][0-9]{14}|7[0-1][0-9]{13}|720[0-9]{12}))$", r"^3[47]\d{2}\s\d{6}\s\d{5}$", "^(?:5[1-5]\d{2}|222[1-9]|22[3-9]\d|2[3-6]\d{2}|27[01]\d|2720)\s\d{4}\s\d{4}\s\d{4}$", "^5[1-5]\d{2}\s\d{4}\s\d{4}\s\d{4}$", r"\b\d{4}\s\d{4}\s\d{4}\s\d{4}\b"]
    # following patterns should be recognized based on phone numbers: +1(123)987-6543,+1-555-987-6543,+1234567896,123-456-7890,(123)456-7890,123.456.7890,1234567890,1-123-456-6789,1 (123) 345-6789, 1 123 456 7890
    phone_pattern = [r"^\+1 \(\d{3}\) \d{3}-\d{4}$","^\+1-\d{3}-\d{3}-\d{4}$","^\+?\d{11}$", "^\d{3}-\d{3}-\d{4}$", "^\(\d{3}\) \d{3}-\d{4}$", "^\d{3}\.\d{3}\.\d{4}$", "^\d{10}$", "^1-\d{3}-\d{3}-\d{4}$", "^1 \(\d{3}\) \d{3}-\d{4}$","^1 \d{3} \d{3} \d{4}$",  r"^\+1\s+\d{3}\s+\d{3}\s+\d{4}$", r"^\+1\s\s\d{3}\s\s\d{3}\s\d{4}$"]
    
    #read pdf and store it as a string 
    #p = open('Invoice  with lots of Passport Numbers, names, ssns, and drivers license numbers.pdf', 'rb')
    #pdf = PyPDF2.PdfReader(p)
    #text = pdf.pages[0].extract_text() + "\n"
    #text = " ".join(text.replace(u"\xa0", " ").strip().split())

    

    text5 = text 
    text2 = text 
    text4 = text 

    dir_path = os.path.dirname(os.path.realpath(__file__))
    pd = open(os.path.join(dir_path,'dependencies','names dataset.pdf'), 'rb')
    pdf = PyPDF2.PdfReader(pd)
    num_pages = len(pdf.pages)
    names_dataset = ""
    for i in range(num_pages):
        page = pdf.pages[i]
        names_dataset += page.extract_text()

    pd.close()

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
    dl_list = []
    all_pii = []

      # extract punctuation for better performance of the libraries 
    for i in text5:
        if i in punc_list:
            text5 = text5.replace(i, " ")

    for format in cc_validate_pattern:
        while re.search(format,text5):
            matches = re.findall(format, text5)
            for match in matches:
                temp = match
                temp2 = temp.replace(" ", "")
                # append cc to list 
                while temp in text3:
                    text3 = text3.replace(temp, temp2)
                if temp2 not in cc_list:
                    cc_list.append(temp2)
                    x = 'x'
                    for n in range (len(temp)-1):
                        x = x + 'x'; 
                        text = text.replace(temp, x)
                    x = 'x'
                    for n in range (len(temp2)-1):
                        x = x + 'x'; 
                        text5 = text5.replace(temp, x)
                    

    # detect cc with no spaces between and replace it with xxx
    for word in text.split():
        if word[-1] in punc_list:
            word = word.rstrip(punc_list)
        for format in cc_validate_pattern:
            if (re.match(format, word)):
            # append cc to list 
                if word not in cc_list:
                    cc_list.append(word)
                    x = 'x'
                    for n in range (len(word)-1):
                        x = x + 'x'; 
                    text = text.replace(word, x)
    
            

            
        
        
    new_list = []
    new_list.append("C")
    new_list.append(cc_list)
    all_pii.append(new_list)
    
    # extract punctuation for better performance of the libraries 
    for i in text4:
        if i in punc_list:
            if i == '.':
                text4 = text4.replace(i, " ")
            else:
                text4 = text4.replace(i, "")

    # detect passport number and replace it with xxx
    # only new passports have a format that is unique from other piis 
    for word in text4.split():
        #edge case: make sure that there is no punctuation after the passport number; otherwise, it will not be detected
        if word[-1] in punc_list:
            word = word.rstrip(punc_list)
        if (re.match(passport_pattern_new, word)):
            if word not in passport_list:
                passport_list.append(word)
                x = 'x';
                for n in range (len(word)-1):
                    x = x + 'x'; 
                text = text.replace(word, x)

    # detect ssn and replace it with xxx
    for word in text.split():
        
        #edge case: make sure that there is no punctuation after the ssn; otherwise, it will not be detected
        #all the punctuation can not be extracted at this point because "-" are part of the ssn
        if word[-1] in punc_list:
            word = word.rstrip(punc_list)
        if (re.match(ssn_validate_pattern, word)):
            # append ssn to ssn_list
            if word not in ssn_list:
                ssn_list.append(word)
                start_ind = text.find(word)
                x = ''         
                for char in word:
                    if char != '-':
                        x = x + 'x'
                    else: 
                        x = x + '-'                       
            text = text.replace(word,x)

        
    new_list = []
    new_list.append("S")
    new_list.append(ssn_list)
    all_pii.append(new_list)        
            

    #load text in nlp
    ner = pipeline("ner", model=ner_model, grouped_entities=True)
    output = ner(text)

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
                
            # Find the previous word and check if it is numeric to identify if it is part of the address 
            previous_word = text.rfind(" ", 0, start_ind-1)

            # Extract the previous word using string slicing
            p_word = text[previous_word + 1:start_ind-1]
            isDigit = True
            for x in p_word:
                if x.isdigit() == False:
                    isDigit == False
            # if it is numeric combine with the rest of address 
            if isDigit and len(p_word) < 5:
                start_ind = previous_word + 1
                temp = p_word + " " + temp 
            if temp not in address_list:
                address_list.append(temp)
            #mask it with xxx for testing purposes 
            x = ''          
            for char in temp:
                if char != ' ':
                    x = x + 'x'
                else: 
                    x = x + ' '                      
            text = text[:start_ind ] + x + text[start_ind+len(x):]

        
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
            if end_ind < len(text):
                if not text[end_ind].isspace() and text[end_ind] not in punc_list:
                    end_ind = text.find(" ", end_ind)
                    temp = text[start_ind:end_ind]
                if temp not in people_list:
                    people_list.append(temp)
                    #mask it with xxx for testing purposes                    
                    x = ''         
                    for char in temp:
                        if char != ' ':
                            x = x + 'x'
                        else: 
                            x = x + ' '                       
                    text = text[:start_ind] + x + text[start_ind+len(x):]
                    
        elif entity_label == "MISC":
            # check if the word is complete since the model sometimes tempts to grab just the beginning of the name 
            temp = entity_group["word"]

            start_ind = text.find(temp)
            end_ind = start_ind + len(temp)
            if not text[end_ind].isspace() and text[end_ind] not in punc_list:
                end_ind = text.find(" ", end_ind)
                temp = text[start_ind:end_ind]
            if temp not in undefined:
                undefined.append(temp)

        elif entity_label == "ORG":
            temp = entity_group["word"]
            if temp not in org_list:
                org_list.append(temp)
            start_ind = text.find(temp)
            x = ''         
            for char in temp:
                if char != ' ':
                    x = x + 'x'
                else: 
                    x = x + ' '                       
            text = text[:start_ind] + x + text[start_ind+len(x):]
                
    
    
    # this is a second layer that checks if the names that were detected are in the dataset of 10 000 common names that we have created       
    for name in people_list:
        first = name.split()
        if first[0] not in names_dataset:
            people_list.remove(name)
    
    
    # check if any names were appended into undefined list, pop it from there and move it to the list of names 
    for word in undefined:
        first = word.split()
        if first[0] in names_dataset:
            undefined.remove(word)
            people_list.append(word)
        if word.isdigit() == False and word in undefined:
            undefined.remove(word)

    for word in undefined:
        start_ind = text.find(word)
        #mask it with xxx for testing purposes                    
        x = ''         
        for char in word:
            if char != ' ':
                x = x + 'x'
            else: 
                x = x + ' '                       
        text = text[:start_ind] + x + text[start_ind+len(x):]
        
             
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

                
    # detect dl and replace it with xxx
    for word in text.split():
        #edge case: make sure that there is no punctuation after the dl; otherwise, it will not be detected
        if word[-1] in punc_list:
            word = word.rstrip(punc_list)
        for format in Dl_pattern:
            if (re.match(format, word)):
            # append dl to dl_list
                if word not in dl_list:
                    dl_list.append(word)
                    x = 'x';
                    for n in range (len(word)-1):
                        x = x + 'x'; 
                    text = text.replace(word, x)
    
            
                
                
    # The code below will handle all the pii that NLP did not detect
    #--------------------------------------------------------------------
    # Extract sentences that have keywords and insert them into new_list 

    new_list = []
    tok_text = tokenize.sent_tokenize(text)
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
        for i in sentence:
            if i in punc_list:
                if i == '.' or i == '-':
                    sentence = sentence.replace(i, " ")
                else:
                    sentence = sentence.replace(i, "")
        sentence_list = []
        #check if there is only one type of the document mentioned in the sentence 
        #if there id more than one, the pii will go into undefined list
        one_type = 0
        character = 'A'
        # assign char depending on the type of pii
        for word in id_words:
            if word.lower() in sentence.lower():
                one_type = one_type + 1
                character = 'B'
        for word in dl_words:
            if word.lower() in sentence.lower():
                one_type = one_type + 1
                character = 'D'
        #trace the the numeric pii 
        for word in sentence.split():
            isDigit = False
            for char in word:
                if char.isdigit() == True:
                    isDigit = True; 
            if isDigit == True and len(word) > 5 and word[0] != "$":
                # sometimes it will grab pii with punctuation, so we need to make sure to get rid of it before passing into the list 
                if word[-1] in punc_list:
                    word = word.rstrip(punc_list)
                if one_type == 1 and character == 'D':
                    if word not in dl_list:
                        dl_list.append(word)
                        start_ind = text.find(word)
                        x = ''
                        for char in word:
                            if char != '-':
                                x = x + 'x'
                            else: 
                                x = x + '-'                       
                    text = text.replace(word,x)
                else:
                    if word not in undefined:
                        undefined.append(word)
                #replace pii with xxx
                #if text.find(word) > -1:
                #    index = text.find(word)
                #    x = 'x';
                #    for n in range (len(word)-1):
                #        x = x + 'x';             
                #    text = text[:index] + x + text[index+len(x):]
        if len(sentence_list) > 0 :
            clean_undetected_list.append(sentence_list)
    #if len(clean_undetected_list) > 0:
        #all_pii.append(clean_undetected_list)

    for pii in undefined:
        if pii in dl_list:
            undefined.remove(pii)

    new_list = []
    new_list.append("D")
    new_list.append(dl_list)
    all_pii.append(new_list)    
    

    # detect phone numbers and replace them with xxx       
    for match in phonenumbers.PhoneNumberMatcher(text, "US"):
        for word in text.split():
            if word[-1] in punc_list:
                word = word.rstrip(punc_list)
            if word == match.raw_string:
            #append phone numbers to phone_list
                if word not in phone_list:
                    phone_list.append(word)
                    x = 'x';
                    for n in range (len(word)-1):
                        x = x + 'x'; 
                    text = text.replace(word, x)
    for format in phone_pattern:
        #while re.search(format, text5):
        matches = re.findall(format, text5)
        for match in matches:               
            temp = match
            # append phone to list 
            if temp not in phone_list:
                phone_list.append(temp)
                x = 'x'
                for n in range (len(temp)-1):
                    x = x + 'x'; 
                    text = text.replace(temp, x)
              
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
                word = word.rstrip(punc_list)
            if word not in email_list:
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
            if word not in ip_list:
                ip_list.append(word)
                x = 'x';
                for n in range (len(word)-1):
                    x = x + 'x'; 
                
                text = text.replace(word, x)

    new_list = []
    new_list.append("I")
    new_list.append(ip_list)
    all_pii.append(new_list)


    #second nlp that we are using for dates 
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)            
    
    # using spacy library to detect dates
    for entity in doc.ents:
        if entity.label_ == "DATE":
            temp = entity.text
            #for punct in punc_list:
            #    if punct in temp:
            #        temp = temp.replace(punct, " ")
            # nlp considers anything assosiated with time as a date: yesterday, a year ago, etc.
            # so we should only extract elements that have some kind of numeric val 
            isDigit = False
            for x in temp:
                if x.isdigit() :
                   isDigit = True;    
            if isDigit == True:  
                date_list.append(temp)
                for word in temp.split():       
                    if text.find(word) > -1:
                        index = text.find(word)
                        x = 'x';
                        for n in range (len(word)-1):
                            x = x + 'x';             
                        text = text[:index] + x + text[index+len(x):]
    for word in text3.split():
        #edge case: make sure that there is no punctuation after the 
        if word[-1] in punc_list:
            word = word.rstrip(punc_list)
        for format in date_pattern:
            if (re.match(format, word)):
            # append date 
                if word not in date_list:
                    date_list.append(word)
                

    new_list = []
    new_list.append("L")
    new_list.append(date_list)
    
    
    
    # We have to figure out what to do with dates; we will probably just have to manually check if they match the format of the DOB because we don't 
    # need to tokenize all the dates 

    all_pii.append(new_list)
    print(all_pii)

    token_list = []
    seen = []
    #sub the pii with uuid to pass it to chat gpt

    for pii_list in all_pii:
        if len(pii_list[1]) != 0:
            char = pii_list[0][0]
            
            for element in pii_list[1]:
                if not element:
                    continue
                temp = []
                temp.append(char)
                temp.append(element)
                #CHECK TO SEE IF PII ALREADY IN DATABASE (IF SO, USE STORED TOKEN INSTEAD OF MAKING NEW ONE)
                if(db_cursor_def.execute("SELECT PII_VALUE FROM PII_TOKEN_XREF WHERE PII_VALUE = %s", element).fetchone()):
                    token = db_cursor_def.execute("SELECT Token FROM PII_TOKEN_XREF WHERE PII_VALUE = %s", element).fetchone()[0]
                else:
                    token = uuid.uuid4().hex
                temp.append(token)
                token_list.append(temp)
                
                
                # While the pii is still in the text, keep replacing it with the token
                while element in text3:
                    index = re.search(re.escape(element), text3)
                    if index is not None:
                        index = index.start()
                        text3 = text3[:index] + char + "<<<" + token + ">>>" + text3[index + len(element):]
                    else:
                        break
  

    # Writing to File
    #dir_path = os.path.dirname(os.path.realpath(__file__))
    #with open(os.path.join(dir_path, 'updatedFiles/tokenized_output.txt'), 'w') as file:
    #   file.write(text3)

    #LOOP THROUGH LIST AND UPLOAD ALL TOKENS TO DATABASE HERE
    print(token_list)
    for token in token_list:
        if not(db_cursor_def.execute("SELECT PII_VALUE FROM PII_TOKEN_XREF WHERE PII_VALUE = %s", element).fetchall()):    
            db_cursor_def.execute("INSERT INTO PII_Token_XREF(Token, PII_VALUE, PII_TYPE) VALUES(%s, %s, %s)", (token[2], token[1], token[0]))
    return (text, token_list, text3)


    

def replace(text):
    new_text = text
    for word in text.split(' '):
        # search for our token in the word
        match = re.search(r'[A-Z]<<<[a-z0-9]{32}>>>', word)
        if match:
            # if there is a match, single out the token and the actual part of the word to replace
            token = word[match.start()+4:match.end()-3]
            to_replace = word[match.start():match.end()]
            #if it's found in the database, set pii to that value, else continue
            try:
                pii = db_cursor_def.execute("SELECT PII_VALUE FROM PII_TOKEN_XREF WHERE TOKEN = %s", token).fetchone()[0]
            except:
                print("Token not found in database.")
                continue
            # Find the token in the text and replace it with the pii
            index = new_text.find(to_replace)
            new_text = new_text[:index] + pii + new_text[index+len(to_replace):]


    # Writing to File
    #dir_path = os.path.dirname(os.path.realpath(__file__))
    #with open(os.path.join(dir_path, 'updatedFiles/detokenized_output.txt'), 'w') as file:
    #    file.write(new_text)
    return new_text


#TODO: Write function to initialize snowflake connection and databases
#Database 

def database_creation():
    load_dotenv()
    SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")

    con_def = snowflake.connector.connect(user='BRENDANMORONEY',
                                       account='ydpcciy-xn91624',
                                        password =SNOWFLAKE_PASSWORD,
                                        database='PII_TOKENIZATION',        
                                        schema ='PUBLIC',
                                        autocommit=True)         

    global db_cursor_def 
    db_cursor_def = con_def.cursor()
    '''
    db_cursor_def.execute("CREATE WAREHOUSE IF NOT EXISTS pii_warehouse")
    db_cursor_def.execute("USE WAREHOUSE pii_warehouse")

    db_cursor_def.execute("CREATE DATABASE IF NOT EXISTS PII_TOKENIZATION")
    db_cursor_def.execute("USE DATABASE PII_TOKENIZATION")

    db_cursor_def.execute("CREATE SCHEMA IF NOT EXISTS PUBLIC")
    db_cursor_def.execute("USE SCHEMA PII_TOKENIZATION.PUBLIC")

    #Creates table with PII_value, PII_type and ID

    
     db_cursor_def.execute("""CREATE TABLE IF NOT EXISTS
    PII_TOKENIZATION.PUBLIC.PII_Token_XREF (Token TEXT, PII_VALUE 
    TEXT,PII_TYPE VARCHAR(16777216), rec_created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    user_added TEXT, updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(Token))""")

    #Creates log table

    db_cursor_def.execute("""CREATE TABLE IF NOT EXISTS PII_TOKENIZATION.PUBLIC.log 
    (time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, user TEXT, document TEXT, PII_type TEXT, override 
    boolean)""")
    '''
    
    


database_creation()

# This code runs the api and also prints out what is going on for debugging and demo purposes
app = Flask(__name__)
# This allows our api to be used by another webpage which is necessary for our use case
CORS(app)

# Replace API route
@app.route("/replace")
def replace_pii():
    print("Replacing", request.headers['text'])
    replaced = replace(request.headers['text'])
    print(replaced)
    return replaced

# Remove API route
@app.route("/remove")
def remove_pii():
    print("Removing", request.headers['text'])
    removed = remove(request.headers['text'])[2]
    print(removed)
    return removed

# Default API route that lets the user know their code is working
@app.route("/")
def hello():
    return "Hello, your api is running!"

