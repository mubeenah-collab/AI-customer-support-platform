import React, { useState, useRef } from 'react';
import { Send, Image, X, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (content: string, imageFile?: File) => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [content, setContent] = useState('');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => setImagePreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if ((!content.trim() && !selectedImage) || isLoading) return;

    onSendMessage(content, selectedImage || undefined);
    setContent('');
    removeImage();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="glass-card" style={{ padding: '1rem', marginTop: 'auto' }}>
      {imagePreview && (
        <div style={{ position: 'relative', display: 'inline-block', marginBottom: '0.75rem' }}>
          <img src={imagePreview} alt="Attached preview" style={{ width: '64px', height: '64px', borderRadius: '0.5rem', objectFit: 'cover' }} />
          <button
            onClick={removeImage}
            style={{
              position: 'absolute',
              top: '-6px',
              right: '-6px',
              backgroundColor: '#ef4444',
              color: '#ffffff',
              borderRadius: '50%',
              width: '20px',
              height: '20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: 'none',
              cursor: 'pointer',
            }}
          >
            <X size={12} />
          </button>
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', alignItems: 'flex-end', gap: '0.75rem' }}>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleImageSelect}
          accept="image/png,image/jpeg,image/webp"
          style={{ display: 'none' }}
        />

        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          style={{
            background: 'rgba(30, 41, 59, 0.8)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            color: selectedImage ? '#818cf8' : '#94a3b8',
            padding: '0.75rem',
            borderRadius: '0.75rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          title="Attach Image for VLM Processing"
        >
          <Image size={20} />
        </button>

        <textarea
          rows={1}
          className="input-field"
          placeholder="Ask a customer support question..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          style={{ resize: 'none', minHeight: '46px', maxHeight: '120px', padding: '0.75rem 1rem' }}
        />

        <button
          type="submit"
          className="btn-primary"
          disabled={isLoading || (!content.trim() && !selectedImage)}
          style={{ padding: '0.75rem 1.25rem', opacity: isLoading || (!content.trim() && !selectedImage) ? 0.6 : 1 }}
        >
          {isLoading ? <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} /> : <Send size={20} />}
        </button>
      </form>
    </div>
  );
};
