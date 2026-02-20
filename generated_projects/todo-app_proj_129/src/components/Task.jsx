import React from 'react';
import { motion } from 'framer-motion';

const Task = ({ task, index, toggleTaskCompletion, deleteTask }) => {
  return (
    <motion.li 
      initial={{ opacity: 0, x: 100 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -100 }}
      layout
      className="flex items-center justify-between p-2 border-b"
    >
      <span
        onClick={() => toggleTaskCompletion(index)}
        className={`cursor-pointer ${task.completed ? 'line-through text-gray-500' : ''}`}
      >
        {task.text}
      </span>
      <button
        onClick={() => deleteTask(index)}
        className="text-red-500 hover:text-red-700"
      >
        Delete
      </button>
    </motion.li>
  );
};

export default Task;