import React from 'react';

const CalculatorButton = ({ text, onClick, className }) => {
    return (
        <button 
            className={`bg-white bg-opacity-25 rounded-lg py-2 font-semibold text-white shadow-md hover:bg-opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`} 
            onClick={onClick}>
            {text}
        </button>
    );
};

export default CalculatorButton;