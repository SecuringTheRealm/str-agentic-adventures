import React, { useState, useEffect } from 'react';
import { 
  Campaign, 
  CampaignCreateRequest, 
  CampaignUpdateRequest,
  createCampaign, 
  updateCampaign,
  getAIAssistance,
  generateAIContent,
  AIAssistanceRequest,
  AIContentGenerationRequest,
  APIError
} from '../services/api';
import styles from "./CampaignEditor.module.css";

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
  const [errorDetails, setErrorDetails] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [showAIAssistant, setShowAIAssistant] = useState(false);
  const [aiSuggestions, setAISuggestions] = useState<string[]>([]);
  const [activeField, setActiveField] = useState<string | null>(null);
  const [aiLoading, setAILoading] = useState(false);
  const [aiGenerating, setAIGenerating] = useState(false);
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

  const applySuggestion = async (suggestion: string) => {
    if (!activeField) return;
    
    // Check if field is empty or has only placeholder content
    const currentValue = formData[activeField as keyof typeof formData];
    const isEmpty = !currentValue || currentValue.trim() === '';
    
    // Enhanced placeholder content detection
    const isPlaceholderContent = (() => {
      if (isEmpty) return true;
      
      const lowerValue = currentValue.toLowerCase().trim();
      
      // Check for common placeholder patterns
      const placeholderPatterns = [
        /^(enter|add|type|write)\s+/,
        /\.\.\.\s*$/,
        /^placeholder/,
        /^example:/,
        /^sample/,
        /^todo:/,
        /^tbd$/,
        /^to be determined/,
        /^fill in/,
        /^coming soon/
      ];
      
      const isCommonPlaceholder = placeholderPatterns.some(pattern => 
        pattern.test(lowerValue)
      );
      
      // Check for field-specific placeholder content
      const fieldSpecificPlaceholders: Record<string, string[]> = {
        name: ['enter campaign name', 'campaign name', 'untitled campaign'],
        description: ['brief description', 'enter description', 'describe your campaign'],
        setting: ['describe the world', 'campaign setting', 'world description'],
        world_description: ['detailed world description', 'world details', 'background lore'],
        homebrew_rules: ['one rule per line', 'custom rules', 'homebrew modifications']
      };
      
      const fieldPlaceholders = fieldSpecificPlaceholders[activeField] || [];
      const hasFieldPlaceholder = fieldPlaceholders.some(placeholder =>
        lowerValue.includes(placeholder.toLowerCase())
      );
      
      // Check for very short content that might be placeholder-like
      const isTooShort = currentValue.trim().length < 10 && 
        !/\w+/.test(currentValue); // Contains actual words
      
      return isCommonPlaceholder || hasFieldPlaceholder || isTooShort;
    })();
    
    // Disable apply for empty fields or placeholder content
    if (isPlaceholderContent) {
      return;
    }
    
    setAIGenerating(true);
    
    try {
      const request: AIContentGenerationRequest = {
        suggestion: suggestion,
        current_text: currentValue,
        context_type: getContextTypeForField(activeField),
        campaign_tone: formData.tone,
      };
      
      const response = await generateAIContent(request);
      
      if (response.success && response.generated_content) {
        // Insert the generated content, respecting existing text
        const enhancedValue = currentValue ? 
          `${currentValue}\n\n${response.generated_content}` : 
          response.generated_content;
        handleInputChange(activeField, enhancedValue);
      } else {
        console.error('AI content generation failed:', response.error);
        // Fallback to the old behavior if generation fails
        const enhancedValue = currentValue ? `${currentValue}\n\n${suggestion}` : suggestion;
        handleInputChange(activeField, enhancedValue);
      }
    } catch (error) {
      console.error('Error generating AI content:', error);
      // Fallback to the old behavior if request fails
      const enhancedValue = currentValue ? `${currentValue}\n\n${suggestion}` : suggestion;
      handleInputChange(activeField, enhancedValue);
    } finally {
      setAIGenerating(false);
      setShowAIAssistant(false);
    }
  };
  
  const getContextTypeForField = (field: string): string => {
    switch (field) {
      case 'setting':
        return 'setting';
      case 'description':
        return 'description';
      case 'world_description':
        return 'description';
      default:
        return 'description';
    }
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

        const updatedCampaign = await updateCampaign(campaign.id!, updates);
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
      if (err instanceof APIError) {
        setError(err.message);
        setErrorDetails(err.details || null);
      } else {
        setError(isEditing ? 'Failed to update campaign' : 'Failed to create campaign');
        setErrorDetails(null);
      }
      console.error('Error saving campaign:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.campaignEditor}>
      <div className={styles.editorHeader}>
        <h2>{isEditing ? 'Edit Campaign' : 'Create Custom Campaign'}</h2>
        {isEditing && (
          <div className={styles.editorControls}>
            <label className={styles.autoSaveToggle}>
              <input
                type="checkbox"
                checked={autoSave}
                onChange={(e) => setAutoSave(e.target.checked)}
              />
              Auto-save
            </label>
            {hasUnsavedChanges && (
              <span className={styles.unsavedIndicator}>● Unsaved changes</span>
            )}
          </div>
        )}
      </div>

      {error && (
        <div className={styles.errorMessage}>
          <p>{error}</p>
          {errorDetails && (
            <details className={styles.errorDetails}>
              <summary>Technical Details</summary>
              <p>{errorDetails}</p>
            </details>
          )}
        </div>
      )}

      <form onSubmit={(e) => { e.preventDefault(); handleSave(); }}>
        <div className={styles.formGroup}>
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
            <div className={styles.validationError}>{validationErrors.name}</div>
          )}
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="description">Description</label>
          <div className={styles.editorToolbar}>
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
              className={styles.aiAssistBtn}
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

        <div className={styles.formGroup}>
          <label htmlFor="setting">Campaign Setting *</label>
          <div className={styles.editorToolbar}>
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
              className={styles.aiAssistBtn}
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
            <div className={styles.validationError}>{validationErrors.setting}</div>
          )}
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="world_description">World Description</label>
          <div className={styles.editorToolbar}>
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
              className={styles.aiAssistBtn}
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

        <div className={styles.formGroup}>
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

        <div className={styles.formGroup}>
          <label htmlFor="homebrew_rules">Homebrew Rules (Optional)</label>
          <textarea
            id="homebrew_rules"
            value={formData.homebrew_rules}
            onChange={(e) => handleInputChange('homebrew_rules', e.target.value)}
            placeholder="One rule per line..."
            rows={3}
            disabled={isSubmitting}
          />
          <div className={styles.helpText}>
            Enter each homebrew rule on a separate line
          </div>
        </div>

        <div className={styles.formActions}>
          <button
            type="button"
            onClick={onCancel}
            className={styles.cancelButton}
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className={styles.saveButton}
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
        <div className={styles.aiAssistantModal}>
          <div className={styles.modalOverlay} onClick={() => setShowAIAssistant(false)} />
          <div className={styles.modalContent}>
            <div className={styles.modalHeader}>
              <h3>✨ AI Writing Assistant</h3>
              <button 
                className={styles.closeButton}
                onClick={() => setShowAIAssistant(false)}
              >
                ×
              </button>
            </div>
            <div className={styles.modalBody}>
              {aiLoading ? (
                <div className={styles.loadingState}>
                  <div className={styles.loadingSpinner}></div>
                  <p>Getting suggestions...</p>
                </div>
              ) : (
                <div className={styles.suggestions}>
                  <h4>Suggestions:</h4>
                  <ul>
                    {aiSuggestions.map((suggestion, index) => {
                      const currentValue = activeField ? formData[activeField as keyof typeof formData] : '';
                      const isEmpty = !currentValue || currentValue.trim() === '';
                      
                      return (
                        <li key={index}>
                          <span>{suggestion}</span>
                          <button
                            onClick={() => applySuggestion(suggestion)}
                            className={styles.applySuggestion}
                            disabled={aiGenerating || isEmpty}
                            title={isEmpty ? "Cannot apply to empty field" : "Generate AI content based on this suggestion"}
                          >
                            {aiGenerating ? (
                              <>
                                <span className="loading-spinner small"></span>
                                Generating...
                              </>
                            ) : (
                              'Apply'
                            )}
                          </button>
                        </li>
                      );
                    })}
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