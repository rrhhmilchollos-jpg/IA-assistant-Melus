import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Task from './Task';
import TaskFilter from './TaskFilter';

const TaskManager = () => {
  const [tasks, setTasks] = useState(() => {
    const savedTasks = localStorage.getItem('tasks');
    return savedTasks ? JSON.parse(savedTasks) : [];
  });
  const [filter, setFilter] = useState('all');
  const [newTask, setNewTask] = useState('');

  useEffect(() => {
    localStorage.setItem('tasks', JSON.stringify(tasks));
  }, [tasks]);

  const addTask = () => {
    if (newTask.trim()) {
      setTasks([...tasks, { text: newTask.trim(), completed: false }]);
      setNewTask('');
    }
  };

  const toggleTaskCompletion = (index) => {
    const updatedTasks = tasks.map((task, idx) => 
      idx === index ? { ...task, completed: !task.completed } : task
    );
    setTasks(updatedTasks);
  };

  const deleteTask = (index) => {
    setTasks(tasks.filter((_, idx) => idx !== index));
  };

  const filterTasks = (status) => {
    setFilter(status);
  };

  const filteredTasks = tasks.filter(task => {
    if (filter === 'completed') return task.completed;
    if (filter === 'active') return !task.completed;
    return true;
  });

  return (
    <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-6">
      <motion.h1 className="text-2xl font-bold mb-4">Task Manager</motion.h1>
      <div className="flex mb-4">
        <input
          type="text"
          value={newTask}
          onChange={e => setNewTask(e.target.value)}
          placeholder="Add a new task"
          className="border flex-grow p-2 rounded-l"
        />
        <button
          onClick={addTask}
          className="bg-blue-500 text-white p-2 rounded-r"
        >Add</button>
      </div>
      <TaskFilter filter={filter} setFilter={filterTasks} />
      <ul>
        {filteredTasks.map((task, index) => (
          <Task 
            key={index} 
            task={task} 
            index={index} 
            toggleTaskCompletion={toggleTaskCompletion} 
            deleteTask={deleteTask}
          />
        ))}
      </ul>
    </div>
  );
};

export default TaskManager;