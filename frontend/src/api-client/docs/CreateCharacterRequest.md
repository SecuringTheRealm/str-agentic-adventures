# CreateCharacterRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [default to undefined]
**race** | [**Race**](Race.md) |  | [default to undefined]
**character_class** | [**CharacterClass**](CharacterClass.md) |  | [default to undefined]
**abilities** | [**Abilities**](Abilities.md) |  | [default to undefined]
**backstory** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { CreateCharacterRequest } from './api';

const instance: CreateCharacterRequest = {
    name,
    race,
    character_class,
    abilities,
    backstory,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
