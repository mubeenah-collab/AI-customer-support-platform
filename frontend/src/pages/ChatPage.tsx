import React, { useEffect, useState, useRef } from 'react';
import { ConversationList, ConversationItem } from '../components/chat/ConversationList';
import { ChatMessage, ChatMessageItem } from '../components/chat/ChatMessage';
import { ChatInput } from '../components/chat/ChatInput';
import { apiClient } from '../services/apiClient';

export const ChatPage: React.FC = () => {
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessageItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const fetchConversations = async () => {
    try {
      const res = await apiClient.get('/chat/conversations');
      const data = res.data;
      const list = Array.isArray(data) ? data : (data?.conversations || data?.items || []);
      setConversations(Array.isArray(list) ? list : []);
    } catch (err) {
      console.error('Failed to fetch conversations:', err);
      setConversations([]);
    }
  };

  const fetchMessages = async (convId: string) => {
    try {
      const res = await apiClient.get(`/chat/conversations/${convId}/messages`);
      const data = res.data;
      const rawItems = Array.isArray(data) ? data : (data?.messages || data?.items || []);
      const safeItems = Array.isArray(rawItems) ? rawItems : [];
      setMessages(
        safeItems.map((m: any) => ({
          id: m.id,
          sender: m.role === 'user' ? 'user' : 'assistant',
          content: m.content,
          image_url: m.image_url,
          citations: m.citations,
          timestamp: m.created_at,
        }))
      );
    } catch (err) {
      console.error('Failed to fetch messages:', err);
      setMessages([]);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (activeConversationId) {
      fetchMessages(activeConversationId);
    } else {
      setMessages([]);
    }
  }, [activeConversationId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (content: string, imageFile?: File) => {
    let imageUrl: string | undefined = undefined;

    if (imageFile) {
      const formData = new FormData();
      formData.append('file', imageFile);
      try {
        const uploadRes = await apiClient.post('/documents/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        imageUrl = uploadRes.data.file_path;
      } catch (err) {
        console.error('Image upload failed before sending chat message:', err);
      }
    }

    const tempUserMsg: ChatMessageItem = {
      id: 'temp-' + Date.now(),
      sender: 'user',
      content,
      image_url: imageUrl,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMsg]);
    setIsLoading(true);

    try {
      const res = await apiClient.post('/chat/message', {
        message: content,
        conversation_id: activeConversationId || undefined,
        image_url: imageUrl,
      });

      const data = res.data;
      if (!activeConversationId && data.conversation_id) {
        setActiveConversationId(data.conversation_id);
        fetchConversations();
      }

      const botMsg: ChatMessageItem = {
        id: data.message_id || 'bot-' + Date.now(),
        sender: 'assistant',
        content: data.response || data.content,
        citations: data.sources || data.citations,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessageItem = {
        id: 'err-' + Date.now(),
        sender: 'assistant',
        content: 'Error: ' + (err.response?.data?.detail || 'Failed to generate response. Please try again.'),
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewConversation = () => {
    setActiveConversationId(null);
    setMessages([]);
  };

  const handleDeleteConversation = async (convId: string) => {
    try {
      await apiClient.delete(`/chat/conversations/${convId}`);
      if (activeConversationId === convId) {
        setActiveConversationId(null);
        setMessages([]);
      }
      fetchConversations();
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 4rem)', gap: '1rem' }}>
      <ConversationList
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={setActiveConversationId}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
      />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div style={{ flex: 1, overflowY: 'auto', paddingRight: '0.5rem' }}>
          {messages.length === 0 ? (
            <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#64748b', textAlign: 'center' }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', marginBottom: '0.5rem' }}>
                AI Customer Support Console
              </h2>
              <p style={{ maxWidth: '440px', fontSize: '0.875rem' }}>
                Ask grounded queries across your uploaded knowledge base documents or attach error screenshots for VLM multi-modal diagnosis.
              </p>
            </div>
          ) : (
            messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
          )}
          <div ref={messagesEndRef} />
        </div>

        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};
