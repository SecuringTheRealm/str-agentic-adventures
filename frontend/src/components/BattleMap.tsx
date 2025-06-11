import React, { useState, useEffect } from 'react';
import { generateBattleMap, getMapTemplates, generateMapVariation, BattleMapRequest, MapVariationRequest } from '../services/api';
import './BattleMap.css';

interface BattleMapProps {
  mapUrl: string | null;
  mapData?: any;
  onMapGenerated?: (mapData: any) => void;
  showControls?: boolean;
}

const BattleMap: React.FC<BattleMapProps> = ({ mapUrl, mapData, onMapGenerated, showControls = false }) => {
  const [expanded, setExpanded] = useState<boolean>(false);
  const [showGenerator, setShowGenerator] = useState<boolean>(false);
  const [templates, setTemplates] = useState<any>(null);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [currentMapData, setCurrentMapData] = useState<any>(mapData);

  useEffect(() => {
    if (showControls) {
      loadTemplates();
    }
  }, [showControls]);

  useEffect(() => {
    setCurrentMapData(mapData);
  }, [mapData]);

  const loadTemplates = async () => {
    try {
      const templatesData = await getMapTemplates();
      setTemplates(templatesData);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const handleGenerateMap = async (environment: any) => {
    setIsGenerating(true);
    try {
      const request: BattleMapRequest = {
        environment,
        combat_context: {}
      };
      
      const newMapData = await generateBattleMap(request);
      setCurrentMapData(newMapData);
      
      if (onMapGenerated) {
        onMapGenerated(newMapData);
      }
    } catch (error) {
      console.error('Failed to generate map:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerateVariation = async (variationType: string) => {
    if (!currentMapData?.id) return;
    
    setIsGenerating(true);
    try {
      const request: MapVariationRequest = {
        variation_type: variationType as any
      };
      
      const variationData = await generateMapVariation(currentMapData.id, request);
      setCurrentMapData(variationData);
      
      if (onMapGenerated) {
        onMapGenerated(variationData);
      }
    } catch (error) {
      console.error('Failed to generate variation:', error);
    } finally {
      setIsGenerating(false);
    }
  };
  
  const toggleExpand = () => {
    setExpanded(!expanded);
  };
  
  const toggleGenerator = () => {
    setShowGenerator(!showGenerator);
  };

  const currentMapUrl = currentMapData?.image_url || mapUrl;
  
  return (
    <div className={`battle-map ${expanded ? 'expanded' : ''}`}>
      <div className="battle-map-header">
        <h3>Battle Map</h3>
        <div className="header-controls">
          {showControls && (
            <button onClick={toggleGenerator} className="control-button">
              {showGenerator ? 'Hide Controls' : 'Show Controls'}
            </button>
          )}
          <button onClick={toggleExpand} className="toggle-button">
            {expanded ? 'Minimize' : 'Expand'}
          </button>
        </div>
      </div>
      
      {showControls && showGenerator && (
        <MapGeneratorControls
          templates={templates}
          onGenerateMap={handleGenerateMap}
          onGenerateVariation={handleGenerateVariation}
          currentMapData={currentMapData}
          isGenerating={isGenerating}
        />
      )}
      
      <div className="map-container">
        {isGenerating ? (
          <div className="loading-state">
            <p>Generating battle map...</p>
            <div className="loading-spinner"></div>
          </div>
        ) : currentMapUrl ? (
          <div className="map-display">
            <img src={currentMapUrl} alt="Tactical Battle Map" />
            {currentMapData && (
              <div className="map-info">
                <h4>{currentMapData.name}</h4>
                <p>{currentMapData.description}</p>
                {currentMapData.tactical_info && (
                  <div className="tactical-info">
                    <small>
                      Grid: {currentMapData.tactical_info.grid_size?.width}x{currentMapData.tactical_info.grid_size?.height} |
                      Recommended: {currentMapData.tactical_info.recommended_participants?.optimal} participants
                    </small>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="empty-map-state">
            <p>No battle map available</p>
            {showControls && (
              <button onClick={toggleGenerator} className="generate-button">
                Generate Battle Map
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

interface MapGeneratorControlsProps {
  templates: any;
  onGenerateMap: (environment: any) => void;
  onGenerateVariation: (variationType: string) => void;
  currentMapData: any;
  isGenerating: boolean;
}

const MapGeneratorControls: React.FC<MapGeneratorControlsProps> = ({
  templates,
  onGenerateMap,
  onGenerateVariation,
  currentMapData,
  isGenerating
}) => {
  const [environment, setEnvironment] = useState({
    location: '',
    terrain: 'plain',
    size: 'medium',
    features: [] as string[],
    lighting: 'normal',
    weather: 'clear',
    template: ''
  });

  const terrainOptions = ['plain', 'forest', 'mountain', 'swamp', 'desert', 'ice', 'dungeon', 'urban'];
  const sizeOptions = ['small', 'medium', 'large', 'massive'];
  const lightingOptions = ['normal', 'dim', 'bright', 'dark', 'magical', 'flickering'];
  const weatherOptions = ['clear', 'rain', 'fog', 'snow', 'storm', 'wind'];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!environment.location.trim()) return;
    onGenerateMap(environment);
  };

  const addFeature = (feature: string) => {
    if (!environment.features.includes(feature)) {
      setEnvironment(prev => ({
        ...prev,
        features: [...prev.features, feature]
      }));
    }
  };

  const removeFeature = (feature: string) => {
    setEnvironment(prev => ({
      ...prev,
      features: prev.features.filter(f => f !== feature)
    }));
  };

  return (
    <div className="map-generator-controls">
      <form onSubmit={handleSubmit} className="generator-form">
        <div className="form-row">
          <div className="form-group">
            <label>Location:</label>
            <input
              type="text"
              value={environment.location}
              onChange={(e) => setEnvironment(prev => ({ ...prev, location: e.target.value }))}
              placeholder="e.g., abandoned castle, dark forest"
              disabled={isGenerating}
            />
          </div>
          
          <div className="form-group">
            <label>Template:</label>
            <select
              value={environment.template}
              onChange={(e) => setEnvironment(prev => ({ ...prev, template: e.target.value }))}
              disabled={isGenerating}
            >
              <option value="">None</option>
              {templates?.templates && Object.keys(templates.templates).map(template => (
                <option key={template} value={template}>
                  {template.replace('_', ' ').toUpperCase()}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Terrain:</label>
            <select
              value={environment.terrain}
              onChange={(e) => setEnvironment(prev => ({ ...prev, terrain: e.target.value }))}
              disabled={isGenerating}
            >
              {terrainOptions.map(terrain => (
                <option key={terrain} value={terrain}>{terrain}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Size:</label>
            <select
              value={environment.size}
              onChange={(e) => setEnvironment(prev => ({ ...prev, size: e.target.value }))}
              disabled={isGenerating}
            >
              {sizeOptions.map(size => (
                <option key={size} value={size}>{size}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Lighting:</label>
            <select
              value={environment.lighting}
              onChange={(e) => setEnvironment(prev => ({ ...prev, lighting: e.target.value }))}
              disabled={isGenerating}
            >
              {lightingOptions.map(lighting => (
                <option key={lighting} value={lighting}>{lighting}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Weather:</label>
            <select
              value={environment.weather}
              onChange={(e) => setEnvironment(prev => ({ ...prev, weather: e.target.value }))}
              disabled={isGenerating}
            >
              {weatherOptions.map(weather => (
                <option key={weather} value={weather}>{weather}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-group">
          <label>Features:</label>
          <div className="features-container">
            {environment.features.map(feature => (
              <span key={feature} className="feature-tag">
                {feature}
                <button 
                  type="button" 
                  onClick={() => removeFeature(feature)}
                  className="remove-feature"
                  disabled={isGenerating}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
          
          {environment.template && templates?.templates?.[environment.template]?.common_features && (
            <div className="template-features">
              <small>Suggested features:</small>
              {templates.templates[environment.template].common_features.map((feature: string) => (
                <button
                  key={feature}
                  type="button"
                  onClick={() => addFeature(feature)}
                  className="add-feature"
                  disabled={isGenerating || environment.features.includes(feature)}
                >
                  + {feature}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="form-actions">
          <button type="submit" disabled={isGenerating || !environment.location.trim()}>
            Generate Map
          </button>
          
          {currentMapData && (
            <div className="variation-buttons">
              <button 
                type="button" 
                onClick={() => onGenerateVariation('minor')}
                disabled={isGenerating}
              >
                Minor Variation
              </button>
              <button 
                type="button" 
                onClick={() => onGenerateVariation('lighting')}
                disabled={isGenerating}
              >
                Change Lighting
              </button>
              <button 
                type="button" 
                onClick={() => onGenerateVariation('weather')}
                disabled={isGenerating}
              >
                Change Weather
              </button>
            </div>
          )}
        </div>
      </form>
    </div>
  );
};

export default BattleMap;
