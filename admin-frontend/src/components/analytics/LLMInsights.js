import React, { useState } from 'react';
import { Row, Col, Card, Badge, Alert, Button } from 'react-bootstrap';
import { BsLightbulb, BsExclamationTriangle, BsSearch, BsGear, BsEye } from 'react-icons/bs';
import { useTheme } from '../../contexts/ThemeContext';

const LLMInsights = ({ data }) => {
  const { colors } = useTheme();
  const [showRawData, setShowRawData] = useState(false);

  if (!data || !data.raw) {
    return (
      <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
        <Card.Body className="text-center py-5">
          <div style={{ color: colors.textSecondary }}>No AI insights available</div>
        </Card.Body>
      </Card>
    );
  }

  let insights = {};
  try {
    // Extract JSON from the raw string
    const jsonMatch = data.raw.match(/```json\n([\s\S]*?)\n```/);
    if (jsonMatch) {
      insights = JSON.parse(jsonMatch[1]);
    } else {
      insights = JSON.parse(data.raw);
    }
  } catch (error) {
    console.error('Error parsing LLM insights:', error);
    return (
      <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
        <Card.Body>
          <Alert variant="warning">
            Unable to parse AI insights. <Button variant="link" onClick={() => setShowRawData(true)}>View raw data</Button>
          </Alert>
          {showRawData && (
            <pre style={{ 
              backgroundColor: colors.background, 
              color: colors.text, 
              padding: '10px', 
              borderRadius: '4px',
              fontSize: '12px',
              maxHeight: '300px',
              overflow: 'auto'
            }}>
              {data.raw}
            </pre>
          )}
        </Card.Body>
      </Card>
    );
  }

  const {
    trending_topics = [],
    recurring_failures = [],
    knowledge_gaps = [],
    action_items = [],
    observations = []
  } = insights;

  const InsightCard = ({ title, items, icon: Icon, variant, emptyMessage }) => (
    <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border, height: '100%' }}>
      <Card.Header style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
        <h6 style={{ color: colors.text }} className="mb-0 d-flex align-items-center">
          <Icon className="me-2" />
          {title}
          <Badge bg={variant} className="ms-2">{items.length}</Badge>
        </h6>
      </Card.Header>
      <Card.Body>
        {items.length > 0 ? (
          <ul style={{ color: colors.text, paddingLeft: '20px', marginBottom: 0 }}>
            {items.map((item, index) => (
              <li key={index} style={{ marginBottom: '8px', fontSize: '14px' }}>
                {item}
              </li>
            ))}
          </ul>
        ) : (
          <div style={{ color: colors.textSecondary, fontStyle: 'italic', textAlign: 'center' }}>
            {emptyMessage}
          </div>
        )}
      </Card.Body>
    </Card>
  );

  return (
    <div>
      <Row>
        <Col md={6} className="mb-4">
          <InsightCard
            title="Trending Topics"
            items={trending_topics}
            icon={BsSearch}
            variant="info"
            emptyMessage="No trending topics identified"
          />
        </Col>
        <Col md={6} className="mb-4">
          <InsightCard
            title="Recurring Failures"
            items={recurring_failures}
            icon={BsExclamationTriangle}
            variant="danger"
            emptyMessage="No recurring failures detected"
          />
        </Col>
      </Row>

      <Row>
        <Col md={6} className="mb-4">
          <InsightCard
            title="Knowledge Gaps"
            items={knowledge_gaps}
            icon={BsLightbulb}
            variant="warning"
            emptyMessage="No knowledge gaps identified"
          />
        </Col>
        <Col md={6} className="mb-4">
          <InsightCard
            title="Action Items"
            items={action_items}
            icon={BsGear}
            variant="primary"
            emptyMessage="No action items suggested"
          />
        </Col>
      </Row>

      <Row>
        <Col xs={12} className="mb-4">
          <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
            <Card.Header style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
              <h6 style={{ color: colors.text }} className="mb-0 d-flex align-items-center">
                <BsEye className="me-2" />
                Key Observations
                <Badge bg="secondary" className="ms-2">{observations.length}</Badge>
              </h6>
            </Card.Header>
            <Card.Body>
              {observations.length > 0 ? (
                <div>
                  {observations.map((observation, index) => (
                    <Alert 
                      key={index} 
                      variant="info" 
                      className="mb-2"
                      style={{ fontSize: '14px' }}
                    >
                      {observation}
                    </Alert>
                  ))}
                </div>
              ) : (
                <div style={{ color: colors.textSecondary, fontStyle: 'italic', textAlign: 'center' }}>
                  No key observations recorded
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Raw Data Toggle */}
      <Row>
        <Col xs={12}>
          <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
            <Card.Header style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
              <div className="d-flex justify-content-between align-items-center">
                <h6 style={{ color: colors.text }} className="mb-0">
                  Raw AI Analysis
                </h6>
                <Button 
                  variant="outline-secondary" 
                  size="sm"
                  onClick={() => setShowRawData(!showRawData)}
                >
                  {showRawData ? 'Hide' : 'Show'} Raw Data
                </Button>
              </div>
            </Card.Header>
            {showRawData && (
              <Card.Body>
                <pre style={{ 
                  backgroundColor: colors.background, 
                  color: colors.text, 
                  padding: '15px', 
                  borderRadius: '4px',
                  fontSize: '12px',
                  maxHeight: '400px',
                  overflow: 'auto',
                  margin: 0
                }}>
                  {data.raw}
                </pre>
              </Card.Body>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default LLMInsights;
