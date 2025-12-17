import React, { useEffect, useState, useRef } from 'react';
import styles from './ChatWidget.module.css';

interface TextSelectionHandlerProps {
  onTextSelected: (text: string) => void;
}

interface ContextMenuPosition {
  x: number;
  y: number;
}

export const TextSelectionHandler: React.FC<TextSelectionHandlerProps> = ({ onTextSelected }) => {
  const [selectedText, setSelectedText] = useState<string>('');
  const [menuPosition, setMenuPosition] = useState<ContextMenuPosition | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseUp = (event: MouseEvent) => {
      // Small delay to ensure selection is complete
      setTimeout(() => {
        const selection = window.getSelection();
        const text = selection?.toString().trim();

        if (text && text.length > 0) {
          setSelectedText(text);

          // Get selection coordinates
          const range = selection?.getRangeAt(0);
          const rect = range?.getBoundingClientRect();

          if (rect) {
            // Calculate position with boundary detection
            const menuWidth = 200; // Approximate menu width
            const menuHeight = 50; // Approximate menu height
            const padding = 16; // Padding from viewport edges

            let x = rect.left + rect.width / 2;
            let y = rect.bottom + 8;

            // Prevent going off right edge
            if (x + menuWidth / 2 > window.innerWidth - padding) {
              x = window.innerWidth - menuWidth / 2 - padding;
            }

            // Prevent going off left edge
            if (x - menuWidth / 2 < padding) {
              x = menuWidth / 2 + padding;
            }

            // If menu would go off bottom, position above selection
            if (y + menuHeight > window.innerHeight - padding) {
              y = rect.top - menuHeight - 8;
            }

            // Ensure y is not negative (above viewport)
            if (y < padding) {
              y = padding;
            }

            setMenuPosition({ x, y });
          }
        } else {
          // Clear menu if no text selected
          setSelectedText('');
          setMenuPosition(null);
        }
      }, 10);
    };

    const handleTouchEnd = (event: TouchEvent) => {
      // Handle mobile touch selection
      setTimeout(() => {
        const selection = window.getSelection();
        const text = selection?.toString().trim();

        if (text && text.length > 0) {
          setSelectedText(text);

          const range = selection?.getRangeAt(0);
          const rect = range?.getBoundingClientRect();

          if (rect) {
            // Calculate position with boundary detection (mobile)
            const menuWidth = 200;
            const menuHeight = 50;
            const padding = 16;

            let x = rect.left + rect.width / 2;
            let y = rect.bottom + 8;

            // Prevent going off right edge
            if (x + menuWidth / 2 > window.innerWidth - padding) {
              x = window.innerWidth - menuWidth / 2 - padding;
            }

            // Prevent going off left edge
            if (x - menuWidth / 2 < padding) {
              x = menuWidth / 2 + padding;
            }

            // If menu would go off bottom, position above selection
            if (y + menuHeight > window.innerHeight - padding) {
              y = rect.top - menuHeight - 8;
            }

            // Ensure y is not negative
            if (y < padding) {
              y = padding;
            }

            setMenuPosition({ x, y });
          }
        }
      }, 10);
    };

    const handleClickOutside = (event: MouseEvent | TouchEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        // Clear selection if clicking outside menu
        setSelectedText('');
        setMenuPosition(null);
      }
    };

    // Attach event listeners
    document.addEventListener('mouseup', handleMouseUp);
    document.addEventListener('touchend', handleTouchEnd);
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('touchstart', handleClickOutside);

    return () => {
      // Cleanup
      document.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('touchend', handleTouchEnd);
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleClickOutside);
    };
  }, []);

  const handleAskChatbot = () => {
    if (selectedText) {
      onTextSelected(selectedText);
      // Clear selection and menu after action
      setSelectedText('');
      setMenuPosition(null);
      window.getSelection()?.removeAllRanges();
    }
  };

  if (!menuPosition || !selectedText) {
    return null;
  }

  return (
    <div
      ref={menuRef}
      className={styles.textSelectionMenu}
      style={{
        position: 'fixed',
        left: `${menuPosition.x}px`,
        top: `${menuPosition.y}px`,
        transform: 'translateX(-50%)', // Center horizontally
        zIndex: 10000,
      }}
    >
      <button
        className={styles.textSelectionButton}
        onClick={handleAskChatbot}
        aria-label="Ask chatbot about this"
      >
        💬 Ask Chatbot about this
      </button>
    </div>
  );
};
