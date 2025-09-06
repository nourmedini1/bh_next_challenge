import React, { useState } from 'react';
import { Form, Button, InputGroup } from 'react-bootstrap';
import { IoSend } from 'react-icons/io5';
import styles from '../styles/ChatInput.module.css';

const ChatInput = ({ onSendMessage }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className={styles.chatInput}>
      <Form onSubmit={handleSubmit}>
        <InputGroup>
          <Form.Control
            type="text"
            placeholder="Ask me anything about BH Assurance services..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            className={styles.messageInput}
          />
          <Button
            type="submit"
            variant="primary"
            disabled={!message.trim()}
            className={styles.sendButton}
          >
            <IoSend size={18} />
          </Button>
        </InputGroup>
      </Form>
    </div>
  );
};

export default ChatInput;
