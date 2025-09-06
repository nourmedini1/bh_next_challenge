import React from 'react';
import { Navbar, Button } from 'react-bootstrap';
import { IoArrowBack, IoMenu } from 'react-icons/io5';
import Logo from './Logo';
import styles from '../styles/ChatHeader.module.css';

const ChatHeader = ({ onBackClick, onToggleSidebar }) => {
  return (
    <Navbar className={styles.chatHeader}>
      <div className={styles.headerLeft}>
        <Button
          variant="ghost"
          className={styles.menuButton}
          onClick={onToggleSidebar}
        >
          <IoMenu size={20} />
        </Button>
        
        <Button
          variant="ghost"
          className={styles.backButton}
          onClick={onBackClick}
        >
          <IoArrowBack size={20} />
        </Button>
      </div>
      
      <div className={styles.headerCenter}>
        <Logo size={32} />
        <span className={styles.title}>BH Assurance Assistant</span>
      </div>
      
      <div className={styles.headerRight}>
        {/* Space for future actions */}
      </div>
    </Navbar>
  );
};

export default ChatHeader;
