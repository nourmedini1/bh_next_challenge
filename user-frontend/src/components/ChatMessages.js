import React, { useEffect, useRef } from 'react';
import { BsRobot, BsPerson, BsCircle, BsChatDots } from 'react-icons/bs';
import { TiMessages } from 'react-icons/ti';
import ReactMarkdown from 'react-markdown';
import useSound from 'use-sound';
import { useAuth } from '../context/AuthContext';
import TypingIndicator from './TypingIndicator';
import styles from '../styles/ChatMessages.module.css';

const ChatMessages = ({customer, messages, isThinking = false , isTyping = false }) => {
  const { isAuthenticated, isGuest } = useAuth();
  const prevMessagesLength = useRef(messages.length);
  const lastMessageSender = useRef(null);

  // Sound hooks with better control
  const [playUserSound] = useSound('/sounds/user-message.wav', {
    volume: 0.8,
    preload: true,
  });

  const [playBotSound] = useSound('/sounds/bot-message.wav', {
    volume: 0.8,
    preload: true,
  });

  // Sound effect function
  const playMessageSound = (sender) => {
    try {
      if (sender === 'user') {
        playUserSound();
      } else {
        playBotSound();
      }
    } catch (error) {
      console.log('Sound play failed:', error);
    }
  };

  // Function to detect Arabic text
  const detectArabicText = (text) => {
    const arabicRegex = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;
    return arabicRegex.test(text);
  };

  // Function to get text direction - enhanced for mixed content
  const getTextDirection = (text) => {
    if (!text) return 'ltr';
    
    // Count Arabic vs Latin characters
    const arabicMatches = text.match(/[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/g);
    const latinMatches = text.match(/[a-zA-Z]/g);
    
    const arabicCount = arabicMatches ? arabicMatches.length : 0;
    const latinCount = latinMatches ? latinMatches.length : 0;
    
    // If more Arabic characters than Latin, use RTL
    if (arabicCount > latinCount) {
      return 'rtl';
    }
    
    return 'ltr';
  };

  // Play sound when new message is added
  useEffect(() => {
    if (messages.length > prevMessagesLength.current && messages.length > 0) {
      const latestMessage = messages[messages.length - 1];
      
      // Only play sound for new messages from different senders
      if (latestMessage.sender !== lastMessageSender.current || prevMessagesLength.current === 0) {
        // Add small delay to ensure message is rendered
        setTimeout(() => {
          playMessageSound(latestMessage.sender);
        }, 150);
      }
      
      lastMessageSender.current = latestMessage.sender;
    }
    prevMessagesLength.current = messages.length;
  }, [messages, playUserSound, playBotSound]);

  const formatTime = (timestamp) => {
    return new Date(timestamp || Date.now()).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const isDifferentSender = (current, previous) => {
    if (!previous) return true;
    return current.sender !== previous.sender;
  };

  const shouldShowAvatar = (current, previous) => {
    // Show avatar only on the first message of a sequence from the same sender
    if (!previous) return true; // Always show for first message
    return current.sender !== previous.sender; // Show only when sender changes
  };

  return (
    <div className={styles.messagesContainer}>
      {messages.length === 0 ? (
        <div className={styles.emptyState}>
          <div className={styles.emptyStateIcon}>
            <TiMessages size={128} />
          </div>
          <div className={styles.emptyStateText}>
            <h3 className={styles.emptyStateHeading}>Welcome to BH Insurance Assistant</h3>
            <p className={styles.emptyStateMessage}>I'm here to make insurance simple for you.</p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((message, index) => {
        const differentSender = isDifferentSender(message, messages[index - 1]);
        const showAvatar = shouldShowAvatar(message, messages[index - 1]);
        const showHeader = showAvatar; // Show header only when showing avatar

        return (
          <div
            key={message.id}
            className={`${styles.messageWrapper} ${
              message.sender === 'user' ? styles.userMessage : styles.botMessage
            } ${differentSender ? styles.differentSender : ''} ${
              index === 0 ? styles.firstMessage : ''
            }`}
          >
            <div className={styles.messageContent}>
              <div className={styles.messageBubbleContainer}>
                {showHeader && (
                  <div className={styles.messageHeader}>
                    <div className={styles.messageHeaderContent}>
                      {showAvatar && (
                        <div className={styles.avatar}>
                          {message.sender === 'user' ? (
                            <div className={styles.userAvatarIcon}>
                              {isAuthenticated ? (
                                <>
                                  <BsCircle size={40} className={styles.circleIcon} />
                                  <span className={styles.avatarLetter}>G</span>
                                </>
                              ) : (
                                <BsPerson size={20} />
                              )}
                            </div>
                          ) : (
                            <>
                              <img
                                src="/images/bot-avatar.png"
                                alt="BH Assistant"
                                className={styles.botAvatar}
                                onError={(e) => {
                                  e.target.style.display = 'none';
                                  e.target.nextSibling.style.display = 'flex';
                                }}
                              />
                              <BsRobot 
                                size={20} 
                                className={styles.fallbackIcon} 
                                style={{ display: 'none' }} 
                              />
                            </>
                          )}
                        </div>
                      )}
                      <span className={styles.senderName}>
                        {message.sender === 'user' 
                          ? (isAuthenticated ? 'Greta' : 'Guest')
                          : message.sender === 'agent' 
                          ? 'Agent' 
                          : 'BH Assistant'}
                      </span>
                    </div>
                  </div>
                )}
                
                <div className={styles.messageBubble}>
                  <div 
                    className={styles.messageText}
                    dir={getTextDirection(message.text)}
                    lang={detectArabicText(message.text) ? 'ar' : 'en'}
                  >
                    {message.sender === 'user' ? (
                      message.text
                    ) : (
                      <ReactMarkdown>{message.text}</ReactMarkdown>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      })}
      {isThinking && <TypingIndicator text="Thinking" />}
      {isTyping && <TypingIndicator text="Typing" />}
      </>
    )}
    </div>
  );
};

export default ChatMessages;