import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Table, Button, Modal, Form, Alert, Badge, Spinner } from 'react-bootstrap';
import { BsPlus, BsPencil, BsTrash, BsEye, BsFileText, BsX, BsCheck2, BsGear } from 'react-icons/bs';
import { useTheme } from '../../contexts/ThemeContext';

const GuidelinesManager = ({ baseUrl, apiStatus }) => {
  const { colors } = useTheme();
  const [guidelines, setGuidelines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [modalMode, setModalMode] = useState('view'); // 'view', 'edit', 'create'
  const [selectedGuideline, setSelectedGuideline] = useState(null);
  const [formData, setFormData] = useState({ 
    condition: '', 
    action: '', 
    tags: [],
    metadata: {}
  });
  const [tagInput, setTagInput] = useState('');
  const [metadataKey, setMetadataKey] = useState('');
  const [metadataValue, setMetadataValue] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Add the missing formatDate function
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'Invalid Date';
    }
  };

  useEffect(() => {
    if (apiStatus === 'connected') {
      fetchGuidelines();
    }
  }, [apiStatus, baseUrl]);

  const fetchGuidelines = async () => {
    try {
      setLoading(true);
      setError(null); // Clear previous errors
      const response = await fetch(`${baseUrl}/guidelines`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch guidelines`);
      }
      const data = await response.json();
      console.log('Guidelines API response:', data);
      if (Array.isArray(data)) {
        data.forEach((guideline, index) => {
          console.log(`Guideline ${index}:`, guideline);
          if (guideline.action && typeof guideline.action === 'object') {
            console.log(`Guideline ${index} action is object:`, guideline.action);
          }
          if (guideline.condition && typeof guideline.condition === 'object') {
            console.log(`Guideline ${index} condition is object:`, guideline.condition);
          }
        });
      }
      setGuidelines(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error fetching guidelines:', err);
      setError(err.message);
      setGuidelines([]);
    } finally {
      setLoading(false);
    }
  };

  const handleShowModal = (mode, guideline = null) => {
    try {
      console.log('Opening modal with mode:', mode, 'and guideline:', guideline);
      
      setModalMode(mode);
      setSelectedGuideline(guideline);
      
      if (mode === 'create') {
        setFormData({ 
          condition: '', 
          action: '', 
          tags: [],
          metadata: {}
        });
      } else if (guideline) {
        // Safe data extraction with type checking
        const safeCondition = guideline.condition 
          ? (typeof guideline.condition === 'object' 
              ? JSON.stringify(guideline.condition, null, 2) 
              : String(guideline.condition))
          : '';
          
        const safeAction = guideline.action 
          ? (typeof guideline.action === 'object' 
              ? JSON.stringify(guideline.action, null, 2) 
              : String(guideline.action))
          : '';
          
        const safeTags = Array.isArray(guideline.tags) 
          ? guideline.tags.filter(tag => tag != null) 
          : [];
          
        const safeMetadata = (guideline.metadata && typeof guideline.metadata === 'object' && !Array.isArray(guideline.metadata))
          ? guideline.metadata 
          : {};

        setFormData({
          condition: safeCondition,
          action: safeAction,
          tags: safeTags,
          metadata: safeMetadata
        });
      }
      
      setTagInput('');
      setMetadataKey('');
      setMetadataValue('');
      setShowModal(true);
      setError(null);
      setSuccess(null);
    } catch (err) {
      console.error('Error in handleShowModal:', err);
      setError(`Failed to open modal: ${err.message}`);
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedGuideline(null);
    setFormData({ 
      condition: '', 
      action: '', 
      tags: [],
      metadata: {}
    });
    setTagInput('');
    setMetadataKey('');
    setMetadataValue('');
    setError(null);
    setSuccess(null);
  };

  const handleShowDeleteModal = (guideline) => {
    setSelectedGuideline(guideline);
    setShowDeleteModal(true);
  };

  const handleCloseDeleteModal = () => {
    setShowDeleteModal(false);
    setSelectedGuideline(null);
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

  const handleAddMetadata = () => {
    if (metadataKey.trim() && metadataValue.trim()) {
      setFormData({
        ...formData,
        metadata: { ...formData.metadata, [metadataKey.trim()]: metadataValue.trim() }
      });
      setMetadataKey('');
      setMetadataValue('');
    }
  };

  const handleRemoveMetadata = (key) => {
    const newMetadata = { ...formData.metadata };
    delete newMetadata[key];
    setFormData({
      ...formData,
      metadata: newMetadata
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setError(null); // Clear previous errors
      let response;
      const payload = {
        condition: formData.condition,
        action: formData.action,
        tags: formData.tags,
        metadata: formData.metadata
      };

      if (modalMode === 'edit' && selectedGuideline?.id) {
        response = await fetch(`${baseUrl}/guidelines/${selectedGuideline.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      } else {
        response = await fetch(`${baseUrl}/guidelines`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      }

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      setSuccess(`Guideline ${modalMode === 'edit' ? 'updated' : 'created'} successfully!`);
      await fetchGuidelines();
      
      if (modalMode === 'create') {
        handleCloseModal();
      }
      
    } catch (err) {
      console.error('Error saving guideline:', err);
      setError(err.message);
    }
  };

  const handleDelete = async () => {
    if (!selectedGuideline?.id) return;
    
    try {
      setError(null); // Clear previous errors
      const response = await fetch(`${baseUrl}/guidelines/${selectedGuideline.id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to delete guideline`);
      }

      setSuccess('Guideline deleted successfully!');
      await fetchGuidelines();
      handleCloseDeleteModal();
      
    } catch (err) {
      console.error('Error deleting guideline:', err);
      setError(err.message);
    }
  };

  if (apiStatus !== 'connected') {
    return (
      <Alert variant="warning">
        API not connected. Cannot manage guidelines.
      </Alert>
    );
  }

  return (
    <div>
      <Row className="mb-3">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <h5 style={{ color: colors.text }}>Guidelines Management</h5>
            <Button 
              variant="primary" 
              onClick={() => handleShowModal('create')}
              className="d-flex align-items-center"
            >
              <BsPlus className="me-1" />
              Add Guideline
            </Button>
          </div>
        </Col>
      </Row>

      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading ? (
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <div style={{ color: colors.textSecondary }} className="mt-2">Loading guidelines...</div>
        </div>
      ) : (
        <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
          <Card.Body className="p-0">
            <Table responsive hover style={{ color: colors.text, margin: 0 }}>
              <thead style={{ backgroundColor: colors.background }}>
                <tr>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Condition</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Action</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Tags</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {guidelines.length === 0 ? (
                  <tr>
                    <td colSpan="4" className="text-center py-4" style={{ color: colors.textSecondary }}>
                      No guidelines found. Create your first guideline to get started.
                    </td>
                  </tr>
                ) : (
                  guidelines.map((guideline) => (
                    <tr key={guideline?.id || `guideline-${Math.random()}`} style={{ borderColor: colors.border }}>
                      <td style={{ color: colors.text, borderColor: colors.border }}>
                        <div style={{ maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          <BsFileText className="me-2 text-primary" />
                          {guideline?.condition 
                            ? (typeof guideline.condition === 'object' 
                                ? JSON.stringify(guideline.condition) 
                                : String(guideline.condition))
                            : 'No condition specified'
                          }
                        </div>
                      </td>
                      <td style={{ color: colors.text, borderColor: colors.border }}>
                        <div style={{ maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {guideline?.action 
                            ? (typeof guideline.action === 'object' 
                                ? JSON.stringify(guideline.action) 
                                : String(guideline.action))
                            : 'No action specified'
                          }
                        </div>
                      </td>
                      <td style={{ color: colors.text, borderColor: colors.border }}>
                        {guideline?.tags && Array.isArray(guideline.tags) && guideline.tags.length > 0 ? (
                          <div>
                            {guideline.tags.slice(0, 2).map((tag, index) => (
                              <Badge key={index} bg="secondary" className="me-1 mb-1">
                                {String(tag)}
                              </Badge>
                            ))}
                            {guideline.tags.length > 2 && (
                              <Badge bg="outline-secondary">+{guideline.tags.length - 2}</Badge>
                            )}
                          </div>
                        ) : (
                          <span style={{ color: colors.textSecondary }}>No tags</span>
                        )}
                      </td>
                      <td>
                        <div className="d-flex gap-1">
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => handleShowModal('view', guideline)}
                          >
                            <BsEye />
                          </Button>
                          <Button
                            variant="outline-warning"
                            size="sm"
                            onClick={() => handleShowModal('edit', guideline)}
                          >
                            <BsPencil />
                          </Button>
                          <Button
                            variant="outline-danger"
                            size="sm"
                            onClick={() => handleShowDeleteModal(guideline)}
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
      <Modal show={showModal} onHide={handleCloseModal} size="lg">
        <Modal.Header closeButton style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
          <Modal.Title style={{ color: colors.text }}>
            <BsGear className="me-2" />
            {modalMode === 'create' ? 'Create Guideline' : 
             modalMode === 'edit' ? 'Edit Guideline' : 'View Guideline'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ backgroundColor: colors.cardBg }}>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}

          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label style={{ color: colors.text }}>Condition</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.condition || ''}
                onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
                readOnly={modalMode === 'view'}
                required
                placeholder="Enter the condition for this guideline"
                style={{ 
                  backgroundColor: colors.background, 
                  borderColor: colors.border,
                  color: colors.text 
                }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label style={{ color: colors.text }}>Action</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.action || ''}
                onChange={(e) => setFormData({ ...formData, action: e.target.value })}
                readOnly={modalMode === 'view'}
                required
                placeholder="Enter the action for this guideline"
                style={{ 
                  backgroundColor: colors.background, 
                  borderColor: colors.border,
                  color: colors.text 
                }}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label style={{ color: colors.text }}>Tags</Form.Label>
              {modalMode !== 'view' && (
                <Row className="mb-2">
                  <Col md={10}>
                    <Form.Control
                      type="text"
                      placeholder="Enter a tag"
                      value={tagInput}
                      onChange={(e) => setTagInput(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          handleAddTag();
                        }
                      }}
                      style={{ backgroundColor: colors.background, borderColor: colors.border, color: colors.text }}
                    />
                  </Col>
                  <Col md={2}>
                    <Button variant="primary" onClick={handleAddTag} size="sm">
                      <BsPlus />
                    </Button>
                  </Col>
                </Row>
              )}
              
              {formData.tags && formData.tags.length > 0 && (
                <div>
                  {formData.tags.map((tag, index) => (
                    <Badge 
                      key={index}
                      bg="primary" 
                      className="me-1 mb-1 d-inline-flex align-items-center"
                    >
                      {String(tag)}
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

            <Form.Group className="mb-3">
              <Form.Label style={{ color: colors.text }}>Metadata</Form.Label>
              {modalMode !== 'view' && (
                <Row className="mb-2">
                  <Col md={5}>
                    <Form.Control
                      type="text"
                      placeholder="Key"
                      value={metadataKey}
                      onChange={(e) => setMetadataKey(e.target.value)}
                      style={{ backgroundColor: colors.background, borderColor: colors.border, color: colors.text }}
                    />
                  </Col>
                  <Col md={5}>
                    <Form.Control
                      type="text"
                      placeholder="Value"
                      value={metadataValue}
                      onChange={(e) => setMetadataValue(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          handleAddMetadata();
                        }
                      }}
                      style={{ backgroundColor: colors.background, borderColor: colors.border, color: colors.text }}
                    />
                  </Col>
                  <Col md={2}>
                    <Button variant="primary" onClick={handleAddMetadata} size="sm">
                      <BsPlus />
                    </Button>
                  </Col>
                </Row>
              )}
              
              {formData.metadata && Object.keys(formData.metadata).length > 0 && (
                <div>
                  {Object.entries(formData.metadata).map(([key, value], index) => (
                    <Badge 
                      key={index}
                      bg="info" 
                      className="me-1 mb-1 d-inline-flex align-items-center"
                    >
                      {String(key)}: {String(value)}
                      {modalMode !== 'view' && (
                        <BsX 
                          className="ms-1" 
                          style={{ cursor: 'pointer' }}
                          onClick={() => handleRemoveMetadata(key)}
                        />
                      )}
                    </Badge>
                  ))}
                </div>
              )}
            </Form.Group>

            {selectedGuideline && modalMode === 'view' && (
              <div className="row">
                <div className="col-md-6">
                  <Form.Group className="mb-3">
                    <Form.Label style={{ color: colors.text }}>Created</Form.Label>
                    <Form.Control
                      type="text"
                      value={selectedGuideline?.created_at ? formatDate(selectedGuideline.created_at) : 'N/A'}
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
                    <Form.Label style={{ color: colors.text }}>Updated</Form.Label>
                    <Form.Control
                      type="text"
                      value={selectedGuideline?.updated_at ? formatDate(selectedGuideline.updated_at) : 'N/A'}
                      readOnly
                      style={{ 
                        backgroundColor: colors.background, 
                        borderColor: colors.border,
                        color: colors.text 
                      }}
                    />
                  </Form.Group>
                </div>
                <div className="col-md-12 mt-3">
                  <Form.Group className="mb-3">
                    <Form.Label style={{ color: colors.text }}>ID</Form.Label>
                    <Form.Control
                      type="text"
                      value={selectedGuideline?.id ? String(selectedGuideline.id) : 'N/A'}
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
              {modalMode === 'edit' ? 'Update' : 'Create'} Guideline
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
          Are you sure you want to delete this guideline? This action cannot be undone.
          {selectedGuideline && (
            <div className="mt-2">
              <strong>Condition:</strong> {
                selectedGuideline.condition 
                  ? (typeof selectedGuideline.condition === 'object' 
                      ? JSON.stringify(selectedGuideline.condition) 
                      : String(selectedGuideline.condition))
                  : 'No condition specified'
              }
            </div>
          )}
        </Modal.Body>
        <Modal.Footer style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
          <Button variant="secondary" onClick={handleCloseDeleteModal}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete}>
            Delete
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default GuidelinesManager;