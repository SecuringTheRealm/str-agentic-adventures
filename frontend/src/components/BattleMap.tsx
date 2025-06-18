import type React from "react";
import { useState } from "react";
import styles from "./BattleMap.module.css";

interface BattleMapProps {
	mapUrl: string | null;
}

const BattleMap: React.FC<BattleMapProps> = ({ mapUrl }) => {
	const [expanded, setExpanded] = useState<boolean>(false);

	const toggleExpand = () => {
		setExpanded(!expanded);
	};

	return (
		<div className={`${styles.battleMap} ${expanded ? styles.expanded : ""}`}>
			<div className={styles.battleMapHeader}>
				<h3>Battle Map</h3>
				<button type="button" onClick={toggleExpand} className={styles.toggleButton}>
					{expanded ? "Minimize" : "Expand"}
				</button>
			</div>

			<div className={styles.mapContainer}>
				{mapUrl ? (
					<img src={mapUrl} alt="Tactical Battle Map" />
				) : (
					<div className={styles.emptyMapState}>
						<p>No battle map available</p>
					</div>
				)}
			</div>
		</div>
	);
};

export default BattleMap;
