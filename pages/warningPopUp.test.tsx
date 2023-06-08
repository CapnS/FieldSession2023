import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import WarningPopUp from 'pages/warningPopUp';

describe('WarningPopUp component', () => {
  // Test Case: Initial State
  test('should not display the modal when isOpen is false', () => {
    const { queryByText } = render(<WarningPopUp isOpen={false} onClose={() => {}} />);
    const modalTitle = queryByText('Certain personalized data has failed to be scrubbed and censored');
    expect(modalTitle).not.toBeInTheDocument();
  });

  // Test Case: Modal Open
  test('should display the modal when isOpen is true', () => {
    const { getByText } = render(<WarningPopUp isOpen={true} onClose={() => {}} />);
    const modalTitle = getByText('Certain personalized data has failed to be scrubbed and censored');
    expect(modalTitle).toBeInTheDocument();
  });

  // Test Case: Modal Close
  test('should call the onClose function when modal is closed', () => {
    const onCloseMock = jest.fn();
    const { getByText } = render(<WarningPopUp isOpen={true} onClose={onCloseMock} />);
    const goBackButton = getByText('Go Back');
    fireEvent.click(goBackButton);
    expect(onCloseMock).toHaveBeenCalled();
  });

  // Test Case: Reveal Tokens
  test('should reveal redacted tokens when "Reveal Redacted" button is clicked', () => {
    const { getByText, queryByText } = render(<WarningPopUp isOpen={true} onClose={() => {}} />);
    const revealButton = getByText('Reveal Redacted');
    fireEvent.click(revealButton);
    const token1 = queryByText('Example Token 1');
    expect(token1).toBeInTheDocument();
  });

  // Test Case: Hide Tokens
  test('should hide redacted tokens when "Hide Redacted" button is clicked', () => {
    const { getByText, queryByText } = render(<WarningPopUp isOpen={true} onClose={() => {}} />);
    const revealButton = getByText('Reveal Redacted');
    fireEvent.click(revealButton);
    fireEvent.click(revealButton);
    const token1 = queryByText('Example Token 1');
    expect(token1).not.toBeInTheDocument();
  });

  // Test Case: Go Back Button
  test('should call the onClose function when "Go Back" button is clicked', () => {
    const onCloseMock = jest.fn();
    const { getByText } = render(<WarningPopUp isOpen={true} onClose={onCloseMock} />);
    const goBackButton = getByText('Go Back');
    fireEvent.click(goBackButton);
    expect(onCloseMock).toHaveBeenCalled();
  });

  // Test Case: Continue Anyways Button
  test('should call the onClose function when "Continue Anyways" button is clicked', () => {
    const onCloseMock = jest.fn();
    const { getByText } = render(<WarningPopUp isOpen={true} onClose={onCloseMock} />);
    const continueButton = getByText('Continue Anyways');
    fireEvent.click(continueButton);
    expect(onCloseMock).toHaveBeenCalled();
  });
});
