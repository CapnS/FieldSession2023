import { useRef, useState, useEffect } from 'react';
import Layout from '@/components/layout';
import styles from '@/styles/Home.module.css';
import { Message } from '@/types/chat';
import Image from 'next/image';
import ReactMarkdown from 'react-markdown';
import LoadingDots from '@/components/ui/LoadingDots';
import { Document } from 'langchain/document';
import http from 'http';

//SPIIT team imports
import { GetServerSideProps } from 'next';
import { parseCookies } from 'nookies';
import WarningPopUp from 'pages/warningPopUp';
import { name } from '../pages/logIn';

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';

export default function Home() {
  const [query, setQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [messageState, setMessageState] = useState<{
    messages: Message[];
    pending?: string;
    history: [string, string][];
    pendingSourceDocs?: Document[];
  }>({
    messages: [
      {
        message: 'Hi, what would you like to learn about this legal case?',
        type: 'apiMessage',
      },
    ],
    history: [],
  });

  const { messages, history } = messageState;

  const messageListRef = useRef<HTMLDivElement>(null);
  const textAreaRef = useRef<HTMLTextAreaElement>(null);

  const [warningVisible, setWarningVisible] = useState(false);
  //CREATE WARNING POP UP
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === '/') {
        setWarningVisible(true);
      }
    };
    window.addEventListener('keydown', handleKeyPress);

    // Clean up event listener on component unmount
    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, []);

  //handle form submission
  async function handleSubmit(e: any) {
    e.preventDefault();

    setError(null);

    if (!query) {
      alert('Please input a question');
      return;
    }

    let question = query.trim();

    // Log question using api/client endpoint
    await fetch('/api/clientAPI', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: `Question is : ${question}` }),
    });
    let basic = question;
    // similar to ingest we have to make a function that returns a promise in order to force the code
    // to remove the PII before sending the question to openai
    function sendRemoveRequest(): Promise<string> {
      return new Promise((resolve, reject) => {
      const options1 = {
        hostname: '127.0.0.1',
        port: 5000,
        path: '/remove',
        method: 'POST',
        headers: {
          'content-type': 'text/plain',
          'name': name // Set the user name
        }
      };
      console.log("NAME", name);
      const req1 = http.request(options1, (res) => {
        let response = '';
        res.on('data', (chunk) => {
          response += chunk;
        });
        res.on('end', () => {
          console.log(response); 
          question = response; // Set question to the response we get from our API
          resolve(response)
        });
      });
      req1.on('error', (error) => {
        console.error('Error:', error);
        reject(error)
      });
      
      req1.write(question);
      req1.end();
      
      // set the message state of the GUI to the non-tokenized question so the user doesn't
      // have to deal with tokens (this is just visuals and is not sent to openAI)
      setMessageState((state) => ({
        ...state,
        messages: [
          ...state.messages,
          {
            type: 'userMessage',
            message: basic,
          },
        ],
      }));
      setLoading(true);
      setQuery(''); 
    });
    }
    

    
    async function move_on(): Promise<any> {
      try {
        // get response from gpt
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question,
            history,
          }),
        });
        let data = await response.json();
        console.log('data', data);
        let tokenized = data.text;

        // as before, we have to make a function in order to stop the code from running until the output
        // is detokenized
        function sendReplaceRequest(): Promise<string> {
          
          return new Promise((resolve, reject) => {
          const options = {
            hostname: '127.0.0.1',
            port: 5000,
            path: '/replace', 
            method: 'POST',
            headers: {
              'Content-Type': 'text/plain'
            }
          };
        
          const req = http.request(options, (res) => {
            let response = '';
            res.on('data', (chunk) => {
              response += chunk;
            });
            res.on('end', () => {
              console.log(response); 
              data.text = response; // set the text to the response data
              resolve(response);
            });
          });
          req.on('error', (error) => {
            console.error('Error:', error);
            reject(error);
          });

          req.write(data.text);
          req.end();
          });
        }
        async function finish(): Promise<any> {
          if (data.error) {
            setError(data.error);
          } else {
            setMessageState((state) => ({
              ...state,
              messages: [
                ...state.messages,
                {
                  type: 'apiMessage',
                  message: data.text,
                  sourceDocs: data.sourceDocuments,
                },
              ],
              history: [...state.history, [question, tokenized]], // Here we set the history to have the tokenized form so future context that is sent
            }));                                                  // is still safe to send to openai
          }
          console.log('messageState', messageState);
  
          setLoading(false);
  
          //scroll to bottom
          messageListRef.current?.scrollTo(0, messageListRef.current.scrollHeight);
          } 

          // send the replace request and then finally finish and update the screen
          sendReplaceRequest()
          .then((responseData) => {
            finish();
          });
        }
      catch (error) {
        setLoading(false);
        setError('An error occurred while fetching the data. Please try again.');
        console.log('error', error);
      }
    }
    // send the remove request and then go to the move on function which gets a response from openai
    sendRemoveRequest()
    .then((responseData) => {
      move_on();
    });
  }

  //prevent empty submissions
  const handleEnter = (e: any) => {
    if (e.key === 'Enter' && query) {
      handleSubmit(e);
    } else if (e.key == 'Enter') {
      e.preventDefault();
    }
  };

  return (
    <>
      <Layout>
        <WarningPopUp isOpen={warningVisible} onClose={() => setWarningVisible(false)} />
        <div className="mx-auto flex flex-col gap-4">
          <h1 className="text-2xl font-bold leading-[1.1] tracking-tighter text-center">
            Chat With Your Legal Docs
          </h1>
          <main className={styles.main}>
            <div className={styles.cloud}>
              <div ref={messageListRef} className={styles.messagelist}>
                {messages.map((message, index) => {
                  let icon;
                  let className;
                  if (message.type === 'apiMessage') {
                    icon = (
                      <Image
                        key={index}
                        src="/bot-image.png"
                        alt="AI"
                        width="40"
                        height="40"
                        className={styles.boticon}
                        priority
                      />
                    );
                    className = styles.apimessage;
                  } else {
                    icon = (
                      <Image
                        key={index}
                        src="/usericon.png"
                        alt="Me"
                        width="30"
                        height="30"
                        className={styles.usericon}
                        priority
                      />
                    );
                    // The latest message sent by the user will be animated while waiting for a response
                    className =
                      loading && index === messages.length - 1
                        ? styles.usermessagewaiting
                        : styles.usermessage;
                  }
                  return (
                    <>
                      <div key={`chatMessage-${index}`} className={className}>
                        {icon}
                        <div className={styles.markdownanswer}>
                          <ReactMarkdown linkTarget="_blank">
                            {message.message}
                          </ReactMarkdown>
                        </div>
                      </div>
                      {message.sourceDocs && (
                        <div
                          className="p-5"
                          key={`sourceDocsAccordion-${index}`}
                        >
                          <Accordion
                            type="single"
                            collapsible
                            className="flex-col"
                          >
                            {message.sourceDocs.map((doc, index) => (
                              <div key={`messageSourceDocs-${index}`}>
                                <AccordionItem value={`item-${index}`}>
                                  <AccordionTrigger>
                                    <h3>Source {index + 1}</h3>
                                  </AccordionTrigger>
                                  <AccordionContent>
                                    <ReactMarkdown linkTarget="_blank">
                                      {doc.pageContent}
                                    </ReactMarkdown>
                                    <p className="mt-2">
                                      <b>Source:</b> {doc.metadata.source}
                                    </p>
                                  </AccordionContent>
                                </AccordionItem>
                              </div>
                            ))}
                          </Accordion>
                        </div>
                      )}
                    </>
                  );
                })}
              </div>
            </div>
            <div className={styles.center}>
              <div className={styles.cloudform}>
                <form onSubmit={handleSubmit}>
                  <textarea
                    disabled={loading}
                    onKeyDown={handleEnter}
                    ref={textAreaRef}
                    autoFocus={false}
                    rows={1}
                    maxLength={512}
                    id="userInput"
                    name="userInput"
                    placeholder={
                      loading
                        ? 'Waiting for response...'
                        : 'What is this legal case about?' 
                    }
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className={styles.textarea}
                  />
                  <button
                    type="submit"
                    disabled={loading}
                    className={styles.generatebutton}
                  >
                    {loading ? (
                      <div className={styles.loadingwheel}>
                        <LoadingDots color="#000" />
                      </div>
                    ) : (
                      // Send icon SVG in input field
                      <svg
                        viewBox="0 0 20 20"
                        className={styles.svgicon}
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"></path>
                      </svg>
                    )}
                  </button>
                </form>
              </div>
            </div>
            {error && (
              <div className="border border-red-400 rounded-md p-4">
                <p className="text-red-500">{error}</p>
              </div>
            )}
          </main>
        </div>
        <footer className="m-auto p-4">
          <a href="https://twitter.com/mayowaoshin">
            Powered by LangChainAI. Demo built by Mayo (Twitter: @mayowaoshin).
          </a>
        </footer>
      </Layout>
    </>
  );

}

export const getServerSideProps: GetServerSideProps = async (context) => {
  // Parse cookies from the incoming server request
  const cookies = parseCookies(context);

  // check the users login status using the isLoggedIN cookie
  if (cookies.isLoggedIn !== 'true') {
    // Else, redirect to '/login'
    return {
      redirect: {
        destination: '/logIn',
        permanent: false,
      },
    };
  }

  return {
    props: {},
  };
};
