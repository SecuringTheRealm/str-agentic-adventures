# Equipment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [optional] [default to undefined]
**name** | **string** |  | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**item_type** | [**ItemType**](ItemType.md) |  | [default to undefined]
**rarity** | [**ItemRarity**](ItemRarity.md) |  | [optional] [default to undefined]
**weight** | **number** |  | [optional] [default to undefined]
**value** | **number** |  | [optional] [default to undefined]
**requires_attunement** | **boolean** |  | [optional] [default to false]
**is_magical** | **boolean** |  | [optional] [default to false]
**stat_modifiers** | **{ [key: string]: number; }** |  | [optional] [default to undefined]
**special_abilities** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**damage_dice** | **string** |  | [optional] [default to undefined]
**damage_type** | **string** |  | [optional] [default to undefined]
**armor_class** | **number** |  | [optional] [default to undefined]
**properties** | **Array&lt;string&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { Equipment } from './api';

const instance: Equipment = {
    id,
    name,
    description,
    item_type,
    rarity,
    weight,
    value,
    requires_attunement,
    is_magical,
    stat_modifiers,
    special_abilities,
    damage_dice,
    damage_type,
    armor_class,
    properties,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
