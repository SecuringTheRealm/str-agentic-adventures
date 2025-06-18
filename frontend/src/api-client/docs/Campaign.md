# Campaign


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [optional] [default to undefined]
**name** | **string** |  | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**setting** | **string** |  | [default to undefined]
**dm_notes** | **string** |  | [optional] [default to undefined]
**created_at** | **string** |  | [optional] [default to undefined]
**characters** | **Array&lt;string | null&gt;** |  | [optional] [default to undefined]
**locations** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**npcs** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**quests** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**current_location** | **string** |  | [optional] [default to undefined]
**tone** | **string** |  | [optional] [default to 'heroic']
**homebrew_rules** | **Array&lt;string | null&gt;** |  | [optional] [default to undefined]
**session_log** | **Array&lt;{ [key: string]: any; }&gt;** |  | [optional] [default to undefined]
**state** | **string** |  | [optional] [default to 'created']
**world_description** | **string** |  | [optional] [default to undefined]
**world_art** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**is_template** | **boolean** |  | [optional] [default to false]
**is_custom** | **boolean** |  | [optional] [default to true]
**template_id** | **string** |  | [optional] [default to undefined]
**plot_hooks** | **Array&lt;string | null&gt;** |  | [optional] [default to undefined]
**key_npcs** | **Array&lt;string | null&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { Campaign } from './api';

const instance: Campaign = {
    id,
    name,
    description,
    setting,
    dm_notes,
    created_at,
    characters,
    locations,
    npcs,
    quests,
    current_location,
    tone,
    homebrew_rules,
    session_log,
    state,
    world_description,
    world_art,
    is_template,
    is_custom,
    template_id,
    plot_hooks,
    key_npcs,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
