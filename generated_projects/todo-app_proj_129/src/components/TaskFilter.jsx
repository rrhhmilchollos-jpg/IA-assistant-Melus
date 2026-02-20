import React from 'react';

const TaskFilter = ({ filter, setFilter }) => {
  return (
    <div className="flex justify-around mb-4">
      <button
        onClick={() => setFilter('all')}
        className={`p-2 ${filter === 'all' ? 'text-blue-500' : 'text-black'}`}
      >All</button>
      <button
        onClick={() => setFilter('active')}
        className={`p-2 ${filter === 'active' ? 'text-blue-500' : 'text-black'}`}
      >Active</button>
      <button
        onClick={() => setFilter('completed')}
        className={`p-2 ${filter === 'completed' ? 'text-blue-500' : 'text-black'}`}
      >Completed</button>
    </div>
  );
};

export default TaskFilter;