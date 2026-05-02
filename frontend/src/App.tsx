import { useId } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import "./App.css";
import { Toaster } from "./components/ui/sonner";
import CampaignEditPage from "./pages/CampaignEditPage";
import CampaignNewPage from "./pages/CampaignNewPage";
import CampaignSelectionPage from "./pages/CampaignSelectionPage";
import CharacterNewPage from "./pages/CharacterNewPage";
import CharacterSelectionPage from "./pages/CharacterSelectionPage";
import GamePage from "./pages/GamePage";

function App() {
  const mainId = useId();

  return (
    <div className="App">
      <a href={`#${mainId}`} className="skip-link">
        Skip to main content
      </a>
      <Toaster richColors position="top-right" />
      <header className="App-header">
        <h1>Securing the Realm - Agentic Adventures</h1>
      </header>

      <main id={mainId} className="App-main">
        <Routes>
          <Route path="/" element={<CampaignSelectionPage />} />
          <Route path="/campaigns/new" element={<CampaignNewPage />} />
          <Route path="/campaigns/:id/edit" element={<CampaignEditPage />} />
          <Route
            path="/campaigns/:id/characters"
            element={<CharacterSelectionPage />}
          />
          <Route
            path="/campaigns/:id/characters/new"
            element={<CharacterNewPage />}
          />
          <Route
            path="/campaigns/:id/play/:characterId"
            element={<GamePage />}
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
