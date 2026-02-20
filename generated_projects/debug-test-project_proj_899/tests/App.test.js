import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../src/App';

test('renders welcome message', () => {
  render(<App />);
  const linkElement = screen.getByText(/Welcome to the Debug Test Project/i);
  expect(linkElement).toBeInTheDocument();
});
