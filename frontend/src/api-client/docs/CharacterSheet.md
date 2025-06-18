# CharacterSheet


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [optional] [default to undefined]
**name** | **string** |  | [default to undefined]
**race** | [**Race**](Race.md) |  | [default to undefined]
**character_class** | [**CharacterClass**](CharacterClass.md) |  | [default to undefined]
**level** | **number** |  | [optional] [default to 1]
**background** | **string** |  | [optional] [default to undefined]
**alignment** | **string** |  | [optional] [default to undefined]
**experience** | **number** |  | [optional] [default to 0]
**abilities** | [**Abilities**](Abilities.md) |  | [default to undefined]
**hit_points** | [**HitPoints**](HitPoints.md) |  | [default to undefined]
**armor_class** | **number** |  | [optional] [default to 10]
**speed** | **number** |  | [optional] [default to 30]
**proficiency_bonus** | **number** |  | [optional] [default to 2]
**skills** | **{ [key: string]: boolean; }** |  | [optional] [default to undefined]
**inventory** | [**Array&lt;InventorySlot&gt;**](InventorySlot.md) |  | [optional] [default to undefined]
**equipped_items** | [**Array&lt;EquippedItem&gt;**](EquippedItem.md) |  | [optional] [default to undefined]
**carrying_capacity** | **number** |  | [optional] [default to undefined]
**spells** | [**Array&lt;Spell&gt;**](Spell.md) |  | [optional] [default to undefined]
**spellcasting** | [**SpellCasting**](SpellCasting.md) |  | [optional] [default to undefined]
**features** | **Array&lt;{ [key: string]: any; }&gt;** |  | [optional] [default to undefined]
**backstory** | **string** |  | [optional] [default to undefined]
**ability_score_improvements_used** | **number** |  | [optional] [default to 0]
**hit_dice** | **string** |  | [optional] [default to '1d8']

## Example

```typescript
import { CharacterSheet } from './api';

const instance: CharacterSheet = {
    id,
    name,
    race,
    character_class,
    level,
    background,
    alignment,
    experience,
    abilities,
    hit_points,
    armor_class,
    speed,
    proficiency_bonus,
    skills,
    inventory,
    equipped_items,
    carrying_capacity,
    spells,
    spellcasting,
    features,
    backstory,
    ability_score_improvements_used,
    hit_dice,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
