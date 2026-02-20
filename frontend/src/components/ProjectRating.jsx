import React, { useState } from 'react';
import { Star } from 'lucide-react';
import { toast } from './ui/sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const ProjectRating = ({ projectId, initialRating = 0, onRated }) => {
  const [rating, setRating] = useState(initialRating);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasRated, setHasRated] = useState(initialRating > 0);

  const submitRating = async (value) => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    const token = localStorage.getItem('session_token');
    
    try {
      const response = await fetch(`${API_BASE}/api/learning/feedback/rating`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify({
          project_id: projectId,
          rating: value
        })
      });
      
      if (response.ok) {
        setRating(value);
        setHasRated(true);
        toast.success(`Rated ${value} stars!`);
        if (onRated) onRated(value);
      } else {
        toast.error('Failed to submit rating');
      }
    } catch (error) {
      toast.error('Error submitting rating');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          onClick={() => submitRating(star)}
          onMouseEnter={() => setHoveredRating(star)}
          onMouseLeave={() => setHoveredRating(0)}
          disabled={isSubmitting}
          className="p-0.5 transition-transform hover:scale-110 disabled:opacity-50"
          data-testid={`rating-star-${star}`}
        >
          <Star
            size={18}
            className={`transition-colors ${
              star <= (hoveredRating || rating)
                ? 'text-yellow-400 fill-yellow-400'
                : 'text-gray-300'
            }`}
          />
        </button>
      ))}
      {hasRated && (
        <span className="text-xs text-gray-400 ml-1">
          Thanks!
        </span>
      )}
    </div>
  );
};

export default ProjectRating;
