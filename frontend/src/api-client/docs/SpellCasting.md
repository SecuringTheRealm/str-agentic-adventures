# SpellCasting


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spellcasting_ability** | **string** |  | [default to undefined]
**spell_attack_bonus** | **number** |  | [optional] [default to 0]
**spell_save_dc** | **number** |  | [optional] [default to 8]
**spell_slots** | [**Array&lt;SpellSlot&gt;**](SpellSlot.md) |  | [optional] [default to undefined]
**known_spells** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**prepared_spells** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**cantrips_known** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**concentration_spell** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { SpellCasting } from './api';

const instance: SpellCasting = {
    spellcasting_ability,
    spell_attack_bonus,
    spell_save_dc,
    spell_slots,
    known_spells,
    prepared_spells,
    cantrips_known,
    concentration_spell,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
