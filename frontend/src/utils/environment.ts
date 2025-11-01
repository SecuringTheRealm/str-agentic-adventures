/**
 * Environment helper utilities to safely read runtime configuration in browsers and tests.
 */

type GlobalWithProcess = typeof globalThis & {
  process?: {
    env?: Record<string, string | undefined>;
  };
};

const getLegacyProcessEnv = ():
  | Record<string, string | undefined>
  | undefined => {
  return (globalThis as GlobalWithProcess).process?.env;
};

/**
 * Resolve an environment variable from Vite's import.meta.env or legacy process.env.
 */
export const getEnvVar = (key: string): string | undefined => {
  const metaEnv = (import.meta.env ?? {}) as Record<string, string | undefined>;
  if (key in metaEnv && metaEnv[key] !== undefined) {
    return metaEnv[key];
  }

  return getLegacyProcessEnv()?.[key];
};

/**
 * Determine the current execution mode.
 */
export const getRuntimeMode = (): string => {
  return (
    import.meta.env.MODE ?? getLegacyProcessEnv()?.NODE_ENV ?? "development"
  );
};

/**
 * Resolve the API base URL provided via environment configuration.
 */
export const getConfiguredApiUrl = (): string => {
  return getEnvVar("VITE_API_URL") ?? "http://localhost:8000";
};
