import React from 'react';
import { BsRobot } from 'react-icons/bs';
import styles from '../styles/TypingIndicator.module.css';

const TypingIndicator = ({ text }) => {
  return (
    <div className={`${styles.messageWrapper} ${styles.botMessage}`}>
      <div className={styles.avatar}>
        <img 
          src="/images/bot-avatar.png" 
          alt="BH Assistant" 
          className={styles.botAvatar}
          onError={(e) => {
            // Fallback to icon if image fails to load
            e.target.style.display = 'none';
            e.target.nextSibling.style.display = 'flex';
          }}
        />
        <BsRobot size={20} className={styles.fallbackIcon} style={{display: 'none'}} />
      </div>
      <div className={styles.messageContent}>
        <div className={styles.messageHeader}>
          <span className={styles.senderName}>BH Assistant</span>
        </div>
        <div className={styles.typingContainer}>
          <div className={styles.typingDots}>
            <span className={styles.typingText}>{text}</span>
            <div className={styles.dot}></div>
            <div className={styles.dot}></div>
            <div className={styles.dot}></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
