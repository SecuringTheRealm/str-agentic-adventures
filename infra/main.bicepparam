using 'main.bicep'

// Values injected from azd environment variables (azd env set KEY VALUE)
// Fallback defaults target swedencentral for broadest model + service availability
param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'development')
param location = readEnvironmentVariable('AZURE_LOCATION', 'swedencentral')
param resourceGroupName = readEnvironmentVariable('AZURE_RESOURCE_GROUP_NAME', 'development-rg')
param budgetContactEmails = empty(readEnvironmentVariable('BUDGET_CONTACT_EMAILS', ''))
  ? []
  : [readEnvironmentVariable('BUDGET_CONTACT_EMAILS', '')]