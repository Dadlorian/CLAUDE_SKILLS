/**
 * Secure Patient-Provider Communication System
 * Encrypted messaging between patients and care team
 */

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

class SecureMessagingService {
  constructor(patientId, token) {
    this.patientId = patientId;
    this.token = token;
    this.api = axios.create({
      headers: { Authorization: `Bearer ${token}` }
    });
  }

  async sendMessage(recipientId, messageText, attachments = []) {
    const payload = {
      sender_id: this.patientId,
      recipient_id: recipientId,
      message: messageText,
      attachments: attachments,
      timestamp: new Date().toISOString(),
      read: false
    };

    const response = await this.api.post('/api/messages', payload);
    return response.data;
  }

  async getConversation(providerId) {
    const response = await this.api.get(
      `/api/messages/conversations/${providerId}`
    );
    return response.data;
  }

  async markAsRead(messageId) {
    await this.api.put(`/api/messages/${messageId}/read`);
  }

  async searchMessages(query) {
    const response = await this.api.get(
      `/api/messages/search?q=${query}`
    );
    return response.data;
  }
}

const SecureMessagingInterface = ({ patientId, token }) => {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const messagingService = new SecureMessagingService(patientId, token);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadConversations();
    const interval = setInterval(loadConversations, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedConversation) {
      loadMessages(selectedConversation.id);
    }
  }, [selectedConversation]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadConversations = async () => {
    try {
      const response = await fetch(`/api/messages/conversations`);
      const data = await response.json();
      setConversations(data.conversations);
    } catch (error) {
      console.error('Error loading conversations:', error);
    }
  };

  const loadMessages = async (conversationId) => {
    try {
      const response = await fetch(`/api/messages/${conversationId}`);
      const data = await response.json();
      setMessages(data.messages);

      // Mark as read
      data.messages.forEach(msg => {
        if (!msg.read && msg.recipient_id === patientId) {
          messagingService.markAsRead(msg.id);
        }
      });
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const sendMessage = async () => {
    if (!messageText.trim() || !selectedConversation) return;

    try {
      const message = await messagingService.sendMessage(
        selectedConversation.provider_id,
        messageText
      );

      setMessages([...messages, message]);
      setMessageText('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadConversations();
      return;
    }

    try {
      const results = await messagingService.searchMessages(searchQuery);
      setConversations(results);
    } catch (error) {
      console.error('Error searching messages:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="secure-messaging">
      <div className="conversations-panel">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
        </div>

        <div className="conversations-list">
          {conversations.map(conv => (
            <ConversationItem
              key={conv.id}
              conversation={conv}
              isSelected={selectedConversation?.id === conv.id}
              onClick={() => setSelectedConversation(conv)}
            />
          ))}
        </div>
      </div>

      <div className="messages-panel">
        {selectedConversation ? (
          <>
            <div className="conversation-header">
              <h3>{selectedConversation.provider_name}</h3>
              <p>{selectedConversation.specialty}</p>
            </div>

            <div className="messages-container">
              {messages.length === 0 ? (
                <p className="no-messages">No messages yet. Start a conversation.</p>
              ) : (
                messages.map(msg => (
                  <MessageBubble
                    key={msg.id}
                    message={msg}
                    isOwn={msg.sender_id === patientId}
                  />
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="message-input-area">
              <textarea
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                placeholder="Type your message here..."
                onKeyPress={(e) => {
                  if (e.ctrlKey && e.key === 'Enter') {
                    sendMessage();
                  }
                }}
              />
              <button onClick={sendMessage} className="send-button">
                Send (Ctrl+Enter)
              </button>
            </div>
          </>
        ) : (
          <div className="no-conversation-selected">
            <p>Select a conversation to start messaging</p>
          </div>
        )}
      </div>
    </div>
  );
};

const ConversationItem = ({ conversation, isSelected, onClick }) => {
  const lastMessage = conversation.last_message;
  const unreadCount = conversation.unread_count;

  return (
    <div
      className={`conversation-item ${isSelected ? 'selected' : ''} ${unreadCount > 0 ? 'unread' : ''}`}
      onClick={onClick}
    >
      <div className="conversation-avatar">
        {conversation.provider_initials}
      </div>

      <div className="conversation-content">
        <h4>{conversation.provider_name}</h4>
        <p className="last-message">
          {lastMessage?.substring(0, 50)}...
        </p>
        <p className="timestamp">
          {formatTime(conversation.last_message_time)}
        </p>
      </div>

      {unreadCount > 0 && (
        <div className="unread-badge">{unreadCount}</div>
      )}
    </div>
  );
};

const MessageBubble = ({ message, isOwn }) => {
  const timestamp = new Date(message.timestamp);

  return (
    <div className={`message-bubble ${isOwn ? 'own' : 'other'}`}>
      <div className="message-content">
        <p className="message-text">{message.message}</p>

        {message.attachments && message.attachments.length > 0 && (
          <div className="attachments">
            {message.attachments.map((att, i) => (
              <a
                key={i}
                href={att.url}
                download
                className="attachment"
              >
                {att.filename}
              </a>
            ))}
          </div>
        )}
      </div>

      <span className="message-time">
        {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </span>

      {isOwn && message.read && (
        <span className="read-indicator">Read</span>
      )}
    </div>
  );
};

function formatTime(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString();
}

export { SecureMessagingInterface, SecureMessagingService };
