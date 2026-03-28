import type React from "react";
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { deleteCampaign, getCampaigns } from "../services/api";
import type { Campaign } from "../types";
import CampaignGallery from "./CampaignGallery";
import styles from "./CampaignSelection.module.css";
import ConfirmDialog from "./ConfirmDialog";

interface CampaignSelectionProps {
  onCampaignCreated: (campaign: Campaign) => void;
}

const CampaignSelection: React.FC<CampaignSelectionProps> = ({
  onCampaignCreated,
}) => {
  const navigate = useNavigate();
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
      const normalizedCampaigns = Array.isArray(data)
        ? data
        : ((data as unknown as { campaigns?: Campaign[] }).campaigns ?? []);
      setCampaigns(normalizedCampaigns);
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

  return (
    <>
      <div className={styles.campaignManager}>
        {error && (
          <div className={styles.errorMessage}>
            {error}
            <Button variant="ghost" size="icon" onClick={() => setError(null)}>
              ×
            </Button>
          </div>
        )}

        <Tabs defaultValue="gallery" className={styles.campaignTabs}>
          <div className={styles.managerHeader}>
            <div className={styles.headerContent}>
              <h2 className={styles.sectionTitle}>Campaign Hub</h2>
              <p className={styles.sectionSubtitle}>
                Choose from our curated templates or manage your custom
                campaigns
              </p>
            </div>
            <TabsList>
              <TabsTrigger value="gallery">Gallery</TabsTrigger>
              <TabsTrigger value="my-campaigns">
                My Campaigns ({customCampaigns.length})
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="gallery">
            <CampaignGallery
              onCampaignSelected={handleCampaignSelected}
              onCreateCustom={handleCreateCustom}
            />
          </TabsContent>

          <TabsContent value="my-campaigns">
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
                    <Button onClick={handleCreateCustom}>
                      Browse Templates
                    </Button>
                  </div>
                ) : (
                  customCampaigns.map((campaign, index) => (
                    <div
                      key={campaign.id}
                      className={styles.campaignCard}
                      style={{ "--card-delay": `${0.08 * (index + 1)}s` } as React.CSSProperties}
                    >
                      <div className={styles.campaignCardBody}>
                        <div className={styles.campaignCardHeader}>
                          <h3>{campaign.name}</h3>
                          <div className={styles.campaignMeta}>
                            {campaign.tone && (
                              <Badge
                                variant="outline"
                                className={`tone-badge ${campaign.tone}`}
                              >
                                {campaign.tone}
                              </Badge>
                            )}
                            {campaign.template_id && (
                              <Badge variant="secondary">
                                Cloned from template
                              </Badge>
                            )}
                          </div>
                        </div>
                        {(campaign.description || campaign.setting) && (
                          <p className={styles.campaignDescription}>
                            {campaign.description || campaign.setting}
                          </p>
                        )}
                      </div>
                      <div className={styles.campaignCardFooter}>
                        <Button
                          size="sm"
                          className={styles.playButton}
                          onClick={() => handleCampaignSelected(campaign)}
                        >
                          ▶ Play
                        </Button>
                        <div className={styles.secondaryActions}>
                          <Button
                            variant="ghost"
                            size="sm"
                            className={styles.ghostAction}
                            onClick={() => handleEditCampaign(campaign)}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className={styles.ghostActionDanger}
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
                    </div>
                  ))
                )}
              </div>
            )}
          </TabsContent>
        </Tabs>
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
