import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Table, Button, Modal, Form, Alert, Badge, Spinner } from 'react-bootstrap';
import { BsPlus, BsPencil, BsTrash, BsEye, BsTag, BsCheck2, BsX } from 'react-icons/bs';
import { useTheme } from '../../contexts/ThemeContext';

const TagsManager = ({ baseUrl, apiStatus }) => {
  const { colors } = useTheme();
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [modalMode, setModalMode] = useState('view'); // 'view', 'edit', 'create'
  const [selectedTag, setSelectedTag] = useState(null);
  const [formData, setFormData] = useState({ 
    name: '', 
    description: '', 
    color: '#007bff',
    category: '',
    is_active: true 
  });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    if (apiStatus === 'connected') {
      fetchTags();
    }
  }, [apiStatus, baseUrl]);

  const fetchTags = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${baseUrl}/tags`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch tags`);
      }
      
      const data = await response.json();
      setTags(Array.isArray(data) ? data : []);
      setError(null);
    } catch (err) {
      console.error('Error fetching tags:', err);
      setError(err.message);
      setTags([]);
    } finally {
      setLoading(false);
    }
  };

  const handleShowModal = (mode, tag = null) => {
    setModalMode(mode);
    setSelectedTag(tag);
    if (mode === 'create') {
      setFormData({ 
        name: '', 
        description: '', 
        color: '#007bff',
        category: '',
        is_active: true 
      });
    } else if (tag) {
      setFormData({
        name: tag.name || '',
        description: tag.description || '',
        color: tag.color || '#007bff',
        category: tag.category || '',
        is_active: tag.is_active !== undefined ? tag.is_active : true
      });
    }
    setShowModal(true);
    setError(null);
    setSuccess(null);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedTag(null);
    setFormData({ 
      name: '', 
      description: '', 
      color: '#007bff',
      category: '',
      is_active: true 
    });
    setError(null);
    setSuccess(null);
  };

  const handleShowDeleteModal = (tag) => {
    setSelectedTag(tag);
    setShowDeleteModal(true);
  };

  const handleCloseDeleteModal = () => {
    setShowDeleteModal(false);
    setSelectedTag(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      let response;
      const payload = {
        name: formData.name
      };

      if (modalMode === 'edit' && selectedTag) {
        response = await fetch(`${baseUrl}/tags/${selectedTag.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      } else {
        response = await fetch(`${baseUrl}/tags`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to ${modalMode} tag`);
      }

      setSuccess(`Tag ${modalMode === 'edit' ? 'updated' : 'created'} successfully`);
      fetchTags();
      setTimeout(() => handleCloseModal(), 1500);
      
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async () => {
    if (!selectedTag) return;

    try {
      const response = await fetch(`${baseUrl}/tags/${selectedTag.id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to delete tag`);
      }

      setSuccess('Tag deleted successfully');
      fetchTags();
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

  const getCategoryBadgeVariant = (category) => {
    const variants = {
      'domain': 'primary',
      'function': 'success',
      'status': 'warning',
      'type': 'info'
    };
    return variants[category] || 'secondary';
  };

  if (apiStatus !== 'connected') {
    return (
      <Alert variant="warning">
        API not connected. Cannot manage tags.
      </Alert>
    );
  }

  return (
    <div>
      <Row className="mb-3">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <h5 style={{ color: colors.text }}>Tags Management</h5>
            <Button 
              variant="primary" 
              onClick={() => handleShowModal('create')}
              className="d-flex align-items-center"
            >
              <BsPlus className="me-1" />
              Add Tag
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
          <div style={{ color: colors.textSecondary }} className="mt-2">Loading tags...</div>
        </div>
      ) : (
        <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
          <Card.Body className="p-0">
            <Table responsive hover style={{ color: colors.text, margin: 0 }}>
              <thead style={{ backgroundColor: colors.background }}>
                <tr>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Tag</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Description</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Category</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Status</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Last Updated</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tags.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="text-center py-4" style={{ color: colors.textSecondary }}>
                      No tags found
                    </td>
                  </tr>
                ) : (
                  tags.map((tag) => (
                    <tr key={tag.id} style={{ borderColor: colors.border }}>
                      <td style={{ color: colors.text }}>
                        <div className="d-flex align-items-center">
                          <div 
                            className="me-2" 
                            style={{
                              width: '12px',
                              height: '12px',
                              backgroundColor: tag.color,
                              borderRadius: '50%'
                            }}
                          />
                          <BsTag className="me-2" size={16} />
                          <div>
                            <strong>{tag.name}</strong>
                            <br />
                            <small style={{ color: colors.textSecondary }}>ID: {tag.id}</small>
                          </div>
                        </div>
                      </td>
                      <td style={{ color: colors.text, maxWidth: '300px' }}>
                        <div style={{ 
                          overflow: 'hidden', 
                          textOverflow: 'ellipsis', 
                          whiteSpace: 'nowrap' 
                        }}>
                          {tag.description}
                        </div>
                      </td>
                      <td>
                        {tag.category && (
                          <Badge bg={getCategoryBadgeVariant(tag.category)} style={{ fontSize: '0.75em' }}>
                            {tag.category}
                          </Badge>
                        )}
                      </td>
                      <td>
                        <div className="d-flex align-items-center">
                          {tag.is_active ? (
                            <>
                              <BsCheck2 className="text-success me-1" />
                              <span style={{ color: colors.text }}>Active</span>
                            </>
                          ) : (
                            <>
                              <BsX className="text-danger me-1" />
                              <span style={{ color: colors.textSecondary }}>Inactive</span>
                            </>
                          )}
                        </div>
                      </td>
                      <td style={{ color: colors.textSecondary }}>
                        {tag.updated_at ? formatDate(tag.updated_at) : 'N/A'}
                      </td>
                      <td>
                        <div className="d-flex gap-1">
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => handleShowModal('view', tag)}
                          >
                            <BsEye />
                          </Button>
                          <Button
                            variant="outline-warning"
                            size="sm"
                            onClick={() => handleShowModal('edit', tag)}
                          >
                            <BsPencil />
                          </Button>
                          <Button
                            variant="outline-danger"
                            size="sm"
                            onClick={() => handleShowDeleteModal(tag)}
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
            <BsTag className="me-2" />
            {modalMode === 'create' ? 'Create Tag' : 
             modalMode === 'edit' ? 'Edit Tag' : 'View Tag'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ backgroundColor: colors.cardBg }}>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}

          <Form onSubmit={handleSubmit}>
            <Row>
              <Col md={8}>
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
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label style={{ color: colors.text }}>Color</Form.Label>
                  <Form.Control
                    type="color"
                    value={formData.color}
                    onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                    disabled={modalMode === 'view'}
                    style={{ 
                      backgroundColor: colors.background, 
                      borderColor: colors.border,
                      color: colors.text 
                    }}
                  />
                </Form.Group>
              </Col>
            </Row>

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
                  <Form.Label style={{ color: colors.text }}>Category</Form.Label>
                  <Form.Select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    disabled={modalMode === 'view'}
                    style={{ 
                      backgroundColor: colors.background, 
                      borderColor: colors.border,
                      color: colors.text 
                    }}
                  >
                    <option value="">Select category</option>
                    <option value="domain">Domain</option>
                    <option value="function">Function</option>
                    <option value="status">Status</option>
                    <option value="type">Type</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label style={{ color: colors.text }}>Status</Form.Label>
                  <Form.Check
                    type="switch"
                    id="is-active-switch"
                    label="Active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    disabled={modalMode === 'view'}
                    style={{ color: colors.text }}
                  />
                </Form.Group>
              </Col>
            </Row>

            {selectedTag && modalMode === 'view' && (
              <div className="row">
                <div className="col-md-6">
                  <Form.Group className="mb-3">
                    <Form.Label style={{ color: colors.text }}>Created</Form.Label>
                    <Form.Control
                      type="text"
                      value={selectedTag.created_at ? formatDate(selectedTag.created_at) : 'N/A'}
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
                      value={selectedTag.updated_at ? formatDate(selectedTag.updated_at) : 'N/A'}
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
              {modalMode === 'edit' ? 'Update' : 'Create'} Tag
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
          Are you sure you want to delete the tag "{selectedTag?.name}"? This action cannot be undone.
        </Modal.Body>
        <Modal.Footer style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
          <Button variant="secondary" onClick={handleCloseDeleteModal}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete}>
            Delete Tag
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default TagsManager;
