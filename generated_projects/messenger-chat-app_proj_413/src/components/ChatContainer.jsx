import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';

const socket = io('http://localhost:8000');

const ChatContainer = () => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    socket.on('receive_message', (data) => {
      setMessages((prevMessages) => [...prevMessages, data]);
    });

    return () => socket.disconnect();
  }, []);

  const sendMessage = () => {
    if (message.trim() !== '') {
      socket.emit('send_message', message);
      setMessages((prevMessages) => [...prevMessages, message]);
      setMessage('');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="h-96 overflow-y-scroll mb-4">
        {messages.map((msg, index) => (
          <div key={index} className="mb-2 bg-indigo-100 p-2 rounded-md">
            {msg}
          </div>
        ))}
      </div>
      <input
        type="text"
        className="border rounded w-full p-2"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <button onClick={sendMessage} className="mt-2 bg-blue-500 text-white p-2 rounded">
        Send
      </button>
    </div>
  );
};

export default ChatContainer;