import React, { useState } from 'react';
import CalculatorButton from './components/CalculatorButton';
import { create, all } from 'mathjs';

const math = create(all);
const App = () => {
    const [input, setInput] = useState('');

    const appendToInput = (val) => {
        setInput(input + val);
    };

    const evaluateInput = () => {
        try {
            setInput(math.evaluate(input).toString());
        } catch (error) {
            alert('Invalid Expression');
            setInput('');
        }
    };

    const clearInput = () => {
        setInput('');
    };

    return (
        <div className="bg-white bg-opacity-30 shadow-lg p-4 rounded-xl backdrop-blur-md w-80">
            <div className="bg-white bg-opacity-20 p-4 mb-4 rounded-lg h-12 text-right text-xl font-light text-white">
                {input}
            </div>
            <div className="grid grid-cols-4 gap-2">
                {[...Array(10).keys()].map(number => (
                    <CalculatorButton key={number} text={number} onClick={() => appendToInput(number)} />
                ))}
            </div>
            <CalculatorButton text="=" onClick={evaluateInput} />
            <CalculatorButton text="C" onClick={clearInput} />
        </div>
    );
};

export default App;
