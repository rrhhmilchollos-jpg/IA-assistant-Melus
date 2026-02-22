import React from 'react';

const TodoItem = ({ task, deleteTask, completeTask }) => {
  return (
    <li className={`todo-item ${task.completed ? 'completed' : ''}`}>
      <span
        className="todo-task"
        onClick={() => completeTask(task.id)}
        style={{ textDecoration: task.completed ? 'line-through' : 'none' }}>
        {task.text}
      </span>
      <button className="delete-button" onClick={() => deleteTask(task.id)}>Delete</button>
    </li>
  );
};

export default TodoItem;
