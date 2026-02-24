import React from 'react';
import emojiData from 'emoji-datasource-google';

// Ensure emoji-datasource-google is installed and included in package.json if missing

const EmojiPicker = ({ onEmojiSelect }) => {
  return (
    <div className="grid grid-cols-8 sm:grid-cols-12 gap-2">
      {emojiData.map((emoji, index) => (
        <button
          key={index}
          onClick={() => onEmojiSelect(emoji.short_name)}
          className="text-xl"
        >
          {String.fromCodePoint(...emoji.unified.split('-').map(u => '0x' + u))}
        </button>
      ))}
    </div>
  );
};

export default EmojiPicker;