import React, { useState, useEffect } from 'react';
import { 
  Campaign, 
  CampaignCreateRequest, 
  CampaignUpdateRequest,
  createCampaign, 
  updateCampaign,
  getAIAssistance,
  AIAssistanceRequest
} from '../services/api';
import './CampaignEditor.css';

interface CampaignEditorProps {
  campaign?: Campaign;
  onCampaignSaved: (campaign: Campaign) => void;
  onCancel: () => void;
}

const CampaignEditor: React.FC<CampaignEditorProps> = ({
  campaign,
  onCampaignSaved,
  onCancel,
}) => {
  const [formData, setFormData] = useState({
    name: campaign?.name || '',
    description: campaign?.description || '',
    setting: campaign?.setting || '',
    tone: campaign?.tone || 'heroic',
    homebrew_rules: campaign?.homebrew_rules?.join('\n') || '',
    world_description: campaign?.world_description || '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [showAIAssistant, setShowAIAssistant] = useState(false);
  const [aiSuggestions, setAISuggestions] = useState<string[]>([]);
  const [activeField, setActiveField] = useState<string | null>(null);
  const [aiLoading, setAILoading] = useState(false);
  const [autoSave, setAutoSave] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const isEditing = !!campaign;

  // Auto-save functionality
  useEffect(() => {
    if (autoSave && hasUnsavedChanges && isEditing) {
      const timeoutId = setTimeout(async () => {
        await handleSave(true); // silent save
      }, 3000);
      return () => clearTimeout(timeoutId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData, autoSave, hasUnsavedChanges, isEditing]);

  // Track changes
  useEffect(() => {
    if (isEditing) {
      const hasChanges = (
        formData.name !== (campaign?.name || '') ||
        formData.description !== (campaign?.description || '') ||
        formData.setting !== (campaign?.setting || '') ||
        formData.tone !== (campaign?.tone || 'heroic') ||
        formData.homebrew_rules !== (campaign?.homebrew_rules?.join('\n') || '') ||
        formData.world_description !== (campaign?.world_description || '')
      );
      setHasUnsavedChanges(hasChanges);
    }
  }, [formData, campaign, isEditing]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setValidationErrors(prev => ({ ...prev, [field]: '' }));
    setError(null);
  };

  const handleFormatText = (field: string, format: 'bold' | 'italic' | 'header' | 'list') => {
    const textarea = document.getElementById(field) as HTMLTextAreaElement;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    const beforeText = textarea.value.substring(0, start);
    const afterText = textarea.value.substring(end);

    let formattedText = '';
    switch (format) {
      case 'bold':
        formattedText = `**${selectedText || 'bold text'}**`;
        break;
      case 'italic':
        formattedText = `*${selectedText || 'italic text'}*`;
        break;
      case 'header':
        formattedText = `## ${selectedText || 'Header'}`;
        break;
      case 'list':
        formattedText = selectedText 
          ? selectedText.split('\n').map(line => `- ${line}`).join('\n')
          : '- List item';
        break;
    }

    const newValue = beforeText + formattedText + afterText;
    handleInputChange(field, newValue);

    // Restore focus and selection
    setTimeout(() => {
      textarea.focus();
      const newStart = start + formattedText.length;
      textarea.setSelectionRange(newStart, newStart);
    }, 0);
  };

  const handleAIAssist = async (field: string, contextType: string) => {
    setActiveField(field);
    setAILoading(true);
    setShowAIAssistant(true);

    try {
      const request: AIAssistanceRequest = {
        text: formData[field as keyof typeof formData],
        context_type: contextType,
        campaign_tone: formData.tone,
      };

      const response = await getAIAssistance(request);
      setAISuggestions(response.suggestions);
    } catch (err) {
      console.error('Error getting AI assistance:', err);
      setAISuggestions(['Unable to get AI suggestions at this time.']);
    } finally {
      setAILoading(false);
    }
  };

  const applySuggestion = (suggestion: string) => {
    if (activeField) {
      const currentValue = formData[activeField as keyof typeof formData];
      const enhancedValue = currentValue ? `${currentValue}\n\n${suggestion}` : suggestion;
      handleInputChange(activeField, enhancedValue);
    }
    setShowAIAssistant(false);
  };

  const validateForm = () => {
    const errors: Record<string, string> = {};
    
    if (!formData.name.trim()) {
      errors.name = 'Campaign name is required';
    }
    
    if (!formData.setting.trim()) {
      errors.setting = 'Campaign setting is required';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = async (silent = false) => {
    if (!validateForm() && !silent) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const homebrewRulesList = formData.homebrew_rules
        .split('\n')
        .map(rule => rule.trim())
        .filter(rule => rule !== '');

      if (isEditing && campaign) {
        const updates: CampaignUpdateRequest = {
          name: formData.name.trim(),
          description: formData.description.trim() || undefined,
          setting: formData.setting.trim(),
          tone: formData.tone,
          homebrew_rules: homebrewRulesList,
          world_description: formData.world_description.trim() || undefined,
        };

        const updatedCampaign = await updateCampaign(campaign.id, updates);
        onCampaignSaved(updatedCampaign);
        setHasUnsavedChanges(false);
        
        if (!silent) {
          // Show success message briefly
          const originalName = formData.name;
          setFormData(prev => ({ ...prev, name: '✓ Saved!' }));
          setTimeout(() => setFormData(prev => ({ ...prev, name: originalName })), 1000);
        }
      } else {
        const campaignData: CampaignCreateRequest = {
          name: formData.name.trim(),
          description: formData.description.trim() || undefined,
          setting: formData.setting.trim(),
          tone: formData.tone,
          homebrew_rules: homebrewRulesList,
        };

        const newCampaign = await createCampaign(campaignData);
        onCampaignSaved(newCampaign);
      }
    } catch (err) {
      setError(isEditing ? 'Failed to update campaign' : 'Failed to create campaign');
      console.error('Error saving campaign:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="campaign-editor">
      <div className="editor-header">
        <h2>{isEditing ? 'Edit Campaign' : 'Create Custom Campaign'}</h2>
        {isEditing && (
          <div className="editor-controls">
            <label className="auto-save-toggle">
              <input
                type="checkbox"
                checked={autoSave}
                onChange={(e) => setAutoSave(e.target.checked)}
              />
              Auto-save
            </label>
            {hasUnsavedChanges && (
              <span className="unsaved-indicator">● Unsaved changes</span>
            )}
          </div>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={(e) => { e.preventDefault(); handleSave(); }}>
        <div className="form-group">
          <label htmlFor="name">Campaign Name *</label>
          <input
            id="name"
            type="text"
            value={formData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            placeholder="Enter campaign name..."
            className={validationErrors.name ? 'error' : ''}
            disabled={isSubmitting}
          />
          {validationErrors.name && (
            <div className="validation-error">{validationErrors.name}</div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="description">Description</label>
          <div className="editor-toolbar">
            <button 
              type="button" 
              onClick={() => handleFormatText('description', 'bold')}
              title="Bold"
            >
              <strong>B</strong>
            </button>
            <button 
              type="button" 
              onClick={() => handleFormatText('description', 'italic')}
              title="Italic"
            >
              <em>I</em>
            </button>
            <button 
              type="button" 
              onClick={() => handleFormatText('description', 'header')}
              title="Header"
            >
              H
            </button>
            <button 
              type="button" 
              onClick={() => handleFormatText('description', 'list')}
              title="List"
            >
              •
            </button>
            <button 
              type="button" 
              onClick={() => handleAIAssist('description', 'description')}
              className="ai-assist-btn"
              title="AI Assistance"
            >
              ✨ AI
            </button>
          </div>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            placeholder="Brief description of your campaign..."
            rows={3}
            disabled={isSubmitting}
          />
        </div>

        <div className="form-group">
          <label htmlFor="setting">Campaign Setting *</label>
          <div className="editor-toolbar">
            <button 
              type="button" 
              onClick={() => handleFormatText('setting', 'bold')}
              title="Bold"
            >
              <strong>B</strong>
            </button>
            <button 
              type="button" 
              onClick={() => handleFormatText('setting', 'italic')}
              title="Italic"
            >
              <em>I</em>
            </button>
            <button 
              type="button" 
              onClick={() => handleFormatText('setting', 'header')}
              title="Header"
            >
              H
            </button>
            <button 
              type="button" 
              onClick={() => handleFormatText('setting', 'list')}
              title="List"
            >
              •
            </button>
            <button 
              type="button" 
              onClick={() => handleAIAssist('setting', 'setting')}
              className="ai-assist-btn"
              title="AI Assistance"
            >
              ✨ AI
            </button>
          </div>
          <textarea
            id="setting"
            value={formData.setting}
            onChange={(e) => handleInputChange('setting', e.target.value)}
            placeholder="Describe the world and setting for your campaign..."
            rows={4}
            className={validationErrors.setting ? 'error' : ''}
            disabled={isSubmitting}
          />
          {validationErrors.setting && (
            <div className="validation-error">{validationErrors.setting}</div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="world_description">World Description</label>
          <div className="editor-toolbar">
            <button 
              type="button" 
              onClick={() => handleFormatText('world_description', 'bold')}
              title="Bold"
            >
              <strong>B</strong>
            </button>
            <button 
              type="button" 
              onClick={() => handleFormatText('world_description', 'italic')}
              title="Italic"
            >
              <em>I</em>
            </button>
            <button 
              type="button" 
              onClick={() => handleFormatText('world_description', 'header')}
              title="Header"
            >
              H
            </button>
            <button 
              type="button" 
              onClick={() => handleFormatText('world_description', 'list')}
              title="List"
            >
              •
            </button>
            <button 
              type="button" 
              onClick={() => handleAIAssist('world_description', 'description')}
              className="ai-assist-btn"
              title="AI Assistance"
            >
              ✨ AI
            </button>
          </div>
          <textarea
            id="world_description"
            value={formData.world_description}
            onChange={(e) => handleInputChange('world_description', e.target.value)}
            placeholder="Detailed world description, lore, and background..."
            rows={6}
            disabled={isSubmitting}
          />
        </div>

        <div className="form-group">
          <label htmlFor="tone">Campaign Tone</label>
          <select
            id="tone"
            value={formData.tone}
            onChange={(e) => handleInputChange('tone', e.target.value)}
            disabled={isSubmitting}
          >
            <option value="heroic">🛡️ Heroic</option>
            <option value="dark">💀 Dark</option>
            <option value="lighthearted">🃏 Lighthearted</option>
            <option value="gritty">⚔️ Gritty</option>
            <option value="mysterious">🔍 Mysterious</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="homebrew_rules">Homebrew Rules (Optional)</label>
          <textarea
            id="homebrew_rules"
            value={formData.homebrew_rules}
            onChange={(e) => handleInputChange('homebrew_rules', e.target.value)}
            placeholder="One rule per line..."
            rows={3}
            disabled={isSubmitting}
          />
          <div className="help-text">
            Enter each homebrew rule on a separate line
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            onClick={onCancel}
            className="cancel-button"
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="save-button"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <span className="loading-spinner small"></span>
                {isEditing ? 'Updating...' : 'Creating...'}
              </>
            ) : (
              isEditing ? 'Update Campaign' : 'Create Campaign'
            )}
          </button>
        </div>
      </form>

      {/* AI Assistant Modal */}
      {showAIAssistant && (
        <div className="ai-assistant-modal">
          <div className="modal-overlay" onClick={() => setShowAIAssistant(false)} />
          <div className="modal-content">
            <div className="modal-header">
              <h3>✨ AI Writing Assistant</h3>
              <button 
                className="close-button"
                onClick={() => setShowAIAssistant(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              {aiLoading ? (
                <div className="loading-state">
                  <div className="loading-spinner"></div>
                  <p>Getting suggestions...</p>
                </div>
              ) : (
                <div className="suggestions">
                  <h4>Suggestions:</h4>
                  <ul>
                    {aiSuggestions.map((suggestion, index) => (
                      <li key={index}>
                        <span>{suggestion}</span>
                        <button
                          onClick={() => applySuggestion(suggestion)}
                          className="apply-suggestion"
                        >
                          Apply
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CampaignEditor;