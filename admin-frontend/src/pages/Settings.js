import React, { useState } from 'react';
import { Container, Card, Form, Button, Row, Col } from 'react-bootstrap';
import { BsGear, BsBell, BsShield, BsPalette } from 'react-icons/bs';
import { useTheme } from '../contexts/ThemeContext';

const Settings = () => {
  const { colors } = useTheme();
  const [settings, setSettings] = useState({
    notifications: {
      emailNotifications: true,
      pushNotifications: false,
      badAnswerAlerts: true,
      performanceAlerts: true,
    },
    security: {
      twoFactorAuth: false,
      sessionTimeout: '30',
      passwordExpiry: '90',
    },
    appearance: {
      compactMode: false,
      showSidebar: true,
      animationsEnabled: true,
    }
  });

  const cardStyle = {
    backgroundColor: colors.cardBg,
    border: `1px solid ${colors.border}`,
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
    marginBottom: '24px',
  };

  const handleSettingChange = (category, setting, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [setting]: value
      }
    }));
  };

  const SettingsSection = ({ title, icon: Icon, children }) => (
    <Card style={cardStyle}>
      <Card.Header style={{ backgroundColor: 'transparent', borderBottom: `1px solid ${colors.border}` }}>
        <div className="d-flex align-items-center">
          <div 
            style={{
              backgroundColor: colors.primary,
              borderRadius: '8px',
              padding: '8px',
              marginRight: '12px',
            }}
          >
            <Icon size={20} color="white" />
          </div>
          <h5 style={{ color: colors.text, margin: 0 }}>{title}</h5>
        </div>
      </Card.Header>
      <Card.Body>
        {children}
      </Card.Body>
    </Card>
  );

  return (
    <Container fluid className="py-4">
      <h1 style={{ color: colors.text, marginBottom: '24px', fontWeight: 'bold' }}>
        Settings
      </h1>

      <Row>
        <Col lg={8}>
          {/* Notifications Settings */}
          <SettingsSection title="Notifications" icon={BsBell}>
            <Form>
              <Row>
                <Col md={6}>
                  <Form.Check
                    type="switch"
                    id="email-notifications"
                    label="Email Notifications"
                    checked={settings.notifications.emailNotifications}
                    onChange={(e) => handleSettingChange('notifications', 'emailNotifications', e.target.checked)}
                    style={{ color: colors.text, marginBottom: '16px' }}
                  />
                  <Form.Check
                    type="switch"
                    id="push-notifications"
                    label="Push Notifications"
                    checked={settings.notifications.pushNotifications}
                    onChange={(e) => handleSettingChange('notifications', 'pushNotifications', e.target.checked)}
                    style={{ color: colors.text, marginBottom: '16px' }}
                  />
                </Col>
                <Col md={6}>
                  <Form.Check
                    type="switch"
                    id="bad-answer-alerts"
                    label="Bad Answer Alerts"
                    checked={settings.notifications.badAnswerAlerts}
                    onChange={(e) => handleSettingChange('notifications', 'badAnswerAlerts', e.target.checked)}
                    style={{ color: colors.text, marginBottom: '16px' }}
                  />
                  <Form.Check
                    type="switch"
                    id="performance-alerts"
                    label="Performance Alerts"
                    checked={settings.notifications.performanceAlerts}
                    onChange={(e) => handleSettingChange('notifications', 'performanceAlerts', e.target.checked)}
                    style={{ color: colors.text, marginBottom: '16px' }}
                  />
                </Col>
              </Row>
            </Form>
          </SettingsSection>

          {/* Security Settings */}
          <SettingsSection title="Security" icon={BsShield}>
            <Form>
              <Row>
                <Col md={6}>
                  <Form.Check
                    type="switch"
                    id="two-factor-auth"
                    label="Two-Factor Authentication"
                    checked={settings.security.twoFactorAuth}
                    onChange={(e) => handleSettingChange('security', 'twoFactorAuth', e.target.checked)}
                    style={{ color: colors.text, marginBottom: '16px' }}
                  />
                  
                  <Form.Group className="mb-3">
                    <Form.Label style={{ color: colors.text }}>Session Timeout (minutes)</Form.Label>
                    <Form.Select
                      value={settings.security.sessionTimeout}
                      onChange={(e) => handleSettingChange('security', 'sessionTimeout', e.target.value)}
                      style={{
                        backgroundColor: colors.surface,
                        border: `1px solid ${colors.border}`,
                        color: colors.text
                      }}
                    >
                      <option value="15">15 minutes</option>
                      <option value="30">30 minutes</option>
                      <option value="60">1 hour</option>
                      <option value="120">2 hours</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label style={{ color: colors.text }}>Password Expiry (days)</Form.Label>
                    <Form.Select
                      value={settings.security.passwordExpiry}
                      onChange={(e) => handleSettingChange('security', 'passwordExpiry', e.target.value)}
                      style={{
                        backgroundColor: colors.surface,
                        border: `1px solid ${colors.border}`,
                        color: colors.text
                      }}
                    >
                      <option value="30">30 days</option>
                      <option value="60">60 days</option>
                      <option value="90">90 days</option>
                      <option value="180">180 days</option>
                      <option value="never">Never</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
              </Row>
            </Form>
          </SettingsSection>

          {/* Appearance Settings */}
          <SettingsSection title="Appearance" icon={BsPalette}>
            <Form>
              <Row>
                <Col md={6}>
                  <Form.Check
                    type="switch"
                    id="compact-mode"
                    label="Compact Mode"
                    checked={settings.appearance.compactMode}
                    onChange={(e) => handleSettingChange('appearance', 'compactMode', e.target.checked)}
                    style={{ color: colors.text, marginBottom: '16px' }}
                  />
                  <Form.Check
                    type="switch"
                    id="show-sidebar"
                    label="Show Sidebar by Default"
                    checked={settings.appearance.showSidebar}
                    onChange={(e) => handleSettingChange('appearance', 'showSidebar', e.target.checked)}
                    style={{ color: colors.text, marginBottom: '16px' }}
                  />
                </Col>
                <Col md={6}>
                  <Form.Check
                    type="switch"
                    id="animations-enabled"
                    label="Enable Animations"
                    checked={settings.appearance.animationsEnabled}
                    onChange={(e) => handleSettingChange('appearance', 'animationsEnabled', e.target.checked)}
                    style={{ color: colors.text, marginBottom: '16px' }}
                  />
                </Col>
              </Row>
            </Form>
          </SettingsSection>

          {/* Save Button */}
          <div className="d-flex justify-content-end">
            <Button 
              variant="primary" 
              size="lg"
              style={{
                backgroundColor: colors.primary,
                borderColor: colors.primary,
                borderRadius: '8px',
                padding: '12px 24px'
              }}
            >
              <BsGear className="me-2" />
              Save Settings
            </Button>
          </div>
        </Col>

        <Col lg={4}>
          <Card style={cardStyle}>
            <Card.Header style={{ backgroundColor: 'transparent', borderBottom: `1px solid ${colors.border}` }}>
              <h5 style={{ color: colors.text, margin: 0 }}>Quick Actions</h5>
            </Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <Button 
                  variant="outline-primary"
                  style={{ border: `1px solid ${colors.primary}`, color: colors.primary }}
                >
                  Export Data
                </Button>
                <Button 
                  variant="outline-secondary"
                  style={{ border: `1px solid ${colors.textSecondary}`, color: colors.textSecondary }}
                >
                  Clear Cache
                </Button>
                <Button 
                  variant="outline-warning"
                >
                  Reset Dashboard
                </Button>
                <Button 
                  variant="outline-danger"
                >
                  Delete All Data
                </Button>
              </div>
            </Card.Body>
          </Card>

          <Card style={cardStyle}>
            <Card.Header style={{ backgroundColor: 'transparent', borderBottom: `1px solid ${colors.border}` }}>
              <h5 style={{ color: colors.text, margin: 0 }}>System Info</h5>
            </Card.Header>
            <Card.Body>
              <div style={{ color: colors.textSecondary, fontSize: '14px' }}>
                <div className="mb-2">
                  <strong>Version:</strong> 2.1.3
                </div>
                <div className="mb-2">
                  <strong>Last Update:</strong> Aug 13, 2025
                </div>
                <div className="mb-2">
                  <strong>Database:</strong> Connected
                </div>
                <div className="mb-2">
                  <strong>API Status:</strong> <span style={{ color: '#28a745' }}>Healthy</span>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Settings;
