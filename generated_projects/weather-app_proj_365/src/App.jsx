import React, { useState } from 'react';
import Weather from './components/Weather';

const App = () => {
  const [city, setCity] = useState('');

  return (
    <div className="text-center">
      <h1 className="text-3xl font-bold mb-4">Weather App</h1>
      <input 
        type="text"
        placeholder="Enter city name"
        value={city}
        onChange={(e) => setCity(e.target.value)}
        className="p-2 border rounded mb-4 w-full"
      />
      <Weather city={city} />
    </div>
  );
};

export default App;