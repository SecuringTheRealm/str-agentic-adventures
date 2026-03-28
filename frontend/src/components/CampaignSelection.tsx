import type React from "react";
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { deleteCampaign, getCampaigns } from "../services/api";
import type { Campaign } from "../types";
import CampaignGallery from "./CampaignGallery";
import styles from "./CampaignSelection.module.css";
import ConfirmDialog from "./ConfirmDialog";

interface CampaignSelectionProps {
  onCampaignCreated: (campaign: Campaign) => void;
}

type ViewMode = "gallery" | "list";

const CampaignSelection: React.FC<CampaignSelectionProps> = ({
  onCampaignCreated,
}) => {
  const navigate = useNavigate();
  const [viewMode, setViewMode] = useState<ViewMode>("gallery");
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [campaignToDelete, setCampaignToDelete] = useState<string | null>(null);

  // Cache filtered custom campaigns to avoid repeated filtering
  const customCampaigns = campaigns.filter((c) => c.is_custom || false);

  const loadCampaigns = useCallback(async () => {
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
  }, []);

  useEffect(() => {
    loadCampaigns();
  }, [loadCampaigns]);

  const handleCampaignSelected = (campaign: Campaign) => {
    onCampaignCreated(campaign);
  };

  const handleCreateCustom = () => {
    navigate("/campaigns/new");
  };

  const handleEditCampaign = (campaign: Campaign) => {
    navigate(`/campaigns/${campaign.id}/edit`);
  };

  const handleDeleteCampaign = (campaignId: string) => {
    setCampaignToDelete(campaignId);
  };

  const handleConfirmDelete = async () => {
    if (!campaignToDelete) return;
    const idToDelete = campaignToDelete;
    setCampaignToDelete(null);
    try {
      await deleteCampaign(idToDelete);
      await loadCampaigns();
    } catch (err) {
      setError("Failed to delete campaign");
      console.error("Error deleting campaign:", err);
    }
  };

  const handleCancelDelete = () => {
    setCampaignToDelete(null);
  };

  const handleBackToGallery = () => {
    setViewMode("gallery");
  };

  if (viewMode === "list") {
    return (
      <>
        <div className={styles.campaignManager}>
          <div className={styles.managerHeader}>
            <h2>My Campaigns</h2>
            <div className={styles.headerActions}>
              <Button variant="secondary" onClick={handleBackToGallery}>
                ← Browse Templates
              </Button>
              <Button onClick={handleCreateCustom}>+ Create New</Button>
            </div>
          </div>

          {error && (
            <div className={styles.errorMessage}>
              {error}
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setError(null)}
              >
                ×
              </Button>
            </div>
          )}

          {loading ? (
            <div className={styles.loadingState}>
              <div className={styles.loadingSpinner} />
              <p>Loading campaigns...</p>
            </div>
          ) : (
            <div className={styles.campaignList}>
              {customCampaigns.length === 0 ? (
                <div className={styles.emptyState}>
                  <div className={styles.emptyIcon}>📚</div>
                  <h3>No Custom Campaigns Yet</h3>
                  <p>
                    Create your first custom campaign or select a template to
                    get started!
                  </p>
                  <Button onClick={handleBackToGallery}>
                    Browse Templates
                  </Button>
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
                        <Badge
                          variant="outline"
                          className={`tone-badge ${campaign.tone}`}
                        >
                          {campaign.tone}
                        </Badge>
                        {campaign.template_id && (
                          <Badge variant="secondary">
                            Cloned from template
                          </Badge>
                        )}
                      </div>
                    </div>
                    <div className={styles.campaignActions}>
                      <Button
                        size="sm"
                        onClick={() => handleCampaignSelected(campaign)}
                      >
                        Play
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleEditCampaign(campaign)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => {
                          if (!campaign.id) {
                            console.error(
                              "Cannot delete campaign: ID is missing"
                            );
                            return;
                          }
                          handleDeleteCampaign(campaign.id);
                        }}
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
        <ConfirmDialog
          isOpen={campaignToDelete !== null}
          title="Delete Campaign"
          message="Are you sure you want to delete this campaign? This action cannot be undone."
          onConfirm={handleConfirmDelete}
          onCancel={handleCancelDelete}
          confirmLabel="Delete"
          cancelLabel="Cancel"
        />
      </>
    );
  }

  return (
    <>
      <div className={styles.campaignManager}>
        <div className={styles.managerHeader}>
          <div className={styles.headerContent}>
            <h2 className={styles.sectionTitle}>Campaign Hub</h2>
            <p>
              Choose from our curated templates or manage your custom campaigns
            </p>
          </div>
          <div className={styles.headerActions}>
            <Button
              variant={viewMode === "gallery" ? "default" : "ghost"}
              onClick={() => setViewMode("gallery")}
            >
              Gallery
            </Button>
            <Button
              variant={(viewMode as string) === "list" ? "default" : "ghost"}
              onClick={() => setViewMode("list")}
            >
              My Campaigns ({customCampaigns.length})
            </Button>
          </div>
        </div>

        {error && (
          <div className={styles.errorMessage}>
            {error}
            <Button variant="ghost" size="icon" onClick={() => setError(null)}>
              ×
            </Button>
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
                <Button onClick={handleBackToGallery}>Browse Templates</Button>
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
                      <Badge
                        variant="outline"
                        className={`tone-badge ${campaign.tone}`}
                      >
                        {campaign.tone}
                      </Badge>
                      {campaign.template_id && (
                        <Badge variant="secondary">Cloned from template</Badge>
                      )}
                    </div>
                  </div>
                  <div className={styles.campaignActions}>
                    <Button
                      size="sm"
                      onClick={() => handleCampaignSelected(campaign)}
                    >
                      Play
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleEditCampaign(campaign)}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => {
                        if (!campaign.id) {
                          console.error(
                            "Cannot delete campaign: ID is missing"
                          );
                          return;
                        }
                        handleDeleteCampaign(campaign.id);
                      }}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
      <ConfirmDialog
        isOpen={campaignToDelete !== null}
        title="Delete Campaign"
        message="Are you sure you want to delete this campaign? This action cannot be undone."
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        confirmLabel="Delete"
        cancelLabel="Cancel"
      />
    </>
  );
};

export default CampaignSelection;
