import React, { useState } from 'react';
import './App.css';

const App = () => {
    const [count, setCount] = useState(0);
    
    const increment = () => {
        setCount(prevCount => prevCount + 1);
    };

    const decrement = () => {
        setCount(prevCount => prevCount - 1);
    };

    const reset = () => {
        setCount(0);
    };

    return (
        <div className="app-container">
            <h1>Simple Counter</h1>
            <div className="counter-display">
                <button onClick={decrement} className="counter-button" id="decrement">-</button>
                <span className="count-value">{count}</span>
                <button onClick={increment} className="counter-button" id="increment">+</button>
            </div>
            <button onClick={reset} className="reset-button" id="reset">Reset</button>
        </div>
    );
};

export default App;