import React, { useState } from 'react';

const App = () => {
    const [count, setCount] = useState(0);

    const increment = () => {
        setCount(count + 1);
    };

    const decrement = () => {
        setCount(count - 1);
    };

    return (
        <div className="max-w-xs mx-auto bg-white shadow rounded-lg p-5">
            <h1 className="text-2xl font-bold text-center mb-5">Simple Counter</h1>
            <div className="flex justify-around items-center">
                <button 
                    onClick={decrement} 
                    className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">
                    -
                </button>
                <span className="text-xl font-mono">{count}</span>
                <button 
                    onClick={increment} 
                    className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
                    +
                </button>
            </div>
        </div>
    );
};

export default App;