import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Form, Button, Alert, Modal, Spinner, Badge, Tabs, Tab } from 'react-bootstrap';
import { BsDatabase, BsUpload, BsInfoCircle, BsCloudUpload, BsFileEarmarkText, BsCheckCircle, BsExclamationTriangle, BsArrowClockwise } from 'react-icons/bs';
import { useTheme } from '../contexts/ThemeContext';

const VectorStores = () => {
  const { colors } = useTheme();
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedStore, setSelectedStore] = useState('');
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(null);
  const [activeTab, setActiveTab] = useState('stores');
  const [apiStatus, setApiStatus] = useState('unknown'); // 'connected', 'disconnected', 'unknown'

  // Vector store descriptions
  const storeDescriptions = {
    '1-CG-Vie': {
      name: 'Life Insurance',
      description: 'Life insurance documents (11 products covering life insurance, retirement, savings, pension plans)',
      category: 'Life & Savings',
      products: 11
    },
    '2-CG-Santé': {
      name: 'Health Insurance', 
      description: 'Health insurance documents (group health insurance and medical coverage)',
      category: 'Health',
      products: 'Multiple'
    },
    '3-CG-Transport': {
      name: 'Transport & Marine',
      description: 'Transport & marine insurance documents (7 products for cargo, shipping, vessel insurance)',
      category: 'Commercial',
      products: 7
    },
    '4-CG-IARD': {
      name: 'Property & Casualty',
      description: 'Property & casualty insurance documents (16+ products for home, business, liability, property risks)',
      category: 'Property',
      products: '16+'
    },
    '5-CG-Engineering': {
      name: 'Engineering & Construction',
      description: 'Engineering & construction insurance documents (4 products for construction, assembly, contractor risks)',
      category: 'Engineering',
      products: 4
    },
    '6-CG-Automobile': {
      name: 'Automobile Insurance',
      description: 'Automobile insurance documents (motor vehicle insurance coverage)',
      category: 'Auto',
      products: 'Multiple'
    },
    '7-Assurance-BH-Connaissances-Generales': {
      name: 'BH Assurance General Knowledge',
      description: 'BH Assurance general knowledge (comprehensive documentation covering procedures, regulations, and services)',
      category: 'General',
      products: 'Comprehensive'
    }
  };

  // Fetch stores data
  useEffect(() => {
    fetchStores();
  }, []);

  const fetchStores = async () => {
    try {
      setLoading(true);
      // Update to use actual API endpoint
      const response = await fetch('http://localhost:8000/query/stores');
      
      if (!response.ok) {
        throw new Error('Failed to fetch stores');
      }
      
      const data = await response.json();
      
      // Transform the API response to our expected format
      const transformedStores = Object.entries(data).map(([key, storeData]) => ({
        name: key,
        displayName: storeData.name,
        description: storeData.description,
        products: storeData.products || [],
        loaded: storeData.loaded,
        endpoint: storeData.endpoint,
        status: storeData.loaded ? 'active' : 'inactive',
        // Mock additional data that might not be in API
        documentCount: Math.floor(Math.random() * 100) + 10,
        lastUpdated: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
        size: `${(Math.random() * 500 + 50).toFixed(1)} MB`
      }));
      
      setStores(transformedStores);
      setError(null);
      setApiStatus('connected');
    } catch (err) {
      console.error('Error fetching stores:', err);
      setError(`Failed to connect to API: ${err.message}`);
      setApiStatus('disconnected');
      // Keep mock data as fallback
      const mockStores = Object.keys(storeDescriptions).map(key => ({
        name: key,
        displayName: storeDescriptions[key].name,
        description: storeDescriptions[key].description,
        products: [],
        loaded: true,
        endpoint: '',
        status: 'active',
        documentCount: Math.floor(Math.random() * 100) + 10,
        lastUpdated: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
        size: `${(Math.random() * 500 + 50).toFixed(1)} MB`
      }));
      setStores(mockStores);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedStore || !uploadFile) {
      alert('Please select a store and file');
      return;
    }

    if (!uploadFile.name.toLowerCase().endsWith('.md')) {
      alert('Please select a markdown (.md) file');
      return;
    }

    setUploading(true);
    setUploadSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', uploadFile);

      // Use actual API endpoint
      const response = await fetch(`http://localhost:8000/query/stores/${selectedStore}/documents`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: Failed to upload document`);
      }

      const result = await response.json();
      
      // Validate response structure
      if (!result || typeof result !== 'object') {
        throw new Error('Invalid response format from server');
      }
      
      setUploadSuccess({
        message: result.message || 'Document uploaded successfully',
        storeName: result.store_name,
        fileName: result.file_name,
        chunkCount: result.chunks_added || 0
      });
      
      // Refresh stores data
      fetchStores();
      
      // Reset form
      setUploadFile(null);
      setSelectedStore('');
      
    } catch (err) {
      console.error('Error uploading file:', err);
      alert(`Error uploading file: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleCloseUploadModal = () => {
    setShowUploadModal(false);
    setUploadSuccess(null);
    setUploadFile(null);
    setSelectedStore('');
  };

  const getCategoryBadgeColor = (category) => {
    const colors = {
      'Life & Savings': 'primary',
      'Health': 'success', 
      'Commercial': 'info',
      'Property': 'warning',
      'Engineering': 'secondary',
      'Auto': 'danger',
      'General': 'dark'
    };
    return colors[category] || 'light';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <Container fluid className="py-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <div>
              <h2 style={{ color: colors.text }} className="mb-1">
                <BsDatabase className="me-2" />
                Vector Stores Management
              </h2>
              <p style={{ color: colors.textSecondary }} className="mb-0">
                Manage vector stores and upload documents for AI processing
              </p>
            </div>
            <div className="d-flex gap-2">
              <Button 
                variant="outline-secondary" 
                onClick={fetchStores}
                disabled={loading}
                className="d-flex align-items-center"
              >
                <BsArrowClockwise className={`me-2 ${loading ? 'spin' : ''}`} />
                Refresh
              </Button>
              <Button 
                variant="primary" 
                onClick={() => setShowUploadModal(true)}
                className="d-flex align-items-center"
              >
                <BsUpload className="me-2" />
                Upload Document
              </Button>
            </div>
          </div>

          {error && (
            <Alert variant="warning" className="d-flex align-items-center">
              <BsExclamationTriangle className="me-2" />
              {error}
            </Alert>
          )}

          {/* API Status Indicator */}
          <div className="d-flex align-items-center mb-3">
            <small style={{ color: colors.textSecondary }} className="me-2">API Status:</small>
            <Badge bg={apiStatus === 'connected' ? 'success' : apiStatus === 'disconnected' ? 'danger' : 'secondary'}>
              {apiStatus === 'connected' ? '🟢 Connected' : apiStatus === 'disconnected' ? '🔴 Disconnected' : '⚪ Unknown'}
            </Badge>
            <small style={{ color: colors.textSecondary }} className="ms-2">
              http://localhost:8000
            </small>
          </div>
        </Col>
      </Row>

      <Tabs activeKey={activeTab} onSelect={(k) => setActiveTab(k)} className="mb-4">
        <Tab eventKey="stores" title="Vector Stores">
          <Row>
            <Col>
              <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
                <Card.Header style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
                  <h5 style={{ color: colors.text }} className="mb-0">
                    Available Vector Stores
                  </h5>
                </Card.Header>
                <Card.Body>
                  {loading ? (
                    <div className="text-center py-4">
                      <Spinner animation="border" variant="primary" />
                      <div style={{ color: colors.textSecondary }} className="mt-2">
                        Loading stores...
                      </div>
                    </div>
                  ) : (
                    <Table responsive hover style={{ color: colors.text }}>
                      <thead>
                        <tr style={{ borderColor: colors.border }}>
                          <th style={{ color: colors.text }}>Store Name</th>
                          <th style={{ color: colors.text }}>Display Name</th>
                          <th style={{ color: colors.text }}>Description</th>
                          <th style={{ color: colors.text }}>Products</th>
                          <th style={{ color: colors.text }}>Documents</th>
                          <th style={{ color: colors.text }}>Size</th>
                          <th style={{ color: colors.text }}>Last Updated</th>
                          <th style={{ color: colors.text }}>Status</th>
                          <th style={{ color: colors.text }}>Endpoint</th>
                        </tr>
                      </thead>
                      <tbody>
                        {stores.map((store) => {
                          const storeInfo = storeDescriptions[store.name] || {};
                          return (
                            <tr key={store.name} style={{ borderColor: colors.border }}>
                              <td>
                                <code style={{ backgroundColor: colors.background, color: colors.primary }}>
                                  {store.name}
                                </code>
                              </td>
                              <td style={{ color: colors.text }}>
                                {store.displayName || storeInfo.name || store.name}
                              </td>
                              <td style={{ color: colors.text, maxWidth: '300px' }}>
                                <div style={{ 
                                  overflow: 'hidden', 
                                  textOverflow: 'ellipsis', 
                                  whiteSpace: 'nowrap',
                                  fontSize: '0.9em'
                                }}>
                                  {store.description || storeInfo.description || 'No description'}
                                </div>
                              </td>
                              <td style={{ color: colors.text }}>
                                {Array.isArray(store.products) ? (
                                  <div>
                                    <Badge bg="info">{store.products.length}</Badge>
                                    {store.products.length > 0 && (
                                      <div style={{ fontSize: '0.8em', color: colors.textSecondary }}>
                                        {store.products.slice(0, 2).join(', ')}
                                        {store.products.length > 2 && '...'}
                                      </div>
                                    )}
                                  </div>
                                ) : (
                                  storeInfo.products || 'N/A'
                                )}
                              </td>
                              <td style={{ color: colors.text }}>
                                {store.documentCount || 0}
                              </td>
                              <td style={{ color: colors.text }}>
                                {store.size || 'N/A'}
                              </td>
                              <td style={{ color: colors.textSecondary }}>
                                {store.lastUpdated ? formatDate(store.lastUpdated) : 'N/A'}
                              </td>
                              <td>
                                <Badge bg={store.loaded ? 'success' : 'warning'}>
                                  {store.loaded ? 'Loaded' : 'Not Loaded'}
                                </Badge>
                              </td>
                              <td style={{ color: colors.text }}>
                                <code style={{ backgroundColor: colors.background, color: colors.textSecondary, fontSize: '0.8em' }}>
                                  {store.endpoint || 'N/A'}
                                </code>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </Table>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>

        <Tab eventKey="info" title="Store Information">
          <Row>
            {Object.entries(storeDescriptions).map(([key, store]) => (
              <Col md={6} lg={4} key={key} className="mb-4">
                <Card 
                  style={{ 
                    backgroundColor: colors.cardBg, 
                    borderColor: colors.border,
                    height: '100%'
                  }}
                >
                  <Card.Header style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
                    <div className="d-flex justify-content-between align-items-center">
                      <h6 style={{ color: colors.text }} className="mb-0">
                        {store.name}
                      </h6>
                      <Badge bg={getCategoryBadgeColor(store.category)}>
                        {store.category}
                      </Badge>
                    </div>
                  </Card.Header>
                  <Card.Body>
                    <div className="mb-3">
                      <small style={{ color: colors.textSecondary }} className="text-uppercase fw-bold">
                        Store ID
                      </small>
                      <div>
                        <code style={{ backgroundColor: colors.background, color: colors.primary }}>
                          {key}
                        </code>
                      </div>
                    </div>
                    <div className="mb-3">
                      <small style={{ color: colors.textSecondary }} className="text-uppercase fw-bold">
                        Description
                      </small>
                      <p style={{ color: colors.text }} className="mb-0 small">
                        {store.description}
                      </p>
                    </div>
                    <div>
                      <small style={{ color: colors.textSecondary }} className="text-uppercase fw-bold">
                        Products
                      </small>
                      <div style={{ color: colors.text }}>
                        {store.products}
                      </div>
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>
        </Tab>
      </Tabs>

      {/* Upload Modal */}
      <Modal show={showUploadModal} onHide={handleCloseUploadModal} size="lg">
        <Modal.Header closeButton style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
          <Modal.Title style={{ color: colors.text }}>
            <BsCloudUpload className="me-2" />
            Upload Document to Vector Store
          </Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ backgroundColor: colors.cardBg }}>
          {uploadSuccess && (
            <Alert variant="success" className="d-flex align-items-start" dismissible onClose={() => setUploadSuccess(null)}>
              <BsCheckCircle className="me-2 mt-1" />
              <div>
                <strong>{uploadSuccess.message}</strong>
                <br />
                <small>
                  <strong>Store:</strong> {uploadSuccess.storeName || selectedStore}<br />
                  <strong>File:</strong> {uploadSuccess.fileName || uploadFile?.name}<br />
                  <strong>Chunks Added:</strong> {uploadSuccess.chunkCount}
                </small>
              </div>
            </Alert>
          )}

          <Form>
            <Form.Group className="mb-3">
              <Form.Label style={{ color: colors.text }}>
                <BsDatabase className="me-2" />
                Select Vector Store
              </Form.Label>
              <Form.Select
                value={selectedStore}
                onChange={(e) => setSelectedStore(e.target.value)}
                style={{ 
                  backgroundColor: colors.background, 
                  borderColor: colors.border,
                  color: colors.text 
                }}
              >
                <option value="">Choose a vector store...</option>
                {stores.map((store) => (
                  <option key={store.name} value={store.name}>
                    {store.displayName ? `${store.displayName} (${store.name})` : store.name}
                  </option>
                ))}
              </Form.Select>
              {selectedStore && (
                <Form.Text style={{ color: colors.textSecondary }}>
                  <BsInfoCircle className="me-1" />
                  {(() => {
                    const store = stores.find(s => s.name === selectedStore);
                    return store?.description || storeDescriptions[selectedStore]?.description || 'No description available';
                  })()}
                </Form.Text>
              )}
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label style={{ color: colors.text }}>
                <BsFileEarmarkText className="me-2" />
                Markdown Document
              </Form.Label>
              <Form.Control
                type="file"
                accept=".md"
                onChange={(e) => setUploadFile(e.target.files[0])}
                style={{ 
                  backgroundColor: colors.background, 
                  borderColor: colors.border,
                  color: colors.text 
                }}
              />
              <Form.Text style={{ color: colors.textSecondary }}>
                Only markdown (.md) files are supported
              </Form.Text>
            </Form.Group>

            {uploadFile && (
              <Alert variant="info">
                <BsInfoCircle className="me-2" />
                <strong>Selected file:</strong> {uploadFile.name} ({(uploadFile.size / 1024).toFixed(1)} KB)
              </Alert>
            )}
          </Form>
        </Modal.Body>
        <Modal.Footer style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
          <Button variant="secondary" onClick={handleCloseUploadModal}>
            Cancel
          </Button>
          <Button 
            variant="primary" 
            onClick={handleFileUpload}
            disabled={!selectedStore || !uploadFile || uploading}
            className="d-flex align-items-center"
          >
            {uploading ? (
              <>
                <Spinner size="sm" className="me-2" />
                Uploading...
              </>
            ) : (
              <>
                <BsUpload className="me-2" />
                Upload Document
              </>
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default VectorStores;
