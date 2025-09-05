import { useEffect, useRef, useState, useCallback } from 'react';

/**
 * Fixed React Hook - aligned with HTML implementation
 */
export default function useParlantChat({
  serverUrl = process.env.REACT_APP_PARLANT_ENV || 'http://192.168.1.16:8800',
  autoStart = true,
  pollWaitSeconds = 30,
  defaultAgentId = "wsAMayFzHK",
  defaultCustomerId = "dhKfsv7rfA",
  defaultTitleTemplate = 'Chat Session {timestamp}'
} = {}) {
  const sessionIdRef = useRef(null);
  const lastOffsetRef = useRef(0);
  const pollingRef = useRef(false);
  const abortRef = useRef(false);

  // Tracking duplicates, errors, skipped events
  const processedOffsetsRef = useRef(new Set());
  const errorCountRef = useRef(0);
  const maxErrors = 5;
  const skippedEventCountRef = useRef(0);
  const maxSkippedEvents = 5000;

  const [messages, setMessages] = useState(() => []);
  const [isThinking, setIsThinking] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [status, setStatus] = useState('ready');
  const [sessionReady, setSessionReady] = useState(false);
  const [error, setError] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [isLoadingSession, setIsLoadingSession] = useState(false);

  const appendMessage = useCallback((partial) => {
    console.log('Appending message:', partial);
    setMessages(prev => {
      // Generate a unique ID that includes more entropy
      const newMessage = { 
        ...partial, 
        id: partial.id || `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}` 
      };
      // Prevent duplicates by checking if message ID already exists
      if (prev.some(msg => msg.id === newMessage.id)) {
        console.log('Skipping duplicate message:', newMessage.id);
        return prev;
      }
      return [...prev, newMessage];
    });
  }, []);

  const jsonFetch = useCallback(async (path, { method = 'GET', body, signal } = {}) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    try {
      const res = await fetch(`${serverUrl}${path}`, {
        method,
        headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache' },
        body: body ? JSON.stringify(body) : undefined,
        signal: signal || controller.signal
      });

      clearTimeout(timeoutId);

      if (!res.ok) {
        let text = '';
        try {
          text = await res.text();
          // Try to parse error body as JSON if possible
          if (text && text[0] === '{') {
            const errJson = JSON.parse(text);
            throw new Error(errJson.detail || text || `HTTP ${res.status}`);
          }
        } catch (e) {
          // If parsing fails, just use text
          throw new Error(text || `HTTP ${res.status}`);
        }
        throw new Error(text || `HTTP ${res.status}`);
      }

      // Handle empty response (e.g. DELETE)
      const contentType = res.headers.get('content-type');
      const responseText = await res.text();
      if (!responseText) {
        return null;
      }
      if (contentType && contentType.includes('application/json')) {
        try {
          return JSON.parse(responseText);
        } catch (e) {
          console.warn('⚠️ Failed to parse JSON response:', responseText);
          return null;
        }
      } else {
        return responseText;
      }
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') throw new Error('Request timeout');
      throw err;
    }
  }, [serverUrl]);

  const api = useRef({
    createSession: ({ agent_id, customer_id, title }) =>
      jsonFetch('/sessions', { method: 'POST', body: { agent_id, customer_id, title } }),
    createEvent: (sessionId, evt) =>
      jsonFetch(`/sessions/${sessionId}/events`, { method: 'POST', body: evt }),
    fetchSessions: ({ agent_id, customer_id }) => {
      const q = new URLSearchParams();
      if (agent_id) q.set('agent_id', agent_id);
      if (customer_id) q.set('customer_id', customer_id);
      const url = `/sessions?${q.toString()}`;
      console.log(`Fetching sessions: ${url}`);
      return jsonFetch(url);
    },
    deleteSession: (session_id) => {
      const url = `/sessions/${session_id}`;
      console.log(`Deleting session: ${url}`);
      return jsonFetch(url, { method: 'DELETE' });
    },
    listEvents: (sessionId, params) => {
      const q = new URLSearchParams();
      if (params.minOffset != null) q.set('min_offset', params.minOffset);
      if (params.waitForData != null) q.set('waitForData', params.waitForData);
      if (params.kinds) {
        if (typeof params.kinds === 'string') {
          q.set('kinds', params.kinds);
        } else if (Array.isArray(params.kinds)) {
          params.kinds.forEach(k => q.append('kinds', k));
        }
      }
      q.set('t', Date.now()); // force no-cache
      const url = `/sessions/${sessionId}/events?${q.toString()}`;
      console.log(`Polling events from offset ${params.minOffset}, URL: ${url}`);
      return jsonFetch(url);
    }
  }).current;

  const handleEvent = useCallback(async (event, skipCustomer = false) => {
    console.log('Processing event with offset:', event.offset, 'kind:', event.kind, 'data:', JSON.stringify(event, null, 2));

    if (event.kind === 'message') {
      // Only skip customer messages if skipCustomer is true
      if (skipCustomer && event.source === 'customer') {
        console.log('Skipping customer message event (already shown in UI):', event);
        return;
      }

      // Extract message text from multiple possible locations
      let messageText = event.data?.message || event.message || event.data?.text || event.text || '';
      let sender = 'bot';
      let agentName = null;

      if (event.source === 'customer') {
        sender = 'user';
      } else if (event.source === 'ai_agent') {
        sender = 'bot';
      } else if (event.source === 'human_agent') {
        sender = 'agent';
        agentName = event.data?.participant?.display_name || 'Agent';
      } else {
        sender = 'bot';
      }

      // Only add message if we have actual text content
      if (messageText && messageText.trim()) {
        console.log('Adding message to chat:', { sender, messageText, agentName });
        appendMessage({
          id: `evt-${event.offset || Date.now()}`,
          text: messageText.trim(),
          sender,
          agentName: agentName || undefined,
          timestamp: new Date(event.created_at || Date.now())
        });
      } else {
        console.warn('Skipping event with no message text:', event);
      }

      // Clear both thinking and typing when a message is received
      setIsThinking(false);
      setIsTyping(false);
    } else if (event.kind === 'status') {
      const newStatus = event.data?.status || event.status || '';
      console.log('Status update:', newStatus);
      
      if (newStatus !== "acknowledged") {
        setStatus(newStatus);
      }
      
      // Handle typing and thinking states based on status
      if (newStatus === 'ready') {
        setIsThinking(false);
        setIsTyping(false);
      } else if (newStatus === 'closed') {
        setIsThinking(false);
        setIsTyping(false);
        pollingRef.current = false;
        abortRef.current = true;
        console.log('Stopping polling due to closed status');
      } else if (newStatus === 'error') {
        setIsThinking(false);
        setIsTyping(false);
        setError('Server error occurred');
      } else if (newStatus === 'typing') {
        setIsThinking(false);
        setIsTyping(true);
      } else {
        // For other statuses (thinking, processing, etc.)
        setIsThinking(true);
        setIsTyping(false);
      }
    }
  }, [appendMessage]);

  const pollLoop = useCallback(async () => {
    if (pollingRef.current || !sessionIdRef.current) {
      console.log('Poll loop skipped:', { isPolling: pollingRef.current, sessionId: sessionIdRef.current });
      return;
    }

    pollingRef.current = true;
    abortRef.current = false;
    console.log('Starting event monitoring from offset:', lastOffsetRef.current);

    while (!abortRef.current && sessionIdRef.current && pollingRef.current) {
      try {
        console.log('Polling for events...');
        const events = await api.listEvents(sessionIdRef.current, {
          minOffset: lastOffsetRef.current,
          waitForData: pollWaitSeconds,
          kinds:'message,status'
        });

        if (events === null) {
          console.log('Received non-JSON response, continuing polling');
          await new Promise(r => setTimeout(r, 3000));
          continue;
        }

        if (Array.isArray(events) && events.length > 0) {
          console.log(`Received ${events.length} events:`, events);
          let batchMax = lastOffsetRef.current;

          for (const event of events) {
            const offset = Number(event.offset);
            if (!isNaN(offset) && Number.isInteger(offset) &&
                offset >= lastOffsetRef.current &&
                !processedOffsetsRef.current.has(offset)) {
              processedOffsetsRef.current.add(offset);
              await handleEvent(event, true); // Skip customer messages
              batchMax = Math.max(batchMax, offset + 1);
              skippedEventCountRef.current = 0;
              console.log('Processed event with offset:', offset);
            } else {
              skippedEventCountRef.current++;
              const reason = processedOffsetsRef.current.has(offset) ? 'duplicate' : offset < lastOffsetRef.current ? 'old offset' : 'invalid offset';
              if (skippedEventCountRef.current <= 10 || skippedEventCountRef.current % 1000 === 0) {
                console.log(`Skipping event (offset: ${event.offset}, reason: ${reason})`);
              }
              if (skippedEventCountRef.current >= maxSkippedEvents) {
                console.warn('Warning: Too many skipped events. Check the server API configuration.');
                pollingRef.current = false;
                setStatus('error');
                setError('Too many skipped events');
                break;
              }
            }
          }

          lastOffsetRef.current = batchMax;
          console.log('Updated lastOffset to:', lastOffsetRef.current);
          errorCountRef.current = 0;
        } else {
          console.log('No new events received');
        }
      } catch (err) {
        console.error('Event monitoring error:', err);
        errorCountRef.current++;
        if (errorCountRef.current >= maxErrors) {
          console.error('Too many polling errors, stopping event monitoring');
          pollingRef.current = false;
          setStatus('error');
          setError(`Polling failed: ${err.message}`);
          break;
        }
        console.log(`Polling error ${errorCountRef.current}/${maxErrors}, retrying in 5 seconds...`);
        await new Promise(r => setTimeout(r, 5000));
      }

      // Wait before next poll
      await new Promise(r => setTimeout(r, 2000));
    }

    pollingRef.current = false;
    console.log('Event monitoring stopped');
  }, [handleEvent, pollWaitSeconds, api]);

  const startNewChat = useCallback(async ({ agentId, customerId, title, sessionId } = {}) => {
    setError(null);
    setIsLoadingSession(true);
    abortRef.current = true;
    await new Promise(r => setTimeout(r, 100));
    
    try {
      let currentSessionId = sessionId;
      
      if (sessionId) {
        // Loading existing session
        console.log('Loading existing session:', sessionId);
        currentSessionId = sessionId;
      } else {
        // Creating new session
        console.log('Creating new chat session...');
        const resolvedAgentId = agentId || defaultAgentId;
        const resolvedCustomerId = customerId || defaultCustomerId;
        const resolvedTitle = title || defaultTitleTemplate.replace('{timestamp}', new Date().toLocaleString());

        const session = await api.createSession({
          agent_id: resolvedAgentId,
          customer_id: resolvedCustomerId,
          title: resolvedTitle
        });

        console.log('Session created:', session.id);
        currentSessionId = session.id;
      }

      // Set up session
      sessionIdRef.current = currentSessionId;
      lastOffsetRef.current = 0;
      processedOffsetsRef.current.clear();
      errorCountRef.current = 0;
      skippedEventCountRef.current = 0;

      // Reset messages to only welcome message
      setMessages([]);

      // If loading existing session, fetch historical messages
      if (sessionId) {
        console.log('Fetching historical messages for session:', sessionId);
        
        try {
          const events = await api.listEvents(currentSessionId, {
            minOffset: 0,
            waitForData: 0,
            kinds: 'message,status'
          });
          
          if (Array.isArray(events) && events.length > 0) {
            console.log(`Loading ${events.length} historical events`);
            let maxOffset = 0;
            
            // Sort events by offset to ensure proper order
            const sortedEvents = events.sort((a, b) => Number(a.offset) - Number(b.offset));
            
            for (const event of sortedEvents) {
              const offset = Number(event.offset);
              if (!isNaN(offset)) {
                processedOffsetsRef.current.add(offset);
                await handleEvent(event, false); // Don't skip customer messages
                maxOffset = Math.max(maxOffset, offset + 1);
              }
            }
            
            lastOffsetRef.current = maxOffset;
            console.log('Loaded historical messages, last offset:', maxOffset);
          } else {
            console.log('No historical messages found for session');
          }
        } catch (historyError) {
          console.error('Failed to load historical messages:', historyError);
          // Continue anyway, just log the error
        }
      }
      
      setSessionReady(true);
      setStatus('ready');
      setIsLoadingSession(false);

      // Start polling for new events
      setTimeout(() => {
        if (!pollingRef.current) {
          pollLoop();
        }
      }, 500);
      
    } catch (e) {
      console.error('Failed to start chat:', e);
      setError(e.message || 'Failed to start chat');
      setStatus('error');
      setIsLoadingSession(false);
    }
  }, [pollLoop, api, defaultAgentId, defaultCustomerId, defaultTitleTemplate, handleEvent]);

  const sendMessage = useCallback(async (text) => {
    if (!text?.trim()) {
      console.log('Empty message, skipping send');
      return;
    }

    const messageText = text.trim();
    console.log('Sending message:', messageText);

    // Add user message immediately to UI for better UX
    appendMessage({
      id: `user-${Date.now()}`,
      text: messageText,
      sender: 'user',
      timestamp: new Date()
    });

    setIsThinking(true);
    setIsTyping(false); // Clear typing when sending message

    // Ensure we have a session
    if (!sessionIdRef.current) {
      console.log('No session, creating new chat first...');
      // Store the pending message
      const pendingMessage = {
        id: `user-${Date.now()}`,
        text: messageText,
        sender: 'user',
        timestamp: new Date()
      };
      await startNewChat();
      // Re-append the user's first message after session creation
      appendMessage(pendingMessage);
    }

    if (!sessionIdRef.current) {
      console.error('No session ID after attempting to create session');
      setIsThinking(false);
      setError('Failed to establish chat session');
      return;
    }

    try {
      await api.createEvent(sessionIdRef.current, {
        kind: 'message',
        source: 'customer',
        message: messageText
      });
      console.log('Message sent successfully to server');

      // Ensure polling is running to get the response
      if (!pollingRef.current) {
        console.log('Starting polling to receive response...');
        setTimeout(() => pollLoop(), 200);
      }
    } catch (e) {
      console.error('Failed to send message:', e);
      setError(e.message || 'Failed to send message');
      setStatus('error');
      setIsThinking(false);
      setIsTyping(false);
    }
  }, [appendMessage, startNewChat, api, pollLoop]);

  const fetchSessions = useCallback(async () => {
    try {
      console.log('Fetching user sessions...');
      const fetchedSessions = await api.fetchSessions({
        agent_id: defaultAgentId,
        customer_id: defaultCustomerId
      });
      
      if (Array.isArray(fetchedSessions)) {
        // Transform sessions to match sidebar format and sort by newest first
        const transformedSessions = fetchedSessions
          .map(session => ({
            id: session.id,
            title: session.title || 'New Conversation',
            lastMessage: 'Session created',
            timestamp: new Date(session.creation_utc)
          }))
          .sort((a, b) => b.timestamp - a.timestamp); // newest first
        setSessions(transformedSessions);
        console.log('Sessions fetched:', transformedSessions);
      } else {
        console.warn('Invalid sessions response:', fetchedSessions);
      }
    } catch (e) {
      console.error('Failed to fetch sessions:', e);
      setError(e.message || 'Failed to fetch sessions');
    }
  }, [api, defaultAgentId, defaultCustomerId]);

  const loadSessionMessages = useCallback(async (sessionId) => {
    // Use startNewChat with sessionId to load existing session
    await startNewChat({ sessionId });
  }, [startNewChat]);

  const deleteSession = useCallback(async (session_id) => {
    try {
      console.log('Deleting session:', session_id);
      await api.deleteSession(session_id);

      // If the deleted session is the current session, clear session but do NOT start a new one
      if (sessionIdRef.current === session_id) {
        sessionIdRef.current = null;
        lastOffsetRef.current = 0;
        processedOffsetsRef.current.clear();
        errorCountRef.current = 0;
        skippedEventCountRef.current = 0;
        setMessages([
          {
            id: 'welcome',
            text: "Hello! I'm the BH Assurance AI assistant. How can I help you today?",
            sender: 'bot',
            timestamp: new Date()
          }
        ]);
        setSessionReady(false);
        setStatus('ready');
        setIsThinking(false);
        setIsTyping(false); // Clear typing state when session is deleted
      }

      // Refresh the sessions list
      await fetchSessions();

      console.log('Session deleted successfully');
    } catch (e) {
      console.error('Failed to delete session:', e);
      setError(e.message || 'Failed to delete session');
    }
  }, [api, fetchSessions]);

  useEffect(() => {
    if (autoStart) {
      // Only fetch sessions, do not create a new session
      fetchSessions();
    }
    return () => {
      console.log('Cleaning up: stopping polling');
      abortRef.current = true;
    };
  }, [autoStart, fetchSessions]);

  return { 
    messages, 
    isThinking, 
    isTyping, // Make sure isTyping is returned
    status, 
    error, 
    sendMessage, 
    startNewChat, 
    sessionReady, 
    sessions, 
    fetchSessions,
    loadSessionMessages,
    isLoadingSession,
    deleteSession 
  };
}