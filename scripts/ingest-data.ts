import { RecursiveCharacterTextSplitter } from 'langchain/text_splitter';
import { OpenAIEmbeddings } from 'langchain/embeddings/openai';
import { PineconeStore } from 'langchain/vectorstores/pinecone';
import { pinecone } from '@/utils/pinecone-client';
import { CustomPDFLoader } from '@/utils/customPDFLoader';
import { PINECONE_INDEX_NAME, PINECONE_NAME_SPACE } from '@/config/pinecone';
import { DirectoryLoader } from 'langchain/document_loaders/fs/directory';
import { stringify } from 'querystring';
import http from 'http';
import logger from '../utils/logger';  
import * as path from 'path';

/* Name of directory to retrieve your files from */
const filePath = 'docs';

export const run = async () => {
  try {
    /*load raw docs from the all files in the directory */
    const directoryLoader = new DirectoryLoader(filePath, {
      '.pdf': (path) => new CustomPDFLoader(path),
    });

    // const loader = new PDFLoader(filePath);
    let rawDocs = await directoryLoader.load();

    // Here we make a function that returns a promise in order to force our pii removal to finish before
    // it is uploaded to the Pinecode Index
    function sendRequest(): Promise<string> {
      return new Promise((resolve, reject) => {
      
      // for each document, send an API request to our localhost API that will remove PII
      rawDocs.forEach((doc) => {
      const options1 = {
        hostname: '127.0.0.1',
        port: 5000,
        path: '/remove', 
        method: 'GET',
        headers: {
          'content-type': 'text/plain', 
          'text': doc.pageContent.replace(/\r?\n|\r/g, '') // Set the text to be replaced
        }
      };
    
      const req1 = http.request(options1, (res) => {
        let response = '';
        res.on('data', (chunk) => {
          response += chunk;
        });
        res.on('end', () => {
          console.log('response', response); 
          doc.pageContent = response; // Set the page content to the tokenized data
          resolve(response);
        });
      });
      req1.on('error', (error) => {
        console.error('Error:', error);
        reject(error);
      });
    
      req1.end();
      
    });
    });
  }
  async function keep_going(): Promise<any> {
    /* Split text into chunks */
    const textSplitter = new RecursiveCharacterTextSplitter({
      chunkSize: 1000,
      chunkOverlap: 200,
    });
    
    
    const docs = await textSplitter.splitDocuments(rawDocs);
    console.log('split docs', docs);

    console.log('creating vector store...');
    /*create and store the embeddings in the vectorStore*/
    const embeddings = new OpenAIEmbeddings();
    const index = pinecone.Index(PINECONE_INDEX_NAME); //change to your own index name


    // Log the source string for each document with timestamp
    console.log('Creating loggable event...');
    docs.forEach(doc => {
      const fileName = path.basename(doc.metadata.source);
      const timestamp = new Date().toISOString();
      logger.info(`Document source: ${fileName} - Timestamp: ${timestamp}`);
    });


    //embed the PDF documents
    await PineconeStore.fromDocuments(docs, embeddings, {
      pineconeIndex: index,
      namespace: PINECONE_NAME_SPACE,
      textKey: 'text',
    });
  
  };
  // call our request function and then call the keep going function, this ensures that the correct data is sent
  sendRequest()
  .then((responseData) => {
    console.log('raw docs', rawDocs);
    keep_going();
  });


} catch (error) {
  console.log('error', error);
  throw new Error('Failed to ingest your data');
}
};

(async () => {
  await run();
  console.log('ingestion complete00');
})();