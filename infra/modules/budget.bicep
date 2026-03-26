@description('Name of the budget')
param name string

@description('Monthly budget amount in the billing currency')
param amount int = 50

@description('Email addresses for budget notifications')
param contactEmails array = []

@description('Budget start date in yyyy-MM-01 format (must be the first of the month)')
param startDate string

resource budget 'Microsoft.Consumption/budgets@2024-08-01' = {
  name: name
  properties: {
    timePeriod: {
      startDate: startDate
    }
    timeGrain: 'Monthly'
    amount: amount
    category: 'Cost'
    notifications: {
      actual_GreaterThan_80_Percent: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 80
        contactEmails: contactEmails
        thresholdType: 'Actual'
      }
      actual_GreaterThan_100_Percent: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 100
        contactEmails: contactEmails
        thresholdType: 'Actual'
      }
      forecasted_GreaterThan_100_Percent: {
        enabled: true
        operator: 'GreaterThan'
        threshold: 100
        contactEmails: contactEmails
        thresholdType: 'Forecasted'
      }
    }
  }
}
