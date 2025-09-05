import React, { useState } from 'react';
import { Button, ListGroup, OverlayTrigger, Popover } from 'react-bootstrap';
import { BsPlus, BsChatDots, BsChevronRight, BsChevronLeft, BsThreeDotsVertical, BsTrash } from 'react-icons/bs';
import styles from '../styles/ChatSidebar.module.css';

const ChatSidebar = ({ 
  chatHistory, 
  currentChatId, 
  onNewChat, 
  onChatSelect, 
  onDeleteSession,
  isCollapsed,
  onToggle,
  onClose,
  isMobile = false
}) => {
  const [showDeletePopover, setShowDeletePopover] = useState(null);

  const formatTime = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) {
      return 'Today';
    } else if (days === 1) {
      return 'Yesterday';
    } else if (days < 7) {
      return `${days} days ago`;
    } else {
      return timestamp.toLocaleDateString();
    }
  };

  const handleDeleteClick = (sessionId, event) => {
    event.stopPropagation(); // Prevent chat selection
    setShowDeletePopover(sessionId);
  };

  const handleDeleteConfirm = (sessionId, event) => {
    event.stopPropagation();
    onDeleteSession(sessionId);
    setShowDeletePopover(null);
  };

  const handleDeleteCancel = (event) => {
    event.stopPropagation();
    setShowDeletePopover(null);
  };

  const renderDeletePopover = (sessionId) => (
    <Popover id={`delete-popover-${sessionId}`} className="modern-popover">
      <Popover.Header className="bg-danger text-white border-0 fw-semibold">
        <BsTrash size={16} className="me-2" />
        Delete Session
      </Popover.Header>
      <Popover.Body className="p-3">
        <p className="mb-3 text-muted">This action cannot be undone. The chat history will be permanently deleted.</p>
        <div className="d-flex gap-2 justify-content-end">
          <Button 
            variant="outline-secondary" 
            size="sm" 
            onClick={handleDeleteCancel}
            className="px-3"
          >
            Cancel
          </Button>
          <Button 
            variant="danger" 
            size="sm" 
            onClick={(e) => handleDeleteConfirm(sessionId, e)}
            className="px-3 fw-semibold"
          >
            <BsTrash size={14} className="me-1" />
            Delete
          </Button>
        </div>
      </Popover.Body>
    </Popover>
  );

  return (
    <div className={`${styles.sidebar} ${isCollapsed ? styles.collapsed : ''}`}>
      {/* Top control buttons */}
      {!isCollapsed && (
        <Button
          variant="ghost"
          className={styles.closeButton}
          onClick={onClose}
          aria-label="Collapse sidebar"
        >
          <BsChevronLeft size={16} />
        </Button>
      )}
      
      {isCollapsed && (
        <Button
          variant="ghost"
          className={styles.expandButton}
          onClick={onToggle}
          title="Expand sidebar"
        >
          <BsChevronRight size={16} />
        </Button>
      )}
      
      <div className={styles.sidebarHeader}>
        {isCollapsed ? (
          <Button
            variant="primary"
            className={styles.collapsedNewChatButton}
            onClick={onNewChat}
            title="New Chat"
          >
            <BsPlus size={20} />
          </Button>
        ) : (
          <Button
            variant="primary"
            className={styles.newChatButton}
            onClick={onNewChat}
          >
            <BsPlus size={20} className="me-2" />
            New Chat
          </Button>
        )}
      </div>
      
      {!isCollapsed && (
        <div className={styles.chatHistory}>
          <h6 className={styles.historyTitle}>Recent Chats</h6>
          <ListGroup variant="flush">
            {chatHistory.map((chat) => (
              <ListGroup.Item
                key={chat.id}
                className={`${styles.chatItem} ${
                  chat.id === currentChatId ? styles.active : ''
                }`}
                onClick={() => onChatSelect(chat.id)}
              >
                <div className={styles.chatItemContent}>
                  <BsChatDots size={16} className={styles.chatIcon} />
                  <div className={styles.chatInfo}>
                    <div className={styles.chatTitle}>{chat.title}</div>
                    <div className={styles.chatPreview}>{chat.lastMessage}</div>
                    <div className={styles.chatTime}>{formatTime(chat.timestamp)}</div>
                  </div>
                  <OverlayTrigger
                    trigger="click"
                    placement="right"
                    show={showDeletePopover === chat.id}
                    onToggle={(show) => setShowDeletePopover(show ? chat.id : null)}
                    overlay={renderDeletePopover(chat.id)}
                    rootClose
                    offset={[0, 8]}
                  >
                    <Button
                      variant="ghost"
                      size="sm"
                      className={styles.deleteButton}
                      onClick={(e) => handleDeleteClick(chat.id, e)}
                      title="Delete session"
                    >
                      <BsThreeDotsVertical size={14} />
                    </Button>
                  </OverlayTrigger>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        </div>
      )}
      
      {isCollapsed && (
        <div className={styles.collapsedChatHistory}>
          {chatHistory.slice(0, 5).map((chat) => (
            <Button
              key={chat.id}
              variant="ghost"
              className={`${styles.collapsedChatItem} ${
                chat.id === currentChatId ? styles.active : ''
              }`}
              onClick={() => onChatSelect(chat.id)}
              title={chat.title}
            >
              <BsChatDots size={16} />
            </Button>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatSidebar;
