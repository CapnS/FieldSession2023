import React, { useState } from 'react';
import Modal from 'react-modal';

interface WarningPopUpProps {
    isOpen: boolean;
    onClose: () => void;
}

const WarningPopUp: React.FC<WarningPopUpProps> = ({ isOpen, onClose }) => {
    const [badTokens, setBadTokens] = useState([
        'Example Token 1',
        'Example Token 2',
        'Example Token 3',
        'Example Token 4',
        'Example Token 5',
        'Example Token 6',
        'Example Token 7',
    ]);
    const [showTokens, setShowTokens] = useState(false); // New state variable

    const revealTokens = () => {
        setShowTokens(!showTokens); // Toggle the visibility of tokens
    };

    return (
        <Modal
            isOpen={isOpen}
            onRequestClose={onClose}
            contentLabel="Warning"
            style={{
                overlay: {
                    backgroundColor: 'rgba(0,0,0,0.5)',
                },
                content: {
                    color: 'black',
                    width: '400px',
                    height: '300px',
                    margin: 'auto',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '20px',
                },
            }}
        >
            <h2 style={{ textAlign: 'center' }}>
                Certain personalized data has failed to be scrubbed and censored
            </h2>
            <button
                onClick={revealTokens}
                style={{
                    backgroundColor: 'white',
                    border: '1px solid black',
                    color: 'black',
                    padding: '10px 32px',
                    textAlign: 'center',
                    textDecoration: 'none',
                    display: 'inline-block',
                    fontSize: '16px',
                    margin: '4px 2px',
                    cursor: 'pointer',
                }}
            >
                {showTokens ? 'Hide Redacted' : 'Reveal Redacted'}
            </button>
            {showTokens && ( // Show the tokens only if showTokens is true
                <div
                    style={{
                        overflowY: 'scroll',
                        maxHeight: '100px',
                        width: '100%',
                        border: '1px solid black',
                        padding: '10px',
                        marginBottom: '20px',
                        textAlign: 'center',
                    }}
                >
                    {badTokens.map((token, index) => (
                        <p key={index}>{token}</p>
                    ))}
                </div>
            )}
            <div
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    width: '100%',
                }}
            >
                <button
                    onClick={onClose}
                    style={{
                        backgroundColor: 'white',
                        border: '1px solid black',
                        color: 'black',
                        padding: '10px 32px',
                        textAlign: 'center',
                        textDecoration: 'none',
                        display: 'inline-block',
                        fontSize: '16px',
                        margin: '4px 2px',
                        cursor: 'pointer',
                    }}
                >
                    Go Back
                </button>
                <button
                    onClick={onClose}
                    style={{
                        backgroundColor: 'white',
                        border: '1px solid black',
                        color: 'black',
                        padding: '10px 32px',
                        textAlign: 'center',
                        textDecoration: 'none',
                        display: 'inline-block',
                        fontSize: '16px',
                        margin: '4px 2px',
                        cursor: 'pointer',
                    }}
                >
                    Continue Anyways
                </button>
            </div>
        </Modal>
    );
};

export default WarningPopUp;
