import React from 'react';
import ChatContainer from '../components/ChatContainer';

const HomePage = () => {
  return (
    <div className="mt-10 text-center">
      <h1 className="text-4xl font-bold mb-6">Welcome to Messenger Chat</h1>
      <ChatContainer />
    </div>
  );
};

export default HomePage;