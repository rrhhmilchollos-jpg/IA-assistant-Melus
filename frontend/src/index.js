import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";
import ErrorBoundary from "@/components/ErrorBoundary";

// Suppress removeChild errors from browser extensions
const originalRemoveChild = Node.prototype.removeChild;
Node.prototype.removeChild = function(child) {
  if (child.parentNode !== this) {
    console.warn('removeChild: node is not a child, ignoring');
    return child;
  }
  return originalRemoveChild.apply(this, arguments);
};

const originalInsertBefore = Node.prototype.insertBefore;
Node.prototype.insertBefore = function(newNode, referenceNode) {
  if (referenceNode && referenceNode.parentNode !== this) {
    console.warn('insertBefore: reference node is not a child, ignoring');
    return newNode;
  }
  return originalInsertBefore.apply(this, arguments);
};

// Global error handler for uncaught errors
window.addEventListener('error', (event) => {
  if (event.message?.includes('removeChild') || 
      event.message?.includes('not a child') ||
      event.message?.includes('insertBefore')) {
    event.preventDefault();
    event.stopPropagation();
    console.warn('Suppressed DOM error:', event.message);
    return false;
  }
});

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
);
