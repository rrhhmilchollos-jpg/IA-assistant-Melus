import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Weather = ({ city }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!city) return;
    const fetchWeather = async () => {
      setLoading(true);
      try {
        const response = await axios.get(
          `https://api.openweathermap.org/data/2.5/weather?q=${city}&units=metric&appid=YOUR_API_KEY`
        );
        setData(response.data);
      } catch (err) {
        setError(err);
      }
      setLoading(false);
    };
    fetchWeather();
  }, [city]);

  if (loading) return <p className="text-xl">Loading...</p>;
  if (error) return <p className="text-xl text-red-500">Error loading weather</p>;
  if (!data) return <p className="text-xl">Enter a city to get weather</p>;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">{data.name}</h2>
      <p className="text-lg">Temperature: {data.main.temp}°C</p>
      <p className="text-lg">Humidity: {data.main.humidity}%</p>
      <p className="text-lg">Wind Speed: {data.wind.speed} km/h</p>
      <img src={`http://openweathermap.org/img/wn/${data.weather[0].icon}@2x.png`} alt="Weather Icon" className="mx-auto" />
    </div>
  );
};

export default Weather;