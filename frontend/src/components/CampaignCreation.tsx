import { useState } from "react";
import type React from "react";
import {
	type Campaign,
	type CampaignCreateRequest,
	createCampaign,
} from "../services/api";
import "./CampaignCreation.css";

interface CampaignCreationProps {
	onCampaignCreated: (campaign: Campaign) => void;
}

const CampaignCreation: React.FC<CampaignCreationProps> = ({
	onCampaignCreated,
}) => {
	const [campaignName, setCampaignName] = useState("");
	const [setting, setSetting] = useState("");
	const [tone, setTone] = useState("heroic");
	const [homebrewRules, setHomebrewRules] = useState("");
	const [isSubmitting, setIsSubmitting] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();

		if (!campaignName || !setting) {
			setError("Campaign name and setting are required.");
			return;
		}

		setIsSubmitting(true);
		setError(null);

		try {
			// Parse homebrew rules into array
			const homebrewRulesList = homebrewRules
				.split("\n")
				.map((rule) => rule.trim())
				.filter((rule) => rule !== "");

			const campaignData: CampaignCreateRequest = {
				name: campaignName,
				setting,
				tone,
				homebrew_rules: homebrewRulesList,
			};

			const result = await createCampaign(campaignData);
			onCampaignCreated(result);
		} catch (err) {
			setError("Failed to create campaign. Please try again.");
			console.error("Error creating campaign:", err);
		} finally {
			setIsSubmitting(false);
		}
	};

	return (
		<div className="campaign-creation">
			<h2>Create New Campaign</h2>

			{error && <div className="error-message">{error}</div>}

			<form onSubmit={handleSubmit}>
				<div className="form-group">
					<label htmlFor="campaign-name">Campaign Name</label>
					<input
						id="campaign-name"
						type="text"
						value={campaignName}
						onChange={(e) => setCampaignName(e.target.value)}
						placeholder="Enter campaign name"
						disabled={isSubmitting}
						required
					/>
				</div>

				<div className="form-group">
					<label htmlFor="setting">Campaign Setting</label>
					<textarea
						id="setting"
						value={setting}
						onChange={(e) => setSetting(e.target.value)}
						placeholder="Describe your campaign setting (e.g., medieval fantasy world, cyberpunk future)"
						disabled={isSubmitting}
						required
					/>
				</div>

				<div className="form-group">
					<label htmlFor="tone">Campaign Tone</label>
					<select
						id="tone"
						value={tone}
						onChange={(e) => setTone(e.target.value)}
						disabled={isSubmitting}
					>
						<option value="heroic">Heroic</option>
						<option value="gritty">Gritty</option>
						<option value="lighthearted">Lighthearted</option>
						<option value="epic">Epic</option>
						<option value="mysterious">Mysterious</option>
					</select>
				</div>

				<div className="form-group">
					<label htmlFor="homebrew-rules">Homebrew Rules (Optional)</label>
					<textarea
						id="homebrew-rules"
						value={homebrewRules}
						onChange={(e) => setHomebrewRules(e.target.value)}
						placeholder="Enter any homebrew rules (one per line)"
						disabled={isSubmitting}
					/>
				</div>

				<button type="submit" className="create-button" disabled={isSubmitting}>
					{isSubmitting ? "Creating..." : "Create Campaign"}
				</button>
			</form>
		</div>
	);
};

export default CampaignCreation;
