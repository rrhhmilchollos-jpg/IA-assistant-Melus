import React from 'react';
import TodoItem from './TodoItem';

const TodoList = ({ tasks, deleteTask, completeTask }) => {
  return (
    <ul className="todo-list">
      {tasks.map(task => (
        <TodoItem key={task.id} task={task} deleteTask={deleteTask} completeTask={completeTask} />
      ))}
    </ul>
  );
};

export default TodoList;
