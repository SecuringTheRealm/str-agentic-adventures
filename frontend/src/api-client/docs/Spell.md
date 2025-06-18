# Spell


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [optional] [default to undefined]
**name** | **string** |  | [default to undefined]
**level** | **number** |  | [default to undefined]
**school** | **string** |  | [default to undefined]
**casting_time** | **string** |  | [default to undefined]
**range** | **string** |  | [default to undefined]
**components** | **string** |  | [default to undefined]
**duration** | **string** |  | [default to undefined]
**description** | **string** |  | [default to undefined]
**requires_concentration** | **boolean** |  | [optional] [default to false]
**available_classes** | **Array&lt;string&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { Spell } from './api';

const instance: Spell = {
    id,
    name,
    level,
    school,
    casting_time,
    range,
    components,
    duration,
    description,
    requires_concentration,
    available_classes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
