import React, { useState, useEffect } from 'react';
import { Toast, ToastContainer } from 'react-bootstrap';
import { BsCheckCircle } from 'react-icons/bs';

const WelcomeToast = () => {
  const [showToast, setShowToast] = useState(false);

  useEffect(() => {
    const hasSeenWelcome = localStorage.getItem('hasSeenWelcome');
    if (!hasSeenWelcome) {
      setTimeout(() => {
        setShowToast(true);
        localStorage.setItem('hasSeenWelcome', 'true');
      }, 1000);
    }
  }, []);

  return (
    <ToastContainer 
      position="top-end" 
      className="p-3"
      style={{ zIndex: 9999 }}
    >
      <Toast 
        show={showToast} 
        onClose={() => setShowToast(false)}
        delay={5000}
        autohide
        bg="success"
      >
        <Toast.Header>
          <BsCheckCircle className="me-2" />
          <strong className="me-auto">Welcome!</strong>
        </Toast.Header>
        <Toast.Body className="text-white">
          <strong>Admin Dashboard is ready!</strong><br />
          Use Alt + 1-5 for quick navigation or toggle dark mode in the header.
        </Toast.Body>
      </Toast>
    </ToastContainer>
  );
};

export default WelcomeToast;
