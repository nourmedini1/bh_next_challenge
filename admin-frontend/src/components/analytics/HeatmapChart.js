import React from 'react';
import { Card } from 'react-bootstrap';
import { useTheme } from '../../contexts/ThemeContext';

const HeatmapChart = ({ data }) => {
  const { colors } = useTheme();

  if (!data || data.length === 0) {
    return (
      <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
        <Card.Body className="text-center py-5">
          <div style={{ color: colors.textSecondary }}>No heatmap data available</div>
        </Card.Body>
      </Card>
    );
  }

  // Create a 7x24 grid (days x hours)
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const hours = Array.from({ length: 24 }, (_, i) => i);

  // Create lookup map from data
  const dataMap = {};
  data.forEach(item => {
    const key = `${item.dow}-${item.hour}`;
    dataMap[key] = item.requests;
  });

  // Find max value for scaling
  const maxRequests = Math.max(...data.map(item => item.requests), 1);

  const getIntensity = (requests) => {
    return requests / maxRequests;
  };

  const getColor = (requests) => {
    if (requests === 0) return colors.background;
    const intensity = getIntensity(requests);
    const alpha = Math.max(0.1, intensity);
    return `rgba(227, 34, 39, ${alpha})`;
  };

  const cellSize = 30;
  const margin = { top: 50, right: 50, bottom: 30, left: 80 };

  return (
    <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
      <Card.Header style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
        <h5 style={{ color: colors.text }} className="mb-0">
          Request Activity Heatmap
        </h5>
        <small style={{ color: colors.textSecondary }}>
          Day of week vs Hour of day
        </small>
      </Card.Header>
      <Card.Body>
        <div style={{ overflowX: 'auto' }}>
          <svg 
            width={margin.left + hours.length * cellSize + margin.right}
            height={margin.top + days.length * cellSize + margin.bottom}
          >
            {/* Hour labels (top) */}
            {hours.map(hour => (
              <text
                key={hour}
                x={margin.left + hour * cellSize + cellSize / 2}
                y={margin.top - 10}
                textAnchor="middle"
                fill={colors.textSecondary}
                fontSize="12"
              >
                {hour}
              </text>
            ))}
            
            {/* Day labels (left) */}
            {days.map((day, dayIndex) => (
              <text
                key={day}
                x={margin.left - 10}
                y={margin.top + dayIndex * cellSize + cellSize / 2 + 4}
                textAnchor="end"
                fill={colors.textSecondary}
                fontSize="12"
              >
                {day}
              </text>
            ))}

            {/* Heatmap cells */}
            {days.map((day, dayIndex) => 
              hours.map(hour => {
                const dow = dayIndex === 0 ? 7 : dayIndex; // Sunday = 7 in your data
                const key = `${dow}-${hour}`;
                const requests = dataMap[key] || 0;
                
                return (
                  <g key={`${dayIndex}-${hour}`}>
                    <rect
                      x={margin.left + hour * cellSize}
                      y={margin.top + dayIndex * cellSize}
                      width={cellSize - 1}
                      height={cellSize - 1}
                      fill={getColor(requests)}
                      stroke={colors.border}
                      strokeWidth="1"
                      style={{ cursor: 'pointer' }}
                    />
                    {requests > 0 && (
                      <text
                        x={margin.left + hour * cellSize + cellSize / 2}
                        y={margin.top + dayIndex * cellSize + cellSize / 2 + 4}
                        textAnchor="middle"
                        fill={requests > maxRequests * 0.5 ? 'white' : colors.text}
                        fontSize="10"
                        fontWeight="bold"
                      >
                        {requests}
                      </text>
                    )}
                  </g>
                );
              })
            )}

            {/* Legend */}
            <text
              x={margin.left}
              y={margin.top + days.length * cellSize + 25}
              fill={colors.textSecondary}
              fontSize="12"
            >
              Low
            </text>
            
            {/* Legend gradient */}
            <defs>
              <linearGradient id="heatmapGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor={colors.background} />
                <stop offset="100%" stopColor="rgba(227, 34, 39, 1)" />
              </linearGradient>
            </defs>
            
            <rect
              x={margin.left + 30}
              y={margin.top + days.length * cellSize + 15}
              width={100}
              height={15}
              fill="url(#heatmapGradient)"
              stroke={colors.border}
            />
            
            <text
              x={margin.left + 140}
              y={margin.top + days.length * cellSize + 25}
              fill={colors.textSecondary}
              fontSize="12"
            >
              High ({maxRequests})
            </text>
          </svg>
        </div>
      </Card.Body>
    </Card>
  );
};

export default HeatmapChart;
