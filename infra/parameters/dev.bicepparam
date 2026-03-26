using '../main.bicep'

// Development environment defaults
// These provide sensible defaults for development infrastructure sizing.
// Dynamic values (API keys, endpoints) are passed inline by the deploy workflow.

param environmentName = 'development'
param location = 'uksouth'
param resourceGroupName = 'development-rg'
