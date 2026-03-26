using '../main.bicep'

// Production environment defaults
// These provide sensible defaults for production infrastructure sizing.
// Dynamic values (API keys, endpoints) are passed inline by the deploy workflow.

param environmentName = 'production'
param location = 'uksouth'
param resourceGroupName = 'production-rg'
