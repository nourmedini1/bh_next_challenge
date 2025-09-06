import React from 'react';
import { Card } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useTheme } from '../../contexts/ThemeContext';

const LatencyDistribution = ({ data }) => {
  const { colors } = useTheme();

  if (!data || data.length === 0) {
    return (
      <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
        <Card.Body className="text-center py-5">
          <div style={{ color: colors.textSecondary }}>No latency data available</div>
        </Card.Body>
      </Card>
    );
  }

  // Format data for chart
  const chartData = data.map(item => {
    const [min, max] = item.range_ms;
    let label;
    
    if (max === null) {
      label = `${min}ms+`;
    } else if (min === 0) {
      label = `0-${max}ms`;
    } else {
      label = `${min}-${max}ms`;
    }
    
    return {
      range: label,
      count: item.count,
      percentage: 0 // Will calculate after we have total
    };
  });

  // Calculate percentages
  const total = chartData.reduce((sum, item) => sum + item.count, 0);
  chartData.forEach(item => {
    item.percentage = total > 0 ? ((item.count / total) * 100).toFixed(1) : 0;
  });

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{
          backgroundColor: colors.cardBg,
          border: `1px solid ${colors.border}`,
          borderRadius: '8px',
          padding: '10px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
          <p style={{ color: colors.text, margin: '0 0 5px 0', fontWeight: 'bold' }}>
            {label}
          </p>
          <p style={{ color: '#007bff', margin: 0 }}>
            Count: {data.count}
          </p>
          <p style={{ color: colors.textSecondary, margin: 0 }}>
            {data.percentage}% of total
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
      <Card.Header style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
        <h5 style={{ color: colors.text }} className="mb-0">
          Latency Distribution
        </h5>
        <small style={{ color: colors.textSecondary }}>
          Response time ranges
        </small>
      </Card.Header>
      <Card.Body>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
            <XAxis 
              dataKey="range" 
              stroke={colors.textSecondary}
              fontSize={10}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis stroke={colors.textSecondary} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="count" fill="#007bff" />
          </BarChart>
        </ResponsiveContainer>
        
        {/* Summary stats */}
        <div className="mt-3 pt-3" style={{ borderTop: `1px solid ${colors.border}` }}>
          <div className="row text-center">
            <div className="col">
              <small style={{ color: colors.textSecondary }}>Total Requests</small>
              <div style={{ color: colors.text, fontWeight: 'bold' }}>{total}</div>
            </div>
            <div className="col">
              <small style={{ color: colors.textSecondary }}>Fastest Range</small>
              <div style={{ color: colors.text, fontWeight: 'bold' }}>
                {chartData[0]?.range || 'N/A'}
              </div>
            </div>
            <div className="col">
              <small style={{ color: colors.textSecondary }}>Most Common</small>
              <div style={{ color: colors.text, fontWeight: 'bold' }}>
                {chartData.reduce((max, item) => item.count > max.count ? item : max, chartData[0])?.range || 'N/A'}
              </div>
            </div>
          </div>
        </div>
      </Card.Body>
    </Card>
  );
};

export default LatencyDistribution;
