# NPCInteractionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**npc_id** | **string** |  | [default to undefined]
**character_id** | **string** |  | [optional] [default to undefined]
**interaction_type** | **string** |  | [default to undefined]
**summary** | **string** |  | [default to undefined]
**outcome** | **string** |  | [optional] [default to undefined]
**relationship_change** | **number** |  | [optional] [default to 0]

## Example

```typescript
import { NPCInteractionRequest } from './api';

const instance: NPCInteractionRequest = {
    npc_id,
    character_id,
    interaction_type,
    summary,
    outcome,
    relationship_change,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
