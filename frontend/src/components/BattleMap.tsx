import type React from "react";
import { useState } from "react";
import "./BattleMap.css";

interface BattleMapProps {
	mapUrl: string | null;
}

const BattleMap: React.FC<BattleMapProps> = ({ mapUrl }) => {
	const [expanded, setExpanded] = useState<boolean>(false);

	const toggleExpand = () => {
		setExpanded(!expanded);
	};

	return (
		<div className={`battle-map ${expanded ? "expanded" : ""}`}>
			<div className="battle-map-header">
				<h3>Battle Map</h3>
				<button type="button" onClick={toggleExpand} className="toggle-button">
					{expanded ? "Minimize" : "Expand"}
				</button>
			</div>

			<div className="map-container">
				{mapUrl ? (
					<img src={mapUrl} alt="Tactical Battle Map" />
				) : (
					<div className="empty-map-state">
						<p>No battle map available</p>
					</div>
				)}
			</div>
		</div>
	);
};

export default BattleMap;
