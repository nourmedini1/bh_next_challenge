import React, { useState, useRef, useEffect } from 'react';
import ChatSidebar from '../components/ChatSidebar';
import ChatMessages from '../components/ChatMessages';
import ChatInput from '../components/ChatInput';
import Navbar from '../components/Navbar';
import styles from '../styles/ChatPage.module.css';
import useParlantChat from '../hooks/useParlantChat';

const ChatPage = () => {
  // Chat state managed by custom hook (messages, typing, send, new chat)
  const {
    messages,
    isThinking,
    isTyping,
    sendMessage: sendChatMessage,
    startNewChat: startNewParlantChat,
    sessionReady,
    status: agentStatus,
    error: chatError,
    sessions,
    fetchSessions,
    isLoadingSession,
    deleteSession
  } = useParlantChat();
  
  const [currentChatId, setCurrentChatId] = useState(null);
  // Removed sidebarOpen (collapsed state handles visibility)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false); // Start expanded
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const messagesEndRef = useRef(null);

  // Handle window resize for mobile detection
  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth <= 768;
      setIsMobile(mobile);
      if (mobile) {
        setSidebarCollapsed(true); // Start collapsed on mobile
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize(); // Call once on mount

    return () => window.removeEventListener('resize', handleResize);
  }, []);


  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isThinking]); // Scroll when messages change OR when typing state changes

  const handleSendMessage = (text) => {
    sendChatMessage(text);
  };

  const handleNewChat = () => {
    // Create a completely new session
    startNewParlantChat();
    setCurrentChatId(null);
    // Refresh sessions after creating a new one
    setTimeout(() => fetchSessions(), 1000);
  };

  const handleChatSelect = (sessionId) => {
    setCurrentChatId(sessionId);
    // Load existing session with its messages
    startNewParlantChat({ sessionId });
  };

  const toggleSidebar = () => {
    // Same behavior for both mobile and desktop
    if (sidebarCollapsed) {
      // If collapsed, expand it
      setSidebarCollapsed(false);
    } else {
      // If expanded, collapse it
      setSidebarCollapsed(true);
    }
  };

  const closeSidebar = () => {
    setSidebarCollapsed(true);
  };

  return (
    <div className={styles.chatPage}>
      <Navbar />
      
      <div className={styles.chatContainer}>
        {/* Sidebar wrapper - always visible, same behavior on mobile and desktop */}
        <div className={`${styles.sidebarWrapper} ${sidebarCollapsed ? styles.sidebarCollapsed : ''} ${isMobile ? styles.mobileOverlay : ''}`}>
          <div className={styles.sidebarCol}>
            <ChatSidebar 
              chatHistory={sessions}
              currentChatId={currentChatId}
              onNewChat={handleNewChat}
              onChatSelect={handleChatSelect}
              onDeleteSession={deleteSession}
              isCollapsed={sidebarCollapsed}
              onToggle={toggleSidebar}
              onClose={closeSidebar}
              isMobile={isMobile}
            />
          </div>
        </div>
        
        {/* Main chat area */}
        <div className={styles.chatMainWrapper}>
          <div className={styles.chatMainCol}>
            <div className={styles.chatMain}>
              <div className={styles.messagesContainer}>
                <ChatMessages messages={messages} isThinking={isThinking} isTyping={isTyping} />
                <div ref={messagesEndRef} />
              </div>
              
              <ChatInput onSendMessage={handleSendMessage} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
