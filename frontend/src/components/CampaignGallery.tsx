import React, { useState, useEffect } from 'react';
import { Campaign, getCampaignTemplates, cloneCampaign } from '../services/api';
import styles from './CampaignGallery.module.css';

interface CampaignGalleryProps {
  onCampaignSelected: (campaign: Campaign) => void;
  onCreateCustom: () => void;
}

const CampaignGallery: React.FC<CampaignGalleryProps> = ({
  onCampaignSelected,
  onCreateCustom,
}) => {
  const [templates, setTemplates] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cloning, setCloning] = useState<string | null>(null);

  useEffect(() => {
    const loadTemplates = async () => {
      try {
        setLoading(true);
        const templateData = await getCampaignTemplates();
        setTemplates(templateData);
      } catch (err) {
        setError('Failed to load campaign templates');
        console.error('Error loading templates:', err);
      } finally {
        setLoading(false);
      }
    };

    loadTemplates();
  }, []);

  const handleSelectTemplate = async (template: Campaign) => {
    try {
      setCloning(template.id!);
      const clonedCampaign = await cloneCampaign({
        template_id: template.id!,
        new_name: `${template.name} (My Campaign)`
      });
      onCampaignSelected(clonedCampaign);
    } catch (err) {
      setError('Failed to clone campaign template');
      console.error('Error cloning template:', err);
    } finally {
      setCloning(null);
    }
  };

  if (loading) {
    return (
      <div className={`${styles.campaignGallery} ${styles.loading}`}>
        <div className={styles.loadingSpinner}></div>
        <p>Loading campaign templates...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${styles.campaignGallery} ${styles.error}`}>
        <div className={styles.errorMessage}>
          <h3>Error Loading Templates</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Try Again</button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.campaignGallery}>
      <header className={styles.galleryHeader}>
        <h2>Choose Your Adventure</h2>
        <p>Select from our curated campaign templates or create your own custom campaign</p>
      </header>

      <div className={styles.campaignOptions}>
        <div className={styles.customCampaignCard}>
          <div className={styles.cardContent}>
            <div className={styles.cardIcon}>✨</div>
            <h3>Create Custom Campaign</h3>
            <p>Start from scratch with your own unique world and story</p>
            <button 
              className={`${styles.selectButton} ${styles.custom}`}
              onClick={onCreateCustom}
            >
              Create Custom
            </button>
          </div>
        </div>

        {templates.map((template) => (
          <div key={template.id} className={styles.campaignCard}>
            <div className={styles.cardContent}>
              <div className={styles.cardHeader}>
                <h3>{template.name}</h3>
                <span className={`${styles.toneBadge} ${template.tone ? styles[template.tone] : ''}`}>
                  {template.tone}
                </span>
              </div>
              
              <p className={styles.cardDescription}>
                {template.description || 'An exciting adventure awaits!'}
              </p>
              
              <div className={styles.cardDetails}>
                <div className={styles.detailItem}>
                  <strong>Setting:</strong>
                  <span>{template.setting.substring(0, 100)}...</span>
                </div>
                
                {template.plot_hooks && template.plot_hooks.length > 0 && (
                  <div className={styles.detailItem}>
                    <strong>Plot Hooks:</strong>
                    <ul>
                      {template.plot_hooks.slice(0, 2).map((hook, index) => (
                        <li key={index}>{hook}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {template.homebrew_rules && template.homebrew_rules.length > 0 && (
                  <div className={styles.detailItem}>
                    <strong>Special Rules:</strong>
                    <span>{template.homebrew_rules.length} custom rule(s)</span>
                  </div>
                )}
              </div>
              
              <button 
                className={styles.selectButton}
                onClick={() => handleSelectTemplate(template)}
                disabled={cloning === template.id}
              >
                {cloning === template.id ? (
                  <>
                    <span className={`${styles.loadingSpinner} ${styles.small}`}></span>
                    Preparing...
                  </>
                ) : (
                  'Select Campaign'
                )}
              </button>
            </div>
          </div>
        ))}
      </div>

      {templates.length === 0 && (
        <div className={styles.noTemplates}>
          <h3>No Templates Available</h3>
          <p>Create a custom campaign to get started!</p>
          <button className={styles.selectButton} onClick={onCreateCustom}>
            Create Custom Campaign
          </button>
        </div>
      )}
    </div>
  );
};

export default CampaignGallery;