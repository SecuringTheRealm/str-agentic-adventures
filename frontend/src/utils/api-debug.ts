/**
 * API debugging utilities to help diagnose production issues
 */
import { getConfiguredApiUrl, getEnvVar, getRuntimeMode } from "./environment";

export const logApiConfiguration = () => {
  console.group("🔧 API Configuration Debug");
  console.log("VITE_API_URL:", getEnvVar("VITE_API_URL"));
  console.log("REACT_APP_API_URL (legacy):", getEnvVar("REACT_APP_API_URL"));
  console.log("Default fallback URL:", "http://localhost:8000");
  console.log("Current MODE:", getRuntimeMode());

  // Get the actual URL that will be used
  const baseUrl = getConfiguredApiUrl();
  console.log("Resolved base URL:", baseUrl);
  console.log(
    "Expected API endpoint:",
    `${baseUrl}/api/game/campaign/templates`
  );
  console.groupEnd();
};

export const testApiConnectivity = async (
  baseUrl: string
): Promise<boolean> => {
  try {
    console.log("🔍 Testing API connectivity to:", baseUrl);

    // Test basic connectivity to the base URL
    const healthResponse = await fetch(`${baseUrl}/health`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!healthResponse.ok) {
      console.error(
        "❌ Health check failed:",
        healthResponse.status,
        healthResponse.statusText
      );
      return false;
    }

    console.log("✅ Health check passed");

    // Test the specific templates endpoint
    const templatesResponse = await fetch(
      `${baseUrl}/api/game/campaign/templates`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (!templatesResponse.ok) {
      console.error(
        "❌ Templates endpoint failed:",
        templatesResponse.status,
        templatesResponse.statusText
      );
      return false;
    }

    const data = await templatesResponse.json();
    console.log(
      "✅ Templates endpoint working, templates count:",
      data.templates?.length || 0
    );
    return true;
  } catch (error) {
    console.error("❌ API connectivity test failed:", error);
    return false;
  }
};

export const validateApiUrl = (
  url: string
): { isValid: boolean; issues: string[] } => {
  const issues: string[] = [];

  if (!url) {
    issues.push("API URL is empty or undefined");
    return { isValid: false, issues };
  }

  if (!url.startsWith("http://") && !url.startsWith("https://")) {
    issues.push("API URL must start with http:// or https://");
  }

  if (url.endsWith("/")) {
    issues.push("API URL should not end with a trailing slash");
  }

  if (url.includes("/api")) {
    issues.push(
      "API URL should not include /api path (it will be added automatically). This causes double /api paths and 404 errors."
    );
  }

  try {
    new URL(url);
  } catch {
    issues.push("API URL is not a valid URL format");
  }

  return { isValid: issues.length === 0, issues };
};
