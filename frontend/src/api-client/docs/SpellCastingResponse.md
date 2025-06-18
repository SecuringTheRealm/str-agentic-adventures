# SpellCastingResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **boolean** |  | [default to undefined]
**message** | **string** |  | [default to undefined]
**spell_effects** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**concentration_broken** | **boolean** |  | [optional] [default to false]
**slot_used** | **boolean** |  | [optional] [default to false]

## Example

```typescript
import { SpellCastingResponse } from './api';

const instance: SpellCastingResponse = {
    success,
    message,
    spell_effects,
    concentration_broken,
    slot_used,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
