import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Table, Button, Modal, Form, Alert, Badge, Spinner } from 'react-bootstrap';
import { BsPlus, BsPencil, BsEye, BsPersonCircle } from 'react-icons/bs';
import { useTheme } from '../../contexts/ThemeContext';

const AgentsManager = ({ baseUrl, apiStatus }) => {
  const { colors } = useTheme();
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('view'); // 'view', 'edit', 'create'
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [formData, setFormData] = useState({ name: '', description: '', tags: [] });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    if (apiStatus === 'connected') {
      fetchAgents();
    }
  }, [apiStatus, baseUrl]);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${baseUrl}/agents`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch agents`);
      }
      
      const data = await response.json();
      setAgents(Array.isArray(data) ? data : []);
      setError(null);
    } catch (err) {
      console.error('Error fetching agents:', err);
      setError(err.message);
      setAgents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleShowModal = (mode, agent = null) => {
    setModalMode(mode);
    setSelectedAgent(agent);
    if (mode === 'create') {
      setFormData({ name: '', description: '', tags: [] });
    } else if (agent) {
      setFormData({
        name: agent.name || '',
        description: agent.description || '',
        tags: agent.tags || []
      });
    }
    setShowModal(true);
    setError(null);
    setSuccess(null);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedAgent(null);
    setFormData({ name: '', description: '', tags: [] });
    setError(null);
    setSuccess(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      let response;
      const payload = {
        name: formData.name,
        description: formData.description,
        tags: formData.tags
      };

      if (modalMode === 'edit' && selectedAgent) {
        response = await fetch(`${baseUrl}/agents/${selectedAgent.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      } else {
        // Note: Create endpoint not in spec, but would typically be POST /agents
        response = await fetch(`${baseUrl}/agents`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to ${modalMode} agent`);
      }

      setSuccess(`Agent ${modalMode === 'edit' ? 'updated' : 'created'} successfully`);
      fetchAgents();
      setTimeout(() => handleCloseModal(), 1500);
      
    } catch (err) {
      setError(err.message);
    }
  };

  const handleTagsChange = (e) => {
    const tags = e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag);
    setFormData({ ...formData, tags });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (apiStatus !== 'connected') {
    return (
      <Alert variant="warning">
        API not connected. Cannot manage agents.
      </Alert>
    );
  }

  return (
    <div>
      <Row className="mb-3">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <h5 style={{ color: colors.text }}>Agents Management</h5>
            <Button 
              variant="primary" 
              onClick={() => handleShowModal('create')}
              className="d-flex align-items-center"
            >
              <BsPlus className="me-1" />
              Add Agent
            </Button>
          </div>
        </Col>
      </Row>

      {loading ? (
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <div style={{ color: colors.textSecondary }} className="mt-2">Loading agents...</div>
        </div>
      ) : (
        <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
          <Card.Body className="p-0">
            <Table responsive hover style={{ color: colors.text, margin: 0 }}>
              <thead style={{ backgroundColor: colors.background }}>
                <tr>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Agent</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Description</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Tags</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Last Updated</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {agents.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="text-center py-4" style={{ color: colors.textSecondary }}>
                      No agents found
                    </td>
                  </tr>
                ) : (
                  agents.map((agent) => (
                    <tr key={agent.id} style={{ borderColor: colors.border }}>
                      <td style={{ color: colors.text }}>
                        <div className="d-flex align-items-center">
                          <BsPersonCircle className="me-2" size={20} />
                          <div>
                            <strong>{String(agent.name || 'Unnamed Agent')}</strong>
                            <br />
                            <small style={{ color: colors.textSecondary }}>ID: {agent.id}</small>
                          </div>
                        </div>
                      </td>
                      <td style={{ color: colors.text, maxWidth: '300px' }}>
                        <div style={{ 
                          overflow: 'hidden', 
                          textOverflow: 'ellipsis', 
                          whiteSpace: 'nowrap' 
                        }}>
                          {typeof agent.description === 'string' ? agent.description : String(agent.description || '')}
                        </div>
                      </td>
                      <td>
                        <div className="d-flex flex-wrap gap-1">
                          {Array.isArray(agent.tags) && agent.tags.map((tag, index) => (
                            <Badge key={index} bg="secondary" style={{ fontSize: '0.75em' }}>
                              {String(tag)}
                            </Badge>
                          ))}
                        </div>
                      </td>
                      <td style={{ color: colors.textSecondary }}>
                        {agent.updated_at ? formatDate(agent.updated_at) : 'N/A'}
                      </td>
                      <td>
                        <div className="d-flex gap-1">
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => handleShowModal('view', agent)}
                          >
                            <BsEye />
                          </Button>
                          <Button
                            variant="outline-warning"
                            size="sm"
                            onClick={() => handleShowModal('edit', agent)}
                          >
                            <BsPencil />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </Table>
          </Card.Body>
        </Card>
      )}

      {/* Modal */}
      <Modal show={showModal} onHide={handleCloseModal} size="lg">
        <Modal.Header closeButton style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
          <Modal.Title style={{ color: colors.text }}>
            <BsPersonCircle className="me-2" />
            {modalMode === 'create' ? 'Create Agent' : 
             modalMode === 'edit' ? 'Edit Agent' : 'View Agent'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ backgroundColor: colors.cardBg }}>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}

          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label style={{ color: colors.text }}>Name</Form.Label>
              <Form.Control
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                readOnly={modalMode === 'view'}
                required
                style={{ 
                  backgroundColor: colors.background, 
                  borderColor: colors.border,
                  color: colors.text 
                }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label style={{ color: colors.text }}>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                readOnly={modalMode === 'view'}
                required
                style={{ 
                  backgroundColor: colors.background, 
                  borderColor: colors.border,
                  color: colors.text 
                }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label style={{ color: colors.text }}>Tags</Form.Label>
              <Form.Control
                type="text"
                value={formData.tags.join(', ')}
                onChange={handleTagsChange}
                readOnly={modalMode === 'view'}
                placeholder="Enter tags separated by commas"
                style={{ 
                  backgroundColor: colors.background, 
                  borderColor: colors.border,
                  color: colors.text 
                }}
              />
              <Form.Text style={{ color: colors.textSecondary }}>
                Separate multiple tags with commas
              </Form.Text>
            </Form.Group>

            {selectedAgent && modalMode === 'view' && (
              <div className="row">
                <div className="col-md-6">
                  <Form.Group className="mb-3">
                    <Form.Label style={{ color: colors.text }}>Created</Form.Label>
                    <Form.Control
                      type="text"
                      value={selectedAgent.created_at ? formatDate(selectedAgent.created_at) : 'N/A'}
                      readOnly
                      style={{ 
                        backgroundColor: colors.background, 
                        borderColor: colors.border,
                        color: colors.text 
                      }}
                    />
                  </Form.Group>
                </div>
                <div className="col-md-6">
                  <Form.Group className="mb-3">
                    <Form.Label style={{ color: colors.text }}>Last Updated</Form.Label>
                    <Form.Control
                      type="text"
                      value={selectedAgent.updated_at ? formatDate(selectedAgent.updated_at) : 'N/A'}
                      readOnly
                      style={{ 
                        backgroundColor: colors.background, 
                        borderColor: colors.border,
                        color: colors.text 
                      }}
                    />
                  </Form.Group>
                </div>
              </div>
            )}
          </Form>
        </Modal.Body>
        <Modal.Footer style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
          <Button variant="secondary" onClick={handleCloseModal}>
            Close
          </Button>
          {modalMode !== 'view' && (
            <Button variant="primary" onClick={handleSubmit}>
              {modalMode === 'edit' ? 'Update' : 'Create'} Agent
            </Button>
          )}
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default AgentsManager;
