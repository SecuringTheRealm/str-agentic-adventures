import React, { useState, useEffect } from "react";
import { Campaign, getCampaigns, deleteCampaign } from "../services/api";
import CampaignGallery from "./CampaignGallery";
import CampaignEditor from "./CampaignEditor";
import styles from "./CampaignSelection.module.css";

interface CampaignSelectionProps {
  onCampaignCreated: (campaign: Campaign) => void;
}

type ViewMode = "gallery" | "editor" | "list";

const CampaignSelection: React.FC<CampaignSelectionProps> = ({
  onCampaignCreated,
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>("gallery");
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(
    null
  );
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Cache filtered custom campaigns to avoid repeated filtering
  const customCampaigns = campaigns.filter((c) => c.is_custom || false);

  const loadCampaigns = async () => {
    try {
      setLoading(true);
      const data = await getCampaigns();
      setCampaigns(data.campaigns);
    } catch (err) {
      setError("Failed to load campaigns");
      console.error("Error loading campaigns:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCampaigns();
  }, []);

  const handleCampaignSelected = (campaign: Campaign) => {
    onCampaignCreated(campaign);
  };

  const handleCreateCustom = () => {
    setSelectedCampaign(null);
    setViewMode("editor");
  };

  const handleEditCampaign = (campaign: Campaign) => {
    setSelectedCampaign(campaign);
    setViewMode("editor");
  };

  const handleCampaignSaved = async (campaign: Campaign) => {
    // Refresh campaigns list
    await loadCampaigns();

    // If this was a new campaign creation, pass it up
    if (!selectedCampaign) {
      onCampaignCreated(campaign);
    } else {
      // If editing, go back to list view
      setViewMode("list");
      setSelectedCampaign(null);
    }
  };

  const handleCancelEdit = () => {
    setSelectedCampaign(null);
    setViewMode("gallery");
  };

  const handleDeleteCampaign = async (campaignId: string) => {
    if (!window.confirm("Are you sure you want to delete this campaign?")) {
      return;
    }

    try {
      await deleteCampaign(campaignId);
      await loadCampaigns();
    } catch (err) {
      setError("Failed to delete campaign");
      console.error("Error deleting campaign:", err);
    }
  };

  const handleBackToGallery = () => {
    setViewMode("gallery");
    setSelectedCampaign(null);
  };

  if (viewMode === "editor") {
    return (
      <CampaignEditor
        campaign={selectedCampaign || undefined}
        onCampaignSaved={handleCampaignSaved}
        onCancel={handleCancelEdit}
      />
    );
  }

  if (viewMode === "list") {
    return (
      <div className={styles.campaignManager}>
        <div className={styles.managerHeader}>
          <h2>My Campaigns</h2>
          <div className={styles.headerActions}>
            <button
              className="action-button secondary"
              onClick={handleBackToGallery}
            >
              ← Browse Templates
            </button>
            <button
              className="action-button primary"
              onClick={handleCreateCustom}
            >
              + Create New
            </button>
          </div>
        </div>

        {error && (
          <div className={styles.errorMessage}>
            {error}
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        {loading ? (
          <div className={styles.loadingState}>
            <div className={styles.loadingSpinner}></div>
            <p>Loading campaigns...</p>
          </div>
        ) : (
          <div className={styles.campaignList}>
            {customCampaigns.length === 0 ? (
              <div className={styles.emptyState}>
                <div className={styles.emptyIcon}>📚</div>
                <h3>No Custom Campaigns Yet</h3>
                <p>
                  Create your first custom campaign or select a template to get
                  started!
                </p>
                <button
                  className="action-button primary"
                  onClick={handleBackToGallery}
                >
                  Browse Templates
                </button>
              </div>
            ) : (
              customCampaigns.map((campaign) => (
                <div key={campaign.id} className={styles.campaignItem}>
                  <div className={styles.campaignInfo}>
                    <h3>{campaign.name}</h3>
                    <p className={styles.campaignDescription}>
                      {campaign.description || campaign.setting}
                    </p>
                    <div className={styles.campaignMeta}>
                      <span className={`tone-badge ${campaign.tone}`}>
                        {campaign.tone}
                      </span>
                      {campaign.template_id && (
                        <span className={styles.cloneBadge}>
                          Cloned from template
                        </span>
                      )}
                    </div>
                  </div>
                  <div className={styles.campaignActions}>
                    <button
                      className="action-button primary small"
                      onClick={() => handleCampaignSelected(campaign)}
                    >
                      Play
                    </button>
                    <button
                      className="action-button secondary small"
                      onClick={() => handleEditCampaign(campaign)}
                    >
                      Edit
                    </button>
                    <button
                      className="action-button danger small"
                      onClick={() => handleDeleteCampaign(campaign.id!)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={styles.campaignManager}>
      <div className={styles.managerHeader}>
        <div className={styles.headerContent}>
          <h2 className={styles.sectionTitle}>Campaign Hub</h2>
          <p>
            Choose from our curated templates or manage your custom campaigns
          </p>
        </div>
        <div className={styles.headerActions}>
          <button
            className={`view-toggle ${viewMode === "gallery" ? "active" : ""}`}
            onClick={() => setViewMode("gallery")}
          >
            Gallery
          </button>
          <button
            className={`view-toggle ${(viewMode as string) === "list" ? "active" : ""}`}
            onClick={() => setViewMode("list")}
          >
            My Campaigns ({customCampaigns.length})
          </button>
        </div>
      </div>

      {error && (
        <div className={styles.errorMessage}>
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {viewMode === "gallery" ? (
        <CampaignGallery
          onCampaignSelected={handleCampaignSelected}
          onCreateCustom={handleCreateCustom}
        />
      ) : (
        <div className={styles.campaignList}>
          {customCampaigns.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>📚</div>
              <h3>No Custom Campaigns Yet</h3>
              <p>
                Create your first custom campaign or select a template to get
                started!
              </p>
              <button
                className="action-button primary"
                onClick={handleBackToGallery}
              >
                Browse Templates
              </button>
            </div>
          ) : (
            customCampaigns.map((campaign) => (
              <div key={campaign.id} className={styles.campaignItem}>
                <div className={styles.campaignInfo}>
                  <h3>{campaign.name}</h3>
                  <p className={styles.campaignDescription}>
                    {campaign.description || campaign.setting}
                  </p>
                  <div className={styles.campaignMeta}>
                    <span className={`tone-badge ${campaign.tone}`}>
                      {campaign.tone}
                    </span>
                    {campaign.template_id && (
                      <span className={styles.cloneBadge}>
                        Cloned from template
                      </span>
                    )}
                  </div>
                </div>
                <div className={styles.campaignActions}>
                  <button
                    className="action-button primary small"
                    onClick={() => handleCampaignSelected(campaign)}
                  >
                    Play
                  </button>
                  <button
                    className="action-button secondary small"
                    onClick={() => handleEditCampaign(campaign)}
                  >
                    Edit
                  </button>
                  <button
                    className="action-button danger small"
                    onClick={() => handleDeleteCampaign(campaign.id!)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default CampaignSelection;
