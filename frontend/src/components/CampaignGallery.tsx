import type React from "react";
import { useEffect, useState } from "react";
import {
  type Campaign,
  cloneCampaign,
  getCampaignTemplates,
  getCampaignTemplatesWithRetry,
} from "../services/api";
import {
  logApiConfiguration,
  testApiConnectivity,
  validateApiUrl,
} from "../utils/api-debug";
import { getRuntimeMode } from "../utils/environment";
import { getApiBaseUrl } from "../utils/urls";
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

        // Log API configuration for debugging
        logApiConfiguration();

        // Validate API URL configuration
        const baseUrl = getApiBaseUrl();
        const validation = validateApiUrl(baseUrl);

        if (!validation.isValid) {
          const errorMsg = `API URL configuration error: ${validation.issues.join(", ")}`;
          console.error(errorMsg);
          setError(errorMsg);
          setDebugInfo(`Base URL: ${baseUrl}`);
          return;
        }

        // Test API connectivity in development or when explicitly debugging
        if (getRuntimeMode() === "development") {
          const isConnected = await testApiConnectivity(baseUrl);
          if (!isConnected) {
            setError(
              "Cannot connect to the backend API. Please ensure the backend server is running."
            );
            setDebugInfo(`Attempted to connect to: ${baseUrl}`);
            return;
          }
        }

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
            <details style={{ marginTop: "1rem", fontSize: "0.9rem" }}>
              <summary>Debug Information</summary>
              <pre
                style={{
                  whiteSpace: "pre-wrap",
                  background: "#f5f5f5",
                  padding: "1rem",
                  margin: "0.5rem 0",
                }}
              >
                {debugInfo}
              </pre>
            </details>
          )}
          <div style={{ marginTop: "1rem" }}>
            <button type="button" onClick={() => window.location.reload()}>
              Try Again
            </button>
            <button
              type="button"
              onClick={() => {
                setError(null);
                setDebugInfo(null);
                window.location.reload();
              }}
              style={{ marginLeft: "0.5rem" }}
            >
              Reload Page
            </button>
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
        <div className={styles.customCampaignCard}>
          <div className={styles.cardContent}>
            <div className={styles.cardIcon}>✨</div>
            <h3>Create Custom Campaign</h3>
            <p>Start from scratch with your own unique world and story</p>
            <button
              type="button"
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
                <span
                  className={`${styles.toneBadge} ${template.tone ? styles[template.tone] : ""}`}
                >
                  {template.tone}
                </span>
              </div>

              <p className={styles.cardDescription}>
                {template.description || "An exciting adventure awaits!"}
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
                      {template.plot_hooks.slice(0, 2).map((hook: string | null) => (
                        <li key={hook || ''}>{hook}</li>
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

              <button
                type="button"
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
              </button>
            </div>
          </div>
        ))}
      </div>

      {templates.length === 0 && (
        <div className={styles.noTemplates}>
          <h3>No Templates Available</h3>
          <p>Create a custom campaign to get started!</p>
          <button
            type="button"
            className={styles.selectButton}
            onClick={onCreateCustom}
          >
            Create Custom Campaign
          </button>
        </div>
      )}
    </div>
  );
};

export default CampaignGallery;
