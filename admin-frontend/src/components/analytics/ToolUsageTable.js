import React, { useState } from 'react';
import { Card, Table, Badge, Form } from 'react-bootstrap';
import { useTheme } from '../../contexts/ThemeContext';

const ToolUsageTable = ({ data }) => {
  const { colors } = useTheme();
  const [sortBy, setSortBy] = useState('requests');
  const [sortOrder, setSortOrder] = useState('desc');

  if (!data || data.length === 0) {
    return (
      <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
        <Card.Body className="text-center py-5">
          <div style={{ color: colors.textSecondary }}>No tool usage data available</div>
        </Card.Body>
      </Card>
    );
  }

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const sortedData = [...data].sort((a, b) => {
    let aVal = a[sortBy];
    let bVal = b[sortBy];
    
    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase();
      bVal = bVal.toLowerCase();
    }
    
    if (sortOrder === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });

  const formatToolName = (toolName) => {
    return toolName
      .replace(/^tool_/, '')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  };

  const getSuccessRate = (success, requests) => {
    if (requests === 0) return 0;
    return ((success / requests) * 100).toFixed(1);
  };

  const getSortIcon = (field) => {
    if (sortBy !== field) return '↕️';
    return sortOrder === 'asc' ? '↑' : '↓';
  };

  return (
    <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
      <Card.Header style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
        <div className="d-flex justify-content-between align-items-center">
          <h5 style={{ color: colors.text }} className="mb-0">
            Tool Usage Statistics
          </h5>
          <Form.Select 
            size="sm" 
            style={{ width: 'auto', backgroundColor: colors.background, borderColor: colors.border, color: colors.text }}
            value={`${sortBy}-${sortOrder}`}
            onChange={(e) => {
              const [field, order] = e.target.value.split('-');
              setSortBy(field);
              setSortOrder(order);
            }}
          >
            <option value="requests-desc">Most Requests</option>
            <option value="requests-asc">Least Requests</option>
            <option value="avg_latency_ms-desc">Highest Latency</option>
            <option value="avg_latency_ms-asc">Lowest Latency</option>
            <option value="errors-desc">Most Errors</option>
            <option value="errors-asc">Least Errors</option>
            <option value="tool_name-asc">Tool Name A-Z</option>
          </Form.Select>
        </div>
      </Card.Header>
      <Card.Body className="p-0">
        <Table responsive hover style={{ color: colors.text, margin: 0 }}>
          <thead style={{ backgroundColor: colors.background }}>
            <tr>
              <th 
                style={{ color: colors.text, cursor: 'pointer', borderColor: colors.border }}
                onClick={() => handleSort('tool_name')}
              >
                Tool Name {getSortIcon('tool_name')}
              </th>
              <th 
                style={{ color: colors.text, cursor: 'pointer', borderColor: colors.border }}
                onClick={() => handleSort('requests')}
              >
                Requests {getSortIcon('requests')}
              </th>
              <th 
                style={{ color: colors.text, cursor: 'pointer', borderColor: colors.border }}
                onClick={() => handleSort('success')}
              >
                Success {getSortIcon('success')}
              </th>
              <th 
                style={{ color: colors.text, cursor: 'pointer', borderColor: colors.border }}
                onClick={() => handleSort('errors')}
              >
                Errors {getSortIcon('errors')}
              </th>
              <th style={{ color: colors.text, borderColor: colors.border }}>
                Success Rate
              </th>
              <th 
                style={{ color: colors.text, cursor: 'pointer', borderColor: colors.border }}
                onClick={() => handleSort('avg_latency_ms')}
              >
                Avg Latency {getSortIcon('avg_latency_ms')}
              </th>
              <th style={{ color: colors.text, borderColor: colors.border }}>
                P95 Latency
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedData.map((tool, index) => {
              const successRate = getSuccessRate(tool.success, tool.requests);
              return (
                <tr key={index} style={{ borderColor: colors.border }}>
                  <td style={{ color: colors.text }}>
                    <div>
                      <strong>{formatToolName(tool.tool_name)}</strong>
                      <br />
                      <small style={{ color: colors.textSecondary }}>
                        {tool.tool_name}
                      </small>
                    </div>
                  </td>
                  <td style={{ color: colors.text }}>
                    <Badge bg="primary">{tool.requests}</Badge>
                  </td>
                  <td style={{ color: colors.text }}>
                    <Badge bg="success">{tool.success}</Badge>
                  </td>
                  <td style={{ color: colors.text }}>
                    <Badge bg="danger">{tool.errors}</Badge>
                  </td>
                  <td>
                    <Badge bg={successRate >= 80 ? 'success' : successRate >= 50 ? 'warning' : 'danger'}>
                      {successRate}%
                    </Badge>
                  </td>
                  <td style={{ color: colors.text }}>
                    {tool.avg_latency_ms.toFixed(0)}ms
                  </td>
                  <td style={{ color: colors.textSecondary }}>
                    {tool.p95_latency_ms.toFixed(0)}ms
                  </td>
                </tr>
              );
            })}
          </tbody>
        </Table>
      </Card.Body>
    </Card>
  );
};

export default ToolUsageTable;
