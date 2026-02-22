import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Home from './pages/Home';
import ChatRoom from './pages/ChatRoom';
import Profile from './pages/Profile';

function App() {
  return (
    <Router>
      <Switch>
        <Route path="/" exact component={Home} />
        <Route path="/chatroom" component={ChatRoom} />
        <Route path="/profile" component={Profile} />
      </Switch>
    </Router>
  );
}

export default App;
