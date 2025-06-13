// Utility functions and constants for item management

export type ItemRarity =
	| "common"
	| "uncommon"
	| "rare"
	| "very rare"
	| "legendary"
	| "artifact";

export const ITEM_RARITY_COLORS: Record<ItemRarity, string> = {
	common: "#9CA3AF", // Gray
	uncommon: "#10B981", // Green
	rare: "#3B82F6", // Blue
	"very rare": "#8B5CF6", // Purple
	legendary: "#F59E0B", // Orange/Gold
	artifact: "#EF4444", // Red
};

export const getRarityColor = (rarity?: string): string => {
	if (!rarity) return ITEM_RARITY_COLORS.common;
	return (
		ITEM_RARITY_COLORS[rarity.toLowerCase() as ItemRarity] ||
		ITEM_RARITY_COLORS.common
	);
};

export const formatItemValue = (value?: number): string => {
	if (value === undefined || value === null) return "";
	if (value === 0) return "0 gp";

	// Convert copper to gold pieces (100 cp = 1 gp)
	if (value >= 100) {
		const gp = Math.floor(value / 100);
		const remaining = value % 100;
		if (remaining === 0) {
			return `${gp} gp`;
		}
		return `${gp} gp ${remaining} cp`;
	}

	return `${value} cp`;
};

export const getRarityDisplayName = (rarity?: string): string => {
	if (!rarity) return "Common";
	return rarity.charAt(0).toUpperCase() + rarity.slice(1);
};
