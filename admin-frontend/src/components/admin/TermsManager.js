import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Table, Button, Modal, Form, Alert, Badge, Spinner, ListGroup } from 'react-bootstrap';
import { BsPlus, BsPencil, BsTrash, BsEye, BsBookmark, BsX, BsCheck2 } from 'react-icons/bs';
import { useTheme } from '../../contexts/ThemeContext';

const TermsManager = ({ baseUrl, apiStatus }) => {
  const { colors } = useTheme();
  const [terms, setTerms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [modalMode, setModalMode] = useState('view'); // 'view', 'edit', 'create'
  const [selectedTerm, setSelectedTerm] = useState(null);
  const [formData, setFormData] = useState({ 
    term: '', 
    description: '', 
    synonyms: [],
    tags: [],
    category: '',
    is_active: true 
  });
  const [synonymInput, setSynonymInput] = useState('');
  const [tagInput, setTagInput] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    if (apiStatus === 'connected') {
      fetchTerms();
    }
  }, [apiStatus, baseUrl]);

  const fetchTerms = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${baseUrl}/terms`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch terms`);
      }
      
      const data = await response.json();
      setTerms(Array.isArray(data) ? data : []);
      setError(null);
    } catch (err) {
      console.error('Error fetching terms:', err);
      setError(err.message);
      setTerms([]);
    } finally {
      setLoading(false);
    }
  };

  const handleShowModal = (mode, term = null) => {
    setModalMode(mode);
    setSelectedTerm(term);
    if (mode === 'create') {
      setFormData({ 
        name: '', 
        description: '', 
        synonyms: [],
        tags: [],
        category: '',
        is_active: true 
      });
    } else if (term) {
      setFormData({
        name: term.name || term.term || '',
        description: term.description || term.definition || '',
        synonyms: term.synonyms || [],
        tags: term.tags || [],
        category: term.category || '',
        is_active: term.is_active !== undefined ? term.is_active : true
      });
    }
    setSynonymInput('');
    setTagInput('');
    setShowModal(true);
    setError(null);
    setSuccess(null);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedTerm(null);
    setFormData({ 
      name: '', 
      description: '', 
      synonyms: [],
      tags: [],
      category: '',
      is_active: true 
    });
    setSynonymInput('');
    setTagInput('');
    setError(null);
    setSuccess(null);
  };

  const handleShowDeleteModal = (term) => {
    setSelectedTerm(term);
    setShowDeleteModal(true);
  };

  const handleCloseDeleteModal = () => {
    setShowDeleteModal(false);
    setSelectedTerm(null);
  };

  const handleAddSynonym = () => {
    if (synonymInput.trim() && !formData.synonyms.includes(synonymInput.trim())) {
      setFormData({
        ...formData,
        synonyms: [...formData.synonyms, synonymInput.trim()]
      });
      setSynonymInput('');
    }
  };

  const handleRemoveSynonym = (index) => {
    setFormData({
      ...formData,
      synonyms: formData.synonyms.filter((_, i) => i !== index)
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
        name: formData.name,
        description: formData.description,
        tags: formData.tags,
        synonyms: formData.synonyms
      };

      if (modalMode === 'edit' && selectedTerm) {
        response = await fetch(`${baseUrl}/terms/${selectedTerm.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      } else {
        response = await fetch(`${baseUrl}/terms`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to ${modalMode} term`);
      }

      setSuccess(`Term ${modalMode === 'edit' ? 'updated' : 'created'} successfully`);
      fetchTerms();
      setTimeout(() => handleCloseModal(), 1500);
      
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async () => {
    if (!selectedTerm) return;

    try {
      const response = await fetch(`${baseUrl}/terms/${selectedTerm.id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to delete term`);
      }

      setSuccess('Term deleted successfully');
      fetchTerms();
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
      'financial': 'success',
      'policy': 'primary',
      'process': 'info',
      'legal': 'warning',
      'technical': 'secondary'
    };
    return variants[category] || 'secondary';
  };

  if (apiStatus !== 'connected') {
    return (
      <Alert variant="warning">
        API not connected. Cannot manage terms.
      </Alert>
    );
  }

  return (
    <div>
      <Row className="mb-3">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <h5 style={{ color: colors.text }}>Terms Management</h5>
            <Button 
              variant="primary" 
              onClick={() => handleShowModal('create')}
              className="d-flex align-items-center"
            >
              <BsPlus className="me-1" />
              Add Term
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
          <div style={{ color: colors.textSecondary }} className="mt-2">Loading terms...</div>
        </div>
      ) : (
        <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
          <Card.Body className="p-0">
            <Table responsive hover style={{ color: colors.text, margin: 0 }}>
              <thead style={{ backgroundColor: colors.background }}>
                <tr>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Term</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Definition</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Tags</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Synonyms</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Category</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Status</th>
                  <th style={{ color: colors.text, borderColor: colors.border }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {terms.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="text-center py-4" style={{ color: colors.textSecondary }}>
                      No terms found
                    </td>
                  </tr>
                ) : (
                  terms.map((term) => (
                    <tr key={term.id} style={{ borderColor: colors.border }}>
                      <td style={{ color: colors.text }}>
                        <div className="d-flex align-items-center">
                          <BsBookmark className="me-2" size={16} />
                          <div>
                            <strong>{term.name || term.term}</strong>
                            <br />
                            <small style={{ color: colors.textSecondary }}>ID: {term.id}</small>
                          </div>
                        </div>
                      </td>
                      <td style={{ color: colors.text, maxWidth: '300px' }}>
                        <div style={{ 
                          overflow: 'hidden', 
                          textOverflow: 'ellipsis', 
                          whiteSpace: 'nowrap' 
                        }}>
                          {term.description || term.definition}
                        </div>
                      </td>
                      <td>
                        <div className="d-flex flex-wrap gap-1">
                          {term.tags?.slice(0, 3).map((tag, index) => (
                            <Badge key={index} bg="primary" style={{ fontSize: '0.75em' }}>
                              {tag}
                            </Badge>
                          ))}
                          {term.tags?.length > 3 && (
                            <Badge bg="light" text="dark" style={{ fontSize: '0.75em' }}>
                              +{term.tags.length - 3} more
                            </Badge>
                          )}
                        </div>
                      </td>
                      <td>
                        <div className="d-flex flex-wrap gap-1">
                          {term.synonyms?.slice(0, 3).map((synonym, index) => (
                            <Badge key={index} bg="outline-secondary" text="dark" style={{ fontSize: '0.75em' }}>
                              {synonym}
                            </Badge>
                          ))}
                          {term.synonyms?.length > 3 && (
                            <Badge bg="light" text="dark" style={{ fontSize: '0.75em' }}>
                              +{term.synonyms.length - 3} more
                            </Badge>
                          )}
                        </div>
                      </td>
                      <td>
                        {term.category && (
                          <Badge bg={getCategoryBadgeVariant(term.category)} style={{ fontSize: '0.75em' }}>
                            {term.category}
                          </Badge>
                        )}
                      </td>
                      <td>
                        <div className="d-flex align-items-center">
                          {term.is_active ? (
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
                      <td>
                        <div className="d-flex gap-1">
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => handleShowModal('view', term)}
                          >
                            <BsEye />
                          </Button>
                          <Button
                            variant="outline-warning"
                            size="sm"
                            onClick={() => handleShowModal('edit', term)}
                          >
                            <BsPencil />
                          </Button>
                          <Button
                            variant="outline-danger"
                            size="sm"
                            onClick={() => handleShowDeleteModal(term)}
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
            <BsBookmark className="me-2" />
            {modalMode === 'create' ? 'Create Term' : 
             modalMode === 'edit' ? 'Edit Term' : 'View Term'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ backgroundColor: colors.cardBg }}>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}

          <Form onSubmit={handleSubmit}>
            <Row>
              <Col md={8}>
                <Form.Group className="mb-3">
                  <Form.Label style={{ color: colors.text }}>Term</Form.Label>
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
                    <option value="financial">Financial</option>
                    <option value="policy">Policy</option>
                    <option value="process">Process</option>
                    <option value="legal">Legal</option>
                    <option value="technical">Technical</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label style={{ color: colors.text }}>Definition</Form.Label>
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
                      bg="primary"
                      className="d-flex align-items-center"
                    >
                      {tag}
                      {modalMode !== 'view' && (
                        <Button
                          variant="link"
                          size="sm"
                          className="p-0 ms-1 text-white"
                          onClick={() => handleRemoveTag(index)}
                          style={{ lineHeight: 1 }}
                        >
                          <BsX />
                        </Button>
                      )}
                    </Badge>
                  ))}
                </div>
              )}
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label style={{ color: colors.text }}>Synonyms</Form.Label>
              {modalMode !== 'view' && (
                <div className="d-flex mb-2">
                  <Form.Control
                    type="text"
                    value={synonymInput}
                    onChange={(e) => setSynonymInput(e.target.value)}
                    placeholder="Add synonym"
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddSynonym())}
                    style={{ 
                      backgroundColor: colors.background, 
                      borderColor: colors.border,
                      color: colors.text 
                    }}
                  />
                  <Button 
                    variant="outline-primary" 
                    onClick={handleAddSynonym}
                    className="ms-2"
                  >
                    Add
                  </Button>
                </div>
              )}
              
              {formData.synonyms.length > 0 && (
                <ListGroup style={{ maxHeight: '150px', overflowY: 'auto' }}>
                  {formData.synonyms.map((synonym, index) => (
                    <ListGroup.Item 
                      key={index}
                      className="d-flex justify-content-between align-items-center"
                      style={{ 
                        backgroundColor: colors.background, 
                        borderColor: colors.border,
                        color: colors.text 
                      }}
                    >
                      {synonym}
                      {modalMode !== 'view' && (
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => handleRemoveSynonym(index)}
                        >
                          <BsX />
                        </Button>
                      )}
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              )}
            </Form.Group>

            <Form.Group className="mb-3">
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

            {selectedTerm && modalMode === 'view' && (
              <div className="row">
                <div className="col-md-6">
                  <Form.Group className="mb-3">
                    <Form.Label style={{ color: colors.text }}>Created</Form.Label>
                    <Form.Control
                      type="text"
                      value={selectedTerm.created_at ? formatDate(selectedTerm.created_at) : 'N/A'}
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
                      value={selectedTerm.updated_at ? formatDate(selectedTerm.updated_at) : 'N/A'}
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
              {modalMode === 'edit' ? 'Update' : 'Create'} Term
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
          Are you sure you want to delete the term "{selectedTerm?.term}"? This action cannot be undone.
        </Modal.Body>
        <Modal.Footer style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
          <Button variant="secondary" onClick={handleCloseDeleteModal}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete}>
            Delete Term
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default TermsManager;
