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
	const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
	const [showTooltip, setShowTooltip] = useState(false);

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();

		// Clear previous validation errors
		setValidationErrors({});
		setError(null);

		// Validate required fields
		const errors: Record<string, string> = {};
		if (!campaignName.trim()) {
			errors.campaignName = "Please enter a campaign name.";
		}
		if (!setting.trim()) {
			errors.setting = "Please enter a campaign setting.";
		}

		if (Object.keys(errors).length > 0) {
			setValidationErrors(errors);
			return;
		}

		setIsSubmitting(true);

		try {
			// Parse homebrew rules into array
			const homebrewRulesList = homebrewRules
				.split("\n")
				.map((rule) => rule.trim())
				.filter((rule) => rule !== "");

			const campaignData: CampaignCreateRequest = {
				name: campaignName.trim(),
				setting: setting.trim(),
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
						placeholder="Shadows Over Eldara"
						disabled={isSubmitting}
						required
						className={validationErrors.campaignName ? 'error' : ''}
					/>
					{validationErrors.campaignName && (
						<div className="validation-error">{validationErrors.campaignName}</div>
					)}
				</div>

				<div className="form-group">
					<div className="label-with-help">
						<label htmlFor="setting">Campaign Setting</label>
						<div
							className="help-icon"
							onMouseEnter={() => setShowTooltip(true)}
							onMouseLeave={() => setShowTooltip(false)}
						>
							ⓘ
							{showTooltip && (
								<div className="tooltip">
									Example: 'Medieval fantasy city threatened by dragons'
								</div>
							)}
						</div>
					</div>
					<div className="textarea-container">
						<textarea
							id="setting"
							value={setting}
							onChange={(e) => setSetting(e.target.value)}
							placeholder="Describe your campaign setting (e.g., medieval fantasy world, cyberpunk future)"
							disabled={isSubmitting}
							required
							maxLength={500}
							className={validationErrors.setting ? 'error' : ''}
						/>
						<div className="character-count">{setting.length}/500 characters</div>
					</div>
					{validationErrors.setting && (
						<div className="validation-error">{validationErrors.setting}</div>
					)}
				</div>

				<div className="form-group">
					<label htmlFor="tone">Campaign Tone</label>
					<div className="custom-select">
						<select
							id="tone"
							value={tone}
							onChange={(e) => setTone(e.target.value)}
							disabled={isSubmitting}
						>
							<option value="heroic">🛡️ Heroic</option>
							<option value="dark">💀 Dark</option>
							<option value="lighthearted">🃏 Humorous</option>
							<option value="gritty">⚔️ Gritty</option>
							<option value="mysterious">🔍 Mystery</option>
						</select>
					</div>
				</div>

				<div className="form-group optional">
					<label htmlFor="homebrew-rules">Homebrew Rules (Optional)</label>
					<textarea
						id="homebrew-rules"
						value={homebrewRules}
						onChange={(e) => setHomebrewRules(e.target.value)}
						placeholder="E.g., Critical hits double damage dice, No encumbrance rules"
						disabled={isSubmitting}
						className="optional-field"
					/>
				</div>

				<button
					type="submit"
					className={`create-button ${isSubmitting ? 'submitting' : ''}`}
					disabled={isSubmitting}
				>
					{isSubmitting ? (
						<span className="button-content">
							<span className="loading-spinner"></span>
							Creating...
						</span>
					) : (
						<span className="button-content">
							Create Campaign
							<span className="button-checkmark">✓</span>
						</span>
					)}
				</button>
			</form>
		</div>
	);
};

export default CampaignCreation;
