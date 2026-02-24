import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './styles/tailwind.output.css';

// Ensure Tailwind CSS output file is correctly linked

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);