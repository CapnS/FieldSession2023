import { OpenAI } from 'langchain/llms/openai';
import { PineconeStore } from 'langchain/vectorstores/pinecone';
import { ConversationalRetrievalQAChain } from 'langchain/chains';

const CONDENSE_PROMPT = `Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:`;

const QA_PROMPT = `You are a helpful AI assistant. Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say you don't know. DO NOT try to make up an answer.
If the question is not related to the context, politely respond that you are tuned to only answer questions that are related to the context.

The context you will be searching through has all personal information replaced with a token in the form A<<<064eee17382c47399e3dbefdeb587568>>> where A represents the type of personal information, and the information between the <<< and >>> represents the value of the personal information. 
Based on the character before the <<<, you will treat the information as follows: 
N represents a name, 
A represents an address, 
O represents an organization name, 
P represents a phone number, 
R represents a passport number, 
D represents a drivers license number, 
B represents an id number, 
S represents a social security number, 
I represents an IP address, 
C represents a credit card number, 
E represents an email, 
L represents a date,
and U represents an unlabeled piece of personal information. 
Please utilize the context when giving your responses, especially when it comes to names. 
For example, some people might have different tokens correlated to them. One for their first name and one for their full name, so make sure to use context clues to look out for this and treat those two tokens as the same person.
Make sure you never respond with just the character in place of one of these values, always give the full token in the correct form that I gave you above. 

{context}

Question: {question}
Helpful answer in markdown:`;

export const makeChain = (vectorstore: PineconeStore) => {
  const model = new OpenAI({
    temperature: 0, // increase temepreature to get more creative answers
    modelName: 'gpt-3.5-turbo', //change this to gpt-4 if you have access
  });

  const chain = ConversationalRetrievalQAChain.fromLLM(
    model,
    vectorstore.asRetriever(),
    {
      qaTemplate: QA_PROMPT,
      questionGeneratorTemplate: CONDENSE_PROMPT,
      returnSourceDocuments: true, //The number of source documents returned is 4 by default
    },
  );
  return chain;
};
