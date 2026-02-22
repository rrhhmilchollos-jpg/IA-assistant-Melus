import React, { useState } from 'react';
import TodoList from './components/TodoList';
import './style.css';

function App() {
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState('all');

  const addTask = task => {
    if (task) {
      const newTask = { id: Date.now(), text: task, completed: false };
      setTasks([...tasks, newTask]);
    }
  };

  const deleteTask = id => {
    setTasks(tasks.filter(task => task.id !== id));
  };

  const completeTask = id => {
    setTasks(
      tasks.map(task =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };

  const filteredTasks = tasks.filter(task =>
    filter === 'completed' ? task.completed : filter === 'pending' ? !task.completed : task
  );

  return (
    <div className="App">
      <h1>Todo App</h1>
      <input type="text" placeholder="Add a new task" 
             onKeyDown={e => {
               if (e.key === 'Enter') {
                 addTask(e.target.value);
                 e.target.value = '';
               }
             }}
      />
      <TodoList tasks={filteredTasks} deleteTask={deleteTask} completeTask={completeTask} />
    </div>
  );
}

export default App;
