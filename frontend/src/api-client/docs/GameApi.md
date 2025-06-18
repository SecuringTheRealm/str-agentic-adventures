# GameApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**awardExperienceApiGameCharacterCharacterIdAwardExperiencePost**](#awardexperienceapigamecharactercharacteridawardexperiencepost) | **POST** /api/game/character/{character_id}/award-experience | Award Experience|
|[**calculateSpellAttackBonusApiGameSpellsAttackBonusPost**](#calculatespellattackbonusapigamespellsattackbonuspost) | **POST** /api/game/spells/attack-bonus | Calculate Spell Attack Bonus|
|[**calculateSpellSaveDcEndpointApiGameSpellsSaveDcPost**](#calculatespellsavedcendpointapigamespellssavedcpost) | **POST** /api/game/spells/save-dc | Calculate Spell Save Dc Endpoint|
|[**castSpellInCombatApiGameCombatCombatIdCastSpellPost**](#castspellincombatapigamecombatcombatidcastspellpost) | **POST** /api/game/combat/{combat_id}/cast-spell | Cast Spell In Combat|
|[**cloneCampaignApiGameCampaignClonePost**](#clonecampaignapigamecampaignclonepost) | **POST** /api/game/campaign/clone | Clone Campaign|
|[**createCampaignApiGameCampaignPost**](#createcampaignapigamecampaignpost) | **POST** /api/game/campaign | Create Campaign|
|[**createCampaignNpcApiGameCampaignCampaignIdNpcsPost**](#createcampaignnpcapigamecampaigncampaignidnpcspost) | **POST** /api/game/campaign/{campaign_id}/npcs | Create Campaign Npc|
|[**createCharacterApiGameCharacterPost**](#createcharacterapigamecharacterpost) | **POST** /api/game/character | Create Character|
|[**deleteCampaignApiGameCampaignCampaignIdDelete**](#deletecampaignapigamecampaigncampaigniddelete) | **DELETE** /api/game/campaign/{campaign_id} | Delete Campaign|
|[**generateAiContentApiGameCampaignAiGeneratePost**](#generateaicontentapigamecampaignaigeneratepost) | **POST** /api/game/campaign/ai-generate | Generate Ai Content|
|[**generateBattleMapApiGameBattleMapPost**](#generatebattlemapapigamebattlemappost) | **POST** /api/game/battle-map | Generate Battle Map|
|[**generateCampaignWorldApiGameCampaignGenerateWorldPost**](#generatecampaignworldapigamecampaigngenerateworldpost) | **POST** /api/game/campaign/generate-world | Generate Campaign World|
|[**generateImageApiGameGenerateImagePost**](#generateimageapigamegenerateimagepost) | **POST** /api/game/generate-image | Generate Image|
|[**generateNpcStatsApiGameNpcNpcIdGenerateStatsPost**](#generatenpcstatsapigamenpcnpcidgeneratestatspost) | **POST** /api/game/npc/{npc_id}/generate-stats | Generate Npc Stats|
|[**getAiAssistanceApiGameCampaignAiAssistPost**](#getaiassistanceapigamecampaignaiassistpost) | **POST** /api/game/campaign/ai-assist | Get Ai Assistance|
|[**getCampaignApiGameCampaignCampaignIdGet**](#getcampaignapigamecampaigncampaignidget) | **GET** /api/game/campaign/{campaign_id} | Get Campaign|
|[**getCampaignTemplatesApiGameCampaignTemplatesGet**](#getcampaigntemplatesapigamecampaigntemplatesget) | **GET** /api/game/campaign/templates | Get Campaign Templates|
|[**getCharacterApiGameCharacterCharacterIdGet**](#getcharacterapigamecharactercharacteridget) | **GET** /api/game/character/{character_id} | Get Character|
|[**getEncumbranceApiGameCharacterCharacterIdEncumbranceGet**](#getencumbranceapigamecharactercharacteridencumbranceget) | **GET** /api/game/character/{character_id}/encumbrance | Get Encumbrance|
|[**getItemCatalogApiGameItemsCatalogGet**](#getitemcatalogapigameitemscatalogget) | **GET** /api/game/items/catalog | Get Item Catalog|
|[**getNpcPersonalityApiGameNpcNpcIdPersonalityGet**](#getnpcpersonalityapigamenpcnpcidpersonalityget) | **GET** /api/game/npc/{npc_id}/personality | Get Npc Personality|
|[**getProgressionInfoApiGameCharacterCharacterIdProgressionInfoGet**](#getprogressioninfoapigamecharactercharacteridprogressioninfoget) | **GET** /api/game/character/{character_id}/progression-info | Get Progression Info|
|[**getSpellListApiGameSpellsListGet**](#getspelllistapigamespellslistget) | **GET** /api/game/spells/list | Get Spell List|
|[**initializeCombatApiGameCombatInitializePost**](#initializecombatapigamecombatinitializepost) | **POST** /api/game/combat/initialize | Initialize Combat|
|[**inputManualRollApiGameDiceManualRollPost**](#inputmanualrollapigamedicemanualrollpost) | **POST** /api/game/dice/manual-roll | Input Manual Roll|
|[**levelUpCharacterApiGameCharacterCharacterIdLevelUpPost**](#levelupcharacterapigamecharactercharacteridleveluppost) | **POST** /api/game/character/{character_id}/level-up | Level Up Character|
|[**listCampaignsApiGameCampaignsGet**](#listcampaignsapigamecampaignsget) | **GET** /api/game/campaigns | List Campaigns|
|[**logNpcInteractionApiGameNpcNpcIdInteractionPost**](#lognpcinteractionapigamenpcnpcidinteractionpost) | **POST** /api/game/npc/{npc_id}/interaction | Log Npc Interaction|
|[**manageCharacterSpellsApiGameCharacterCharacterIdSpellsPost**](#managecharacterspellsapigamecharactercharacteridspellspost) | **POST** /api/game/character/{character_id}/spells | Manage Character Spells|
|[**manageConcentrationApiGameCharacterCharacterIdConcentrationPost**](#manageconcentrationapigamecharactercharacteridconcentrationpost) | **POST** /api/game/character/{character_id}/concentration | Manage Concentration|
|[**manageEquipmentApiGameCharacterCharacterIdEquipmentPost**](#manageequipmentapigamecharactercharacteridequipmentpost) | **POST** /api/game/character/{character_id}/equipment | Manage Equipment|
|[**manageMagicalEffectsApiGameItemsMagicalEffectsPost**](#managemagicaleffectsapigameitemsmagicaleffectspost) | **POST** /api/game/items/magical-effects | Manage Magical Effects|
|[**manageSpellSlotsApiGameCharacterCharacterIdSpellSlotsPost**](#managespellslotsapigamecharactercharacteridspellslotspost) | **POST** /api/game/character/{character_id}/spell-slots | Manage Spell Slots|
|[**processCombatTurnApiGameCombatCombatIdTurnPost**](#processcombatturnapigamecombatcombatidturnpost) | **POST** /api/game/combat/{combat_id}/turn | Process Combat Turn|
|[**processPlayerActionApiGameSessionSessionIdActionPost**](#processplayeractionapigamesessionsessionidactionpost) | **POST** /api/game/session/{session_id}/action | Process Player Action|
|[**processPlayerInputApiGameInputPost**](#processplayerinputapigameinputpost) | **POST** /api/game/input | Process Player Input|
|[**rollDiceApiGameDiceRollPost**](#rolldiceapigamedicerollpost) | **POST** /api/game/dice/roll | Roll Dice|
|[**rollDiceWithCharacterApiGameDiceRollWithCharacterPost**](#rolldicewithcharacterapigamedicerollwithcharacterpost) | **POST** /api/game/dice/roll-with-character | Roll Dice With Character|
|[**startGameSessionApiGameCampaignCampaignIdStartSessionPost**](#startgamesessionapigamecampaigncampaignidstartsessionpost) | **POST** /api/game/campaign/{campaign_id}/start-session | Start Game Session|
|[**updateCampaignApiGameCampaignCampaignIdPut**](#updatecampaignapigamecampaigncampaignidput) | **PUT** /api/game/campaign/{campaign_id} | Update Campaign|

# **awardExperienceApiGameCharacterCharacterIdAwardExperiencePost**
> { [key: string]: any; } awardExperienceApiGameCharacterCharacterIdAwardExperiencePost(requestBody)

Award experience points to a character.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let characterId: string; // (default to undefined)
let requestBody: { [key: string]: number | null; }; //

const { status, data } = await apiInstance.awardExperienceApiGameCharacterCharacterIdAwardExperiencePost(
    characterId,
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **{ [key: string]: number | null; }**|  | |
| **characterId** | [**string**] |  | defaults to undefined|


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **calculateSpellAttackBonusApiGameSpellsAttackBonusPost**
> { [key: string]: any; } calculateSpellAttackBonusApiGameSpellsAttackBonusPost(spellAttackBonusRequest)

Calculate spell attack bonus for a character.

### Example

```typescript
import {
    GameApi,
    Configuration,
    SpellAttackBonusRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let spellAttackBonusRequest: SpellAttackBonusRequest; //

const { status, data } = await apiInstance.calculateSpellAttackBonusApiGameSpellsAttackBonusPost(
    spellAttackBonusRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **spellAttackBonusRequest** | **SpellAttackBonusRequest**|  | |


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **calculateSpellSaveDcEndpointApiGameSpellsSaveDcPost**
> { [key: string]: any; } calculateSpellSaveDcEndpointApiGameSpellsSaveDcPost()

Calculate spell save DC for a character.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let characterClass: CharacterClass; // (default to undefined)
let level: number; // (default to undefined)
let spellcastingAbilityScore: number; // (default to undefined)

const { status, data } = await apiInstance.calculateSpellSaveDcEndpointApiGameSpellsSaveDcPost(
    characterClass,
    level,
    spellcastingAbilityScore
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **characterClass** | **CharacterClass** |  | defaults to undefined|
| **level** | [**number**] |  | defaults to undefined|
| **spellcastingAbilityScore** | [**number**] |  | defaults to undefined|


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **castSpellInCombatApiGameCombatCombatIdCastSpellPost**
> SpellCastingResponse castSpellInCombatApiGameCombatCombatIdCastSpellPost(castSpellRequest)

Cast spells during combat with sophisticated effect resolution.

### Example

```typescript
import {
    GameApi,
    Configuration,
    CastSpellRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let combatId: string; // (default to undefined)
let castSpellRequest: CastSpellRequest; //

const { status, data } = await apiInstance.castSpellInCombatApiGameCombatCombatIdCastSpellPost(
    combatId,
    castSpellRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **castSpellRequest** | **CastSpellRequest**|  | |
| **combatId** | [**string**] |  | defaults to undefined|


### Return type

**SpellCastingResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cloneCampaignApiGameCampaignClonePost**
> Campaign cloneCampaignApiGameCampaignClonePost(cloneCampaignRequest)

Clone a template campaign for customization.

### Example

```typescript
import {
    GameApi,
    Configuration,
    CloneCampaignRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let cloneCampaignRequest: CloneCampaignRequest; //

const { status, data } = await apiInstance.cloneCampaignApiGameCampaignClonePost(
    cloneCampaignRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **cloneCampaignRequest** | **CloneCampaignRequest**|  | |


### Return type

**Campaign**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createCampaignApiGameCampaignPost**
> Campaign createCampaignApiGameCampaignPost(createCampaignRequest)

Create a new campaign.

### Example

```typescript
import {
    GameApi,
    Configuration,
    CreateCampaignRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let createCampaignRequest: CreateCampaignRequest; //

const { status, data } = await apiInstance.createCampaignApiGameCampaignPost(
    createCampaignRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createCampaignRequest** | **CreateCampaignRequest**|  | |


### Return type

**Campaign**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createCampaignNpcApiGameCampaignCampaignIdNpcsPost**
> NPC createCampaignNpcApiGameCampaignCampaignIdNpcsPost(createNPCRequest)

Create and manage campaign NPCs.

### Example

```typescript
import {
    GameApi,
    Configuration,
    CreateNPCRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let campaignId: string; // (default to undefined)
let createNPCRequest: CreateNPCRequest; //

const { status, data } = await apiInstance.createCampaignNpcApiGameCampaignCampaignIdNpcsPost(
    campaignId,
    createNPCRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createNPCRequest** | **CreateNPCRequest**|  | |
| **campaignId** | [**string**] |  | defaults to undefined|


### Return type

**NPC**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createCharacterApiGameCharacterPost**
> CharacterSheet createCharacterApiGameCharacterPost(createCharacterRequest)

Create a new player character.

### Example

```typescript
import {
    GameApi,
    Configuration,
    CreateCharacterRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let createCharacterRequest: CreateCharacterRequest; //

const { status, data } = await apiInstance.createCharacterApiGameCharacterPost(
    createCharacterRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **createCharacterRequest** | **CreateCharacterRequest**|  | |


### Return type

**CharacterSheet**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteCampaignApiGameCampaignCampaignIdDelete**
> any deleteCampaignApiGameCampaignCampaignIdDelete()

Delete a custom campaign (templates cannot be deleted).

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let campaignId: string; // (default to undefined)

const { status, data } = await apiInstance.deleteCampaignApiGameCampaignCampaignIdDelete(
    campaignId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **campaignId** | [**string**] |  | defaults to undefined|


### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **generateAiContentApiGameCampaignAiGeneratePost**
> AIContentGenerationResponse generateAiContentApiGameCampaignAiGeneratePost(aIContentGenerationRequest)

Generate AI content based on a specific suggestion and current text.

### Example

```typescript
import {
    GameApi,
    Configuration,
    AIContentGenerationRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let aIContentGenerationRequest: AIContentGenerationRequest; //

const { status, data } = await apiInstance.generateAiContentApiGameCampaignAiGeneratePost(
    aIContentGenerationRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIContentGenerationRequest** | **AIContentGenerationRequest**|  | |


### Return type

**AIContentGenerationResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **generateBattleMapApiGameBattleMapPost**
> { [key: string]: any; } generateBattleMapApiGameBattleMapPost(requestBody)

Generate a battle map based on environment details.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let requestBody: { [key: string]: any; }; //

const { status, data } = await apiInstance.generateBattleMapApiGameBattleMapPost(
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **{ [key: string]: any; }**|  | |


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **generateCampaignWorldApiGameCampaignGenerateWorldPost**
> { [key: string]: any; } generateCampaignWorldApiGameCampaignGenerateWorldPost(requestBody)

Generate world description and setting for a new campaign.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let requestBody: { [key: string]: any; }; //

const { status, data } = await apiInstance.generateCampaignWorldApiGameCampaignGenerateWorldPost(
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **{ [key: string]: any; }**|  | |


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **generateImageApiGameGenerateImagePost**
> { [key: string]: any; } generateImageApiGameGenerateImagePost(requestBody)

Generate an image based on the request details.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let requestBody: { [key: string]: any; }; //

const { status, data } = await apiInstance.generateImageApiGameGenerateImagePost(
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **{ [key: string]: any; }**|  | |


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **generateNpcStatsApiGameNpcNpcIdGenerateStatsPost**
> NPCStatsResponse generateNpcStatsApiGameNpcNpcIdGenerateStatsPost(generateNPCStatsRequest)

Generate combat stats for NPCs dynamically.

### Example

```typescript
import {
    GameApi,
    Configuration,
    GenerateNPCStatsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let npcId: string; // (default to undefined)
let generateNPCStatsRequest: GenerateNPCStatsRequest; //

const { status, data } = await apiInstance.generateNpcStatsApiGameNpcNpcIdGenerateStatsPost(
    npcId,
    generateNPCStatsRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **generateNPCStatsRequest** | **GenerateNPCStatsRequest**|  | |
| **npcId** | [**string**] |  | defaults to undefined|


### Return type

**NPCStatsResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAiAssistanceApiGameCampaignAiAssistPost**
> AIAssistanceResponse getAiAssistanceApiGameCampaignAiAssistPost(aIAssistanceRequest)

Get AI assistance for campaign text enhancement.

### Example

```typescript
import {
    GameApi,
    Configuration,
    AIAssistanceRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let aIAssistanceRequest: AIAssistanceRequest; //

const { status, data } = await apiInstance.getAiAssistanceApiGameCampaignAiAssistPost(
    aIAssistanceRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **aIAssistanceRequest** | **AIAssistanceRequest**|  | |


### Return type

**AIAssistanceResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getCampaignApiGameCampaignCampaignIdGet**
> Campaign getCampaignApiGameCampaignCampaignIdGet()

Get a specific campaign by ID.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let campaignId: string; // (default to undefined)

const { status, data } = await apiInstance.getCampaignApiGameCampaignCampaignIdGet(
    campaignId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **campaignId** | [**string**] |  | defaults to undefined|


### Return type

**Campaign**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getCampaignTemplatesApiGameCampaignTemplatesGet**
> any getCampaignTemplatesApiGameCampaignTemplatesGet()

Get pre-built campaign templates.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

const { status, data } = await apiInstance.getCampaignTemplatesApiGameCampaignTemplatesGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getCharacterApiGameCharacterCharacterIdGet**
> { [key: string]: any; } getCharacterApiGameCharacterCharacterIdGet()

Retrieve a character sheet by ID.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let characterId: string; // (default to undefined)

const { status, data } = await apiInstance.getCharacterApiGameCharacterCharacterIdGet(
    characterId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **characterId** | [**string**] |  | defaults to undefined|


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getEncumbranceApiGameCharacterCharacterIdEncumbranceGet**
> EncumbranceResponse getEncumbranceApiGameCharacterCharacterIdEncumbranceGet()

Calculate carrying capacity and weight.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let characterId: string; // (default to undefined)

const { status, data } = await apiInstance.getEncumbranceApiGameCharacterCharacterIdEncumbranceGet(
    characterId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **characterId** | [**string**] |  | defaults to undefined|


### Return type

**EncumbranceResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getItemCatalogApiGameItemsCatalogGet**
> ItemCatalogResponse getItemCatalogApiGameItemsCatalogGet()

Browse available items with rarity and value information.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let itemType: ItemType; // (optional) (default to undefined)
let rarity: ItemRarity; // (optional) (default to undefined)
let minValue: number; // (optional) (default to undefined)
let maxValue: number; // (optional) (default to undefined)

const { status, data } = await apiInstance.getItemCatalogApiGameItemsCatalogGet(
    itemType,
    rarity,
    minValue,
    maxValue
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **itemType** | **ItemType** |  | (optional) defaults to undefined|
| **rarity** | **ItemRarity** |  | (optional) defaults to undefined|
| **minValue** | [**number**] |  | (optional) defaults to undefined|
| **maxValue** | [**number**] |  | (optional) defaults to undefined|


### Return type

**ItemCatalogResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getNpcPersonalityApiGameNpcNpcIdPersonalityGet**
> NPCPersonality getNpcPersonalityApiGameNpcNpcIdPersonalityGet()

Get NPC personality traits and behaviors.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let npcId: string; // (default to undefined)

const { status, data } = await apiInstance.getNpcPersonalityApiGameNpcNpcIdPersonalityGet(
    npcId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **npcId** | [**string**] |  | defaults to undefined|


### Return type

**NPCPersonality**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getProgressionInfoApiGameCharacterCharacterIdProgressionInfoGet**
> { [key: string]: any; } getProgressionInfoApiGameCharacterCharacterIdProgressionInfoGet()

Get progression information for a character.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let characterId: string; // (default to undefined)

const { status, data } = await apiInstance.getProgressionInfoApiGameCharacterCharacterIdProgressionInfoGet(
    characterId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **characterId** | [**string**] |  | defaults to undefined|


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSpellListApiGameSpellsListGet**
> SpellListResponse getSpellListApiGameSpellsListGet()

Get available spells by class and level.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let characterClass: CharacterClass; // (optional) (default to undefined)
let spellLevel: number; // (optional) (default to undefined)
let school: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getSpellListApiGameSpellsListGet(
    characterClass,
    spellLevel,
    school
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **characterClass** | **CharacterClass** |  | (optional) defaults to undefined|
| **spellLevel** | [**number**] |  | (optional) defaults to undefined|
| **school** | [**string**] |  | (optional) defaults to undefined|


### Return type

**SpellListResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **initializeCombatApiGameCombatInitializePost**
> { [key: string]: any; } initializeCombatApiGameCombatInitializePost(requestBody)

Initialize a new combat encounter.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let requestBody: { [key: string]: any; }; //

const { status, data } = await apiInstance.initializeCombatApiGameCombatInitializePost(
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **{ [key: string]: any; }**|  | |


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **inputManualRollApiGameDiceManualRollPost**
> { [key: string]: any; } inputManualRollApiGameDiceManualRollPost(requestBody)

Input a manual dice roll result.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let requestBody: { [key: string]: any; }; //

const { status, data } = await apiInstance.inputManualRollApiGameDiceManualRollPost(
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **{ [key: string]: any; }**|  | |


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **levelUpCharacterApiGameCharacterCharacterIdLevelUpPost**
> { [key: string]: any; } levelUpCharacterApiGameCharacterCharacterIdLevelUpPost(levelUpRequest)

Level up a character.

### Example

```typescript
import {
    GameApi,
    Configuration,
    LevelUpRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let characterId: string; // (default to undefined)
let levelUpRequest: LevelUpRequest; //

const { status, data } = await apiInstance.levelUpCharacterApiGameCharacterCharacterIdLevelUpPost(
    characterId,
    levelUpRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **levelUpRequest** | **LevelUpRequest**|  | |
| **characterId** | [**string**] |  | defaults to undefined|


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listCampaignsApiGameCampaignsGet**
> CampaignListResponse listCampaignsApiGameCampaignsGet()

List all campaigns including templates and custom campaigns.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

const { status, data } = await apiInstance.listCampaignsApiGameCampaignsGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**CampaignListResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **logNpcInteractionApiGameNpcNpcIdInteractionPost**
> NPCInteractionResponse logNpcInteractionApiGameNpcNpcIdInteractionPost(nPCInteractionRequest)

Log and retrieve NPC interaction history.

### Example

```typescript
import {
    GameApi,
    Configuration,
    NPCInteractionRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let npcId: string; // (default to undefined)
let nPCInteractionRequest: NPCInteractionRequest; //

const { status, data } = await apiInstance.logNpcInteractionApiGameNpcNpcIdInteractionPost(
    npcId,
    nPCInteractionRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **nPCInteractionRequest** | **NPCInteractionRequest**|  | |
| **npcId** | [**string**] |  | defaults to undefined|


### Return type

**NPCInteractionResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **manageCharacterSpellsApiGameCharacterCharacterIdSpellsPost**
> { [key: string]: any; } manageCharacterSpellsApiGameCharacterCharacterIdSpellsPost(manageSpellsRequest)

Manage known spells for a character.

### Example

```typescript
import {
    GameApi,
    Configuration,
    ManageSpellsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let characterId: string; // (default to undefined)
let manageSpellsRequest: ManageSpellsRequest; //

const { status, data } = await apiInstance.manageCharacterSpellsApiGameCharacterCharacterIdSpellsPost(
    characterId,
    manageSpellsRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **manageSpellsRequest** | **ManageSpellsRequest**|  | |
| **characterId** | [**string**] |  | defaults to undefined|


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **manageConcentrationApiGameCharacterCharacterIdConcentrationPost**
> ConcentrationCheckResponse manageConcentrationApiGameCharacterCharacterIdConcentrationPost(concentrationRequest)

Manage spell concentration tracking for a character.

### Example

```typescript
import {
    GameApi,
    Configuration,
    ConcentrationRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let characterId: string; // (default to undefined)
let concentrationRequest: ConcentrationRequest; //

const { status, data } = await apiInstance.manageConcentrationApiGameCharacterCharacterIdConcentrationPost(
    characterId,
    concentrationRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **concentrationRequest** | **ConcentrationRequest**|  | |
| **characterId** | [**string**] |  | defaults to undefined|


### Return type

**ConcentrationCheckResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **manageEquipmentApiGameCharacterCharacterIdEquipmentPost**
> EquipmentResponse manageEquipmentApiGameCharacterCharacterIdEquipmentPost(manageEquipmentRequest)

Equip/unequip items with stat effects.

### Example

```typescript
import {
    GameApi,
    Configuration,
    ManageEquipmentRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let characterId: string; // (default to undefined)
let manageEquipmentRequest: ManageEquipmentRequest; //

const { status, data } = await apiInstance.manageEquipmentApiGameCharacterCharacterIdEquipmentPost(
    characterId,
    manageEquipmentRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **manageEquipmentRequest** | **ManageEquipmentRequest**|  | |
| **characterId** | [**string**] |  | defaults to undefined|


### Return type

**EquipmentResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **manageMagicalEffectsApiGameItemsMagicalEffectsPost**
> MagicalEffectsResponse manageMagicalEffectsApiGameItemsMagicalEffectsPost(magicalEffectsRequest)

Apply magical item effects to character stats.

### Example

```typescript
import {
    GameApi,
    Configuration,
    MagicalEffectsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let magicalEffectsRequest: MagicalEffectsRequest; //

const { status, data } = await apiInstance.manageMagicalEffectsApiGameItemsMagicalEffectsPost(
    magicalEffectsRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **magicalEffectsRequest** | **MagicalEffectsRequest**|  | |


### Return type

**MagicalEffectsResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **manageSpellSlotsApiGameCharacterCharacterIdSpellSlotsPost**
> { [key: string]: any; } manageSpellSlotsApiGameCharacterCharacterIdSpellSlotsPost(manageSpellSlotsRequest)

Manage spell slot usage and recovery for a character.

### Example

```typescript
import {
    GameApi,
    Configuration,
    ManageSpellSlotsRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let characterId: string; // (default to undefined)
let manageSpellSlotsRequest: ManageSpellSlotsRequest; //

const { status, data } = await apiInstance.manageSpellSlotsApiGameCharacterCharacterIdSpellSlotsPost(
    characterId,
    manageSpellSlotsRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **manageSpellSlotsRequest** | **ManageSpellSlotsRequest**|  | |
| **characterId** | [**string**] |  | defaults to undefined|


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **processCombatTurnApiGameCombatCombatIdTurnPost**
> { [key: string]: any; } processCombatTurnApiGameCombatCombatIdTurnPost(requestBody)

Process a single combat turn.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let combatId: string; // (default to undefined)
let requestBody: { [key: string]: any; }; //

const { status, data } = await apiInstance.processCombatTurnApiGameCombatCombatIdTurnPost(
    combatId,
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **{ [key: string]: any; }**|  | |
| **combatId** | [**string**] |  | defaults to undefined|


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **processPlayerActionApiGameSessionSessionIdActionPost**
> { [key: string]: any; } processPlayerActionApiGameSessionSessionIdActionPost(requestBody)

Process a player action within a game session.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let sessionId: string; // (default to undefined)
let requestBody: { [key: string]: any; }; //

const { status, data } = await apiInstance.processPlayerActionApiGameSessionSessionIdActionPost(
    sessionId,
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **{ [key: string]: any; }**|  | |
| **sessionId** | [**string**] |  | defaults to undefined|


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **processPlayerInputApiGameInputPost**
> GameResponse processPlayerInputApiGameInputPost(playerInput)

Process player input and get game response.

### Example

```typescript
import {
    GameApi,
    Configuration,
    PlayerInput
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let playerInput: PlayerInput; //

const { status, data } = await apiInstance.processPlayerInputApiGameInputPost(
    playerInput
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **playerInput** | **PlayerInput**|  | |


### Return type

**GameResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **rollDiceApiGameDiceRollPost**
> { [key: string]: any; } rollDiceApiGameDiceRollPost(requestBody)

Roll dice using D&D notation.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let requestBody: { [key: string]: string | null; }; //

const { status, data } = await apiInstance.rollDiceApiGameDiceRollPost(
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **{ [key: string]: string | null; }**|  | |


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **rollDiceWithCharacterApiGameDiceRollWithCharacterPost**
> { [key: string]: any; } rollDiceWithCharacterApiGameDiceRollWithCharacterPost(requestBody)

Roll dice with character context for skill checks.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let requestBody: { [key: string]: any; }; //

const { status, data } = await apiInstance.rollDiceWithCharacterApiGameDiceRollWithCharacterPost(
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **{ [key: string]: any; }**|  | |


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **startGameSessionApiGameCampaignCampaignIdStartSessionPost**
> { [key: string]: any; } startGameSessionApiGameCampaignCampaignIdStartSessionPost(requestBody)

Start a new game session for a campaign.

### Example

```typescript
import {
    GameApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let campaignId: string; // (default to undefined)
let requestBody: { [key: string]: any; }; //

const { status, data } = await apiInstance.startGameSessionApiGameCampaignCampaignIdStartSessionPost(
    campaignId,
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **{ [key: string]: any; }**|  | |
| **campaignId** | [**string**] |  | defaults to undefined|


### Return type

**{ [key: string]: any; }**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateCampaignApiGameCampaignCampaignIdPut**
> Campaign updateCampaignApiGameCampaignCampaignIdPut(campaignUpdateRequest)

Update an existing campaign.

### Example

```typescript
import {
    GameApi,
    Configuration,
    CampaignUpdateRequest
} from './api';

const configuration = new Configuration();
const apiInstance = new GameApi(configuration);

let campaignId: string; // (default to undefined)
let campaignUpdateRequest: CampaignUpdateRequest; //

const { status, data } = await apiInstance.updateCampaignApiGameCampaignCampaignIdPut(
    campaignId,
    campaignUpdateRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **campaignUpdateRequest** | **CampaignUpdateRequest**|  | |
| **campaignId** | [**string**] |  | defaults to undefined|


### Return type

**Campaign**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

