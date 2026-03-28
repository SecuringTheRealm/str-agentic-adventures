import type React from "react";
import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  cloneCampaign,
  getCampaignTemplates,
  getCampaignTemplatesWithRetry,
} from "../services/api";
import type { Campaign } from "../types";
import { getRuntimeMode } from "../utils/environment";
import styles from "./CampaignGallery.module.css";

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
  const [debugInfo, setDebugInfo] = useState<string | null>(null);

  useEffect(() => {
    const loadTemplates = async () => {
      try {
        setLoading(true);
        setError(null);
        setDebugInfo(null);

        // Load templates with retry logic for production reliability
        const isProduction = getRuntimeMode() === "production";
        const templateData = isProduction
          ? await getCampaignTemplatesWithRetry()
          : await getCampaignTemplates();
        setTemplates(templateData);

        if (templateData.length === 0) {
          setDebugInfo(
            "API call succeeded but returned no templates. Check if the backend has seeded template data."
          );
        }
      } catch (err: any) {
        console.error("Error loading templates:", err);

        // Provide detailed error information for debugging
        let errorMessage = "Failed to load campaign templates";
        let debugMessage = "";

        if (err.response) {
          // HTTP error response
          errorMessage = `HTTP ${err.response.status}: ${err.response.statusText}`;
          debugMessage = `URL: ${err.config?.url || "Unknown"}\nResponse: ${JSON.stringify(err.response.data, null, 2)}`;
        } else if (err.request) {
          // Network error
          errorMessage = "Network error - cannot reach the backend server";
          debugMessage = `URL: ${err.config?.url || "Unknown"}\nError: ${err.message}`;
        } else {
          // Other error
          errorMessage = err.message || errorMessage;
          debugMessage = `Error type: ${err.name || "Unknown"}\nStack: ${err.stack || "No stack trace"}`;
        }

        setError(errorMessage);
        setDebugInfo(debugMessage);
      } finally {
        setLoading(false);
      }
    };

    loadTemplates();
  }, []);

  const handleSelectTemplate = async (template: Campaign) => {
    try {
      if (!template.id) {
        throw new Error("Template ID is required");
      }
      setCloning(template.id);
      const clonedCampaign = await cloneCampaign({
        template_id: template.id,
        new_name: `${template.name} (My Campaign)`,
      });
      onCampaignSelected(clonedCampaign);
    } catch (err) {
      setError("Failed to clone campaign template");
      console.error("Error cloning template:", err);
    } finally {
      setCloning(null);
    }
  };

  if (loading) {
    return (
      <div className={`${styles.campaignGallery} ${styles.loading}`}>
        <div className={styles.loadingSpinner} />
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
          {debugInfo && (
            <details className={styles.debugDetails}>
              <summary>Debug Information</summary>
              <pre
                style={{
                  whiteSpace: "pre-wrap",
                  margin: "0.5rem 0",
                }}
              >
                {debugInfo}
              </pre>
            </details>
          )}
          <div style={{ marginTop: "1rem" }} className="flex gap-2">
            <Button variant="default" onClick={() => window.location.reload()}>
              Try Again
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setError(null);
                setDebugInfo(null);
                window.location.reload();
              }}
            >
              Reload Page
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.campaignGallery}>
      <header className={styles.galleryHeader}>
        <h2>Choose Your Adventure</h2>
        <p>
          Select from our curated campaign templates or create your own custom
          campaign
        </p>
      </header>

      <div className={styles.campaignOptions}>
        <Card className={styles.customCampaignCard}>
          <CardHeader>
            <div className={styles.cardIcon}>✨</div>
            <CardTitle>Create Custom Campaign</CardTitle>
            <CardDescription>
              Start from scratch with your own unique world and story
            </CardDescription>
          </CardHeader>
          <CardFooter>
            <Button
              className={`${styles.selectButton} ${styles.custom}`}
              onClick={onCreateCustom}
            >
              Create Custom
            </Button>
          </CardFooter>
        </Card>

        {templates.map((template) => (
          <Card key={template.id} className={styles.campaignCard}>
            <CardHeader className={styles.cardHeader}>
              <CardTitle>{template.name}</CardTitle>
              <Badge
                className={`${styles.toneBadge} ${template.tone ? styles[template.tone] : ""}`}
                variant="secondary"
              >
                {template.tone}
              </Badge>
            </CardHeader>

            <CardContent>
              <CardDescription className={styles.cardDescription}>
                {template.description || "An exciting adventure awaits!"}
              </CardDescription>

              <div className={styles.cardDetails}>
                <div className={styles.detailItem}>
                  <strong>Setting:</strong>
                  <span>{template.setting.substring(0, 100)}...</span>
                </div>

                {template.plot_hooks && template.plot_hooks.length > 0 && (
                  <div className={styles.detailItem}>
                    <strong>Plot Hooks:</strong>
                    <ul>
                      {template.plot_hooks
                        .slice(0, 2)
                        .map((hook: string | null) => (
                          <li key={hook || ""}>{hook}</li>
                        ))}
                    </ul>
                  </div>
                )}

                {template.homebrew_rules &&
                  template.homebrew_rules.length > 0 && (
                    <div className={styles.detailItem}>
                      <strong>Special Rules:</strong>
                      <span>
                        {template.homebrew_rules.length} custom rule(s)
                      </span>
                    </div>
                  )}
              </div>
            </CardContent>

            <CardFooter>
              <Button
                className={styles.selectButton}
                onClick={() => handleSelectTemplate(template)}
                disabled={cloning === template.id}
              >
                {cloning === template.id ? (
                  <>
                    <span
                      className={`${styles.loadingSpinner} ${styles.small}`}
                    />
                    Preparing...
                  </>
                ) : (
                  "Select Campaign"
                )}
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>

      {templates.length === 0 && (
        <div className={styles.noTemplates}>
          <h3>No Templates Available</h3>
          <p>Create a custom campaign to get started!</p>
          <Button className={styles.selectButton} onClick={onCreateCustom}>
            Create Custom Campaign
          </Button>
        </div>
      )}
    </div>
  );
};

export default CampaignGallery;
