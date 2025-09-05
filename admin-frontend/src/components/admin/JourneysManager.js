import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Table, Button, Modal, Form, Alert, Badge, Spinner, ListGroup } from 'react-bootstrap';
import { BsPlus, BsPencil, BsTrash, BsEye, BsMap, BsX } from 'react-icons/bs';
import { useTheme } from '../../contexts/ThemeContext';

const JourneysManager = ({ baseUrl, apiStatus }) => {
  const { colors } = useTheme();
  const [journeys, setJourneys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [modalMode, setModalMode] = useState('view'); // 'view', 'edit', 'create'
  const [selectedJourney, setSelectedJourney] = useState(null);
  const [formData, setFormData] = useState({ 
    title: '', 
    description: '', 
    conditions: [],
    tags: []
  });
  const [conditionInput, setConditionInput] = useState('');
  const [tagInput, setTagInput] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    if (apiStatus === 'connected') {
      fetchJourneys();
    }
  }, [apiStatus, baseUrl]);

  const fetchJourneys = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${baseUrl}/journeys`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch journeys`);
      }
      
      const data = await response.json();
      setJourneys(Array.isArray(data) ? data : []);
      setError(null);
    } catch (err) {
      console.error('Error fetching journeys:', err);
      setError(err.message);
      setJourneys([]);
    } finally {
      setLoading(false);
    }
  };

  const handleShowModal = (mode, journey = null) => {
    setModalMode(mode);
    setSelectedJourney(journey);
    if (mode === 'create') {
      setFormData({ 
        title: '', 
        description: '', 
        conditions: [],
        tags: []
      });
    } else if (journey) {
      setFormData({
        title: journey.title || journey.name || '',
        description: journey.description || '',
        conditions: journey.conditions || [],
        tags: journey.tags || []
      });
    }
    setConditionInput('');
    setTagInput('');
    setShowModal(true);
    setError(null);
    setSuccess(null);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedJourney(null);
    setFormData({ 
      title: '', 
      description: '', 
      conditions: [],
      tags: []
    });
    setConditionInput('');
    setTagInput('');
    setError(null);
    setSuccess(null);
  };

  const handleShowDeleteModal = (journey) => {
    setSelectedJourney(journey);
    setShowDeleteModal(true);
  };

  const handleCloseDeleteModal = () => {
    setShowDeleteModal(false);
    setSelectedJourney(null);
  };

  const handleAddCondition = () => {
    if (conditionInput.trim() && !formData.conditions.includes(conditionInput.trim())) {
      setFormData({
        ...formData,
        conditions: [...formData.conditions, conditionInput.trim()]
      });
      setConditionInput('');
    }
  };

  const handleRemoveCondition = (index) => {
    setFormData({
      ...formData,
      conditions: formData.conditions.filter((_, i) => i !== index)
    });
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData({
        ...formData,
        tags: [...formData.tags, tagInput.trim()]
      });
      setTagInput('');
    }
  };

  const handleRemoveTag = (index) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter((_, i) => i !== index)
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      let response;
      const payload = {
        title: formData.title,
        description: formData.description,
        conditions: formData.conditions,
        tags: formData.tags
      };

      if (modalMode === 'edit' && selectedJourney) {
        response = await fetch(`${baseUrl}/journeys/${selectedJourney.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      } else {
        response = await fetch(`${baseUrl}/journeys`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to ${modalMode} journey`);
      }

      setSuccess(`Journey ${modalMode === 'edit' ? 'updated' : 'created'} successfully`);
      fetchJourneys();
      setTimeout(() => handleCloseModal(), 1500);
      
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async () => {
    if (!selectedJourney) return;

    try {
      const response = await fetch(`${baseUrl}/journeys/${selectedJourney.id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to delete journey`);
      }

      setSuccess('Journey deleted successfully');
      fetchJourneys();
      handleCloseDeleteModal();
      
    } catch (err) {
      setError(err.message);
    }
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
        API not connected. Cannot manage journeys.
      </Alert>
    );
  }

  return (
    <div>
      <Row className="mb-3">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <h5 style={{ color: colors.text }}>Journeys Management</h5>
            <Button 
              variant="primary" 
              onClick={() => handleShowModal('create')}
              className="d-flex align-items-center"
            >
              <BsPlus className="me-1" />
              Add Journey
            </Button>
          </div>
        </Col>
      </Row>

      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {loading ? (
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <div style={{ color: colors.textSecondary }} className="mt-2">Loading journeys...</div>
        </div>
      ) : (
        <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
          <Card.Body className="p-0">
            <Table responsive hover style={{ color: colors.text, margin: 0 }}>
              <thead style={{ backgroundColor: colors.background }}>
                <tr>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Journey</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Description</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Conditions</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Tags</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {journeys.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="text-center py-4" style={{ color: colors.textSecondary }}>
                      No journeys found
                    </td>
                  </tr>
                ) : (
                  journeys.map((journey) => (
                    <tr key={journey.id} style={{ borderColor: colors.border }}>
                      <td style={{ color: colors.text }}>
                        <div className="d-flex align-items-center">
                          <BsMap className="me-2" size={16} />
                          <div>
                            <strong>{String(journey.title || journey.name || 'Untitled Journey')}</strong>
                            <br />
                            <small style={{ color: colors.textSecondary }}>ID: {journey.id}</small>
                          </div>
                        </div>
                      </td>
                      <td style={{ color: colors.text, maxWidth: '250px' }}>
                        <div style={{ 
                          overflow: 'hidden', 
                          textOverflow: 'ellipsis', 
                          whiteSpace: 'nowrap' 
                        }}>
                          {typeof journey.description === 'string' ? journey.description : String(journey.description || '')}
                        </div>
                      </td>
                      <td>
                        <Badge bg="info" style={{ fontSize: '0.75em' }}>
                          {journey.conditions?.length || 0} conditions
                        </Badge>
                      </td>
                      <td>
                        <div className="d-flex flex-wrap gap-1">
                          {Array.isArray(journey.tags) && journey.tags.slice(0, 2).map((tag, index) => (
                            <Badge key={index} bg="secondary" style={{ fontSize: '0.75em' }}>
                              {String(tag)}
                            </Badge>
                          ))}
                          {Array.isArray(journey.tags) && journey.tags.length > 2 && (
                            <Badge bg="light" text="dark" style={{ fontSize: '0.75em' }}>
                              +{journey.tags.length - 2}
                            </Badge>
                          )}
                        </div>
                      </td>
                      <td>
                        <div className="d-flex gap-1">
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => handleShowModal('view', journey)}
                          >
                            <BsEye />
                          </Button>
                          <Button
                            variant="outline-warning"
                            size="sm"
                            onClick={() => handleShowModal('edit', journey)}
                          >
                            <BsPencil />
                          </Button>
                          <Button
                            variant="outline-danger"
                            size="sm"
                            onClick={() => handleShowDeleteModal(journey)}
                          >
                            <BsTrash />
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

      {/* Main Modal */}
      <Modal show={showModal} onHide={handleCloseModal} size="xl">
        <Modal.Header closeButton style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
          <Modal.Title style={{ color: colors.text }}>
            <BsMap className="me-2" />
            {modalMode === 'create' ? 'Create Journey' : 
             modalMode === 'edit' ? 'Edit Journey' : 'View Journey'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ backgroundColor: colors.cardBg, maxHeight: '70vh', overflowY: 'auto' }}>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}

          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label style={{ color: colors.text }}>Title</Form.Label>
              <Form.Control
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
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

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label style={{ color: colors.text }}>Conditions</Form.Label>
                  {modalMode !== 'view' && (
                    <div className="d-flex mb-2">
                      <Form.Control
                        type="text"
                        value={conditionInput}
                        onChange={(e) => setConditionInput(e.target.value)}
                        placeholder="Add condition (e.g., status = active)"
                        onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCondition())}
                        style={{ 
                          backgroundColor: colors.background, 
                          borderColor: colors.border,
                          color: colors.text 
                        }}
                      />
                      <Button 
                        variant="outline-primary" 
                        onClick={handleAddCondition}
                        className="ms-2"
                      >
                        Add
                      </Button>
                    </div>
                  )}
                  
                  {formData.conditions.length > 0 && (
                    <ListGroup style={{ maxHeight: '200px', overflowY: 'auto' }}>
                      {formData.conditions.map((condition, index) => (
                        <ListGroup.Item 
                          key={index}
                          className="d-flex justify-content-between align-items-center"
                          style={{ 
                            backgroundColor: colors.background, 
                            borderColor: colors.border,
                            color: colors.text 
                          }}
                        >
                          <code style={{ color: colors.text }}>{condition}</code>
                          {modalMode !== 'view' && (
                            <Button
                              variant="outline-danger"
                              size="sm"
                              onClick={() => handleRemoveCondition(index)}
                            >
                              <BsX />
                            </Button>
                          )}
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  )}
                </Form.Group>
              </Col>

              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label style={{ color: colors.text }}>Tags</Form.Label>
                  {modalMode !== 'view' && (
                    <div className="d-flex mb-2">
                      <Form.Control
                        type="text"
                        value={tagInput}
                        onChange={(e) => setTagInput(e.target.value)}
                        placeholder="Add tag"
                        onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
                        style={{ 
                          backgroundColor: colors.background, 
                          borderColor: colors.border,
                          color: colors.text 
                        }}
                      />
                      <Button 
                        variant="outline-primary" 
                        onClick={handleAddTag}
                        className="ms-2"
                      >
                        Add
                      </Button>
                    </div>
                  )}
                  
                  {formData.tags.length > 0 && (
                    <div className="d-flex flex-wrap gap-2">
                      {formData.tags.map((tag, index) => (
                        <Badge 
                          key={index} 
                          bg="secondary" 
                          className="d-flex align-items-center"
                          style={{ fontSize: '0.85em' }}
                        >
                          {tag}
                          {modalMode !== 'view' && (
                            <BsX 
                              className="ms-1" 
                              style={{ cursor: 'pointer' }}
                              onClick={() => handleRemoveTag(index)}
                            />
                          )}
                        </Badge>
                      ))}
                    </div>
                  )}
                </Form.Group>
              </Col>
            </Row>

            {/* Journey Steps Display */}
            {selectedJourney && selectedJourney.steps && modalMode === 'view' && (
              <Form.Group className="mb-3">
                <Form.Label style={{ color: colors.text }}>Journey Steps</Form.Label>
                <div style={{ 
                  maxHeight: '200px', 
                  overflowY: 'auto',
                  border: `1px solid ${colors.border}`,
                  borderRadius: '4px',
                  padding: '10px',
                  backgroundColor: colors.background
                }}>
                  {Array.isArray(selectedJourney.steps) ? (
                    selectedJourney.steps.map((step, index) => (
                      <div key={index} style={{ 
                        marginBottom: '10px',
                        padding: '8px',
                        backgroundColor: colors.cardBg,
                        borderRadius: '4px',
                        border: `1px solid ${colors.border}`
                      }}>
                        <div style={{ color: colors.text, fontWeight: 'bold' }}>
                          Step {index + 1}
                        </div>
                        {typeof step === 'object' && step !== null ? (
                          <div style={{ fontSize: '0.9em', color: colors.textSecondary }}>
                            {step.customer_action && (
                              <div><strong>Customer Action:</strong> {String(step.customer_action)}</div>
                            )}
                            {step.agent_action && (
                              <div><strong>Agent Action:</strong> {String(step.agent_action)}</div>
                            )}
                            {step.is_customer_dependent !== undefined && (
                              <div><strong>Customer Dependent:</strong> {String(step.is_customer_dependent)}</div>
                            )}
                            {Object.entries(step).filter(([key]) => 
                              !['customer_action', 'agent_action', 'is_customer_dependent'].includes(key)
                            ).map(([key, value]) => (
                              <div key={key}><strong>{key}:</strong> {String(value)}</div>
                            ))}
                          </div>
                        ) : (
                          <div style={{ color: colors.textSecondary }}>{String(step)}</div>
                        )}
                      </div>
                    ))
                  ) : (
                    <div style={{ color: colors.textSecondary }}>No steps data available</div>
                  )}
                </div>
              </Form.Group>
            )}

            {selectedJourney && modalMode === 'view' && (
              <div className="row">
                <div className="col-md-6">
                  <Form.Group className="mb-3">
                    <Form.Label style={{ color: colors.text }}>Created</Form.Label>
                    <Form.Control
                      type="text"
                      value={selectedJourney.created_at ? formatDate(selectedJourney.created_at) : 'N/A'}
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
                      value={selectedJourney.updated_at ? formatDate(selectedJourney.updated_at) : 'N/A'}
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
              {modalMode === 'edit' ? 'Update' : 'Create'} Journey
            </Button>
          )}
        </Modal.Footer>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal show={showDeleteModal} onHide={handleCloseDeleteModal}>
        <Modal.Header closeButton style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
          <Modal.Title style={{ color: colors.text }}>Confirm Delete</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ backgroundColor: colors.cardBg, color: colors.text }}>
          Are you sure you want to delete the journey "{selectedJourney?.title || selectedJourney?.name}"? This action cannot be undone.
        </Modal.Body>
        <Modal.Footer style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
          <Button variant="secondary" onClick={handleCloseDeleteModal}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete}>
            Delete Journey
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default JourneysManager;
