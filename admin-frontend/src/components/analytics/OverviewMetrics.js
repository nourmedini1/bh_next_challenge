import React from 'react';
import { Row, Col, Card } from 'react-bootstrap';
import { BsCheckCircle, BsXCircle, BsClock, BsSpeedometer } from 'react-icons/bs';
import { useTheme } from '../../contexts/ThemeContext';

const OverviewMetrics = ({ data }) => {
  const { colors } = useTheme();

  if (!data?.overview) {
    return <div>No overview data available</div>;
  }

  const { overview, metadata } = data;
  const successRate = ((overview.total_success / overview.total_requests) * 100).toFixed(1);
  const errorRate = ((overview.total_errors / overview.total_requests) * 100).toFixed(1);

  const metrics = [
    {
      title: 'Total Requests',
      value: overview.total_requests.toLocaleString(),
      icon: BsSpeedometer,
      color: '#007bff',
      subtitle: `Last ${metadata?.since_hours || 0} hours`
    },
    {
      title: 'Success Rate',
      value: `${successRate}%`,
      icon: BsCheckCircle,
      color: '#28a745',
      subtitle: `${overview.total_success} successful`
    },
    {
      title: 'Error Rate',
      value: `${errorRate}%`,
      icon: BsXCircle,
      color: '#dc3545',
      subtitle: `${overview.total_errors} failed`
    },
    {
      title: 'Avg Latency',
      value: `${overview.avg_latency_ms.toFixed(0)}ms`,
      icon: BsClock,
      color: '#ffc107',
      subtitle: `P95: ${overview.p95_latency_ms.toFixed(0)}ms`
    }
  ];

  return (
    <Row>
      {metrics.map((metric, index) => {
        const IconComponent = metric.icon;
        return (
          <Col md={3} key={index} className="mb-3">
            <Card 
              style={{ 
                backgroundColor: colors.cardBg, 
                borderColor: colors.border,
                height: '100%'
              }}
            >
              <Card.Body className="text-center">
                <div className="mb-3">
                  <IconComponent 
                    size={32} 
                    style={{ color: metric.color }}
                  />
                </div>
                <h3 style={{ color: colors.text }} className="mb-1">
                  {metric.value}
                </h3>
                <h6 style={{ color: colors.text }} className="mb-1">
                  {metric.title}
                </h6>
                <small style={{ color: colors.textSecondary }}>
                  {metric.subtitle}
                </small>
              </Card.Body>
            </Card>
          </Col>
        );
      })}
    </Row>
  );
};

export default OverviewMetrics;
