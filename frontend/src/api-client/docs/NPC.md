# NPC


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** |  | [optional] [default to undefined]
**name** | **string** |  | [default to undefined]
**race** | **string** |  | [optional] [default to undefined]
**gender** | **string** |  | [optional] [default to undefined]
**age** | **number** |  | [optional] [default to undefined]
**occupation** | **string** |  | [optional] [default to undefined]
**location** | **string** |  | [optional] [default to undefined]
**campaign_id** | **string** |  | [default to undefined]
**personality** | [**NPCPersonality**](NPCPersonality.md) |  | [optional] [default to undefined]
**voice_description** | **string** |  | [optional] [default to undefined]
**level** | **number** |  | [optional] [default to 1]
**abilities** | [**Abilities**](Abilities.md) |  | [optional] [default to undefined]
**hit_points** | [**HitPoints**](HitPoints.md) |  | [optional] [default to undefined]
**armor_class** | **number** |  | [optional] [default to undefined]
**skills** | **{ [key: string]: number; }** |  | [optional] [default to undefined]
**relationships** | [**Array&lt;NPCRelationship&gt;**](NPCRelationship.md) |  | [optional] [default to undefined]
**interaction_history** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**importance** | **string** |  | [optional] [default to 'minor']
**story_role** | **string** |  | [optional] [default to undefined]
**quest_involvement** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**is_alive** | **boolean** |  | [optional] [default to true]
**current_mood** | **string** |  | [optional] [default to 'neutral']
**notes** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { NPC } from './api';

const instance: NPC = {
    id,
    name,
    race,
    gender,
    age,
    occupation,
    location,
    campaign_id,
    personality,
    voice_description,
    level,
    abilities,
    hit_points,
    armor_class,
    skills,
    relationships,
    interaction_history,
    importance,
    story_role,
    quest_involvement,
    is_alive,
    current_mood,
    notes,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
