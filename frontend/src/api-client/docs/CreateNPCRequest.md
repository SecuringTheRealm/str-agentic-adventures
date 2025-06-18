# CreateNPCRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**campaign_id** | **string** |  | [default to undefined]
**name** | **string** |  | [default to undefined]
**race** | **string** |  | [optional] [default to undefined]
**gender** | **string** |  | [optional] [default to undefined]
**age** | **number** |  | [optional] [default to undefined]
**occupation** | **string** |  | [optional] [default to undefined]
**location** | **string** |  | [optional] [default to undefined]
**importance** | **string** |  | [optional] [default to 'minor']
**story_role** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { CreateNPCRequest } from './api';

const instance: CreateNPCRequest = {
    campaign_id,
    name,
    race,
    gender,
    age,
    occupation,
    location,
    importance,
    story_role,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
