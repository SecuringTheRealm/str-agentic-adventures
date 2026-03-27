import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "./App";

// Mock all API calls to avoid network issues in tests
vi.mock("./services/api", () => ({
  getCampaignTemplates: vi.fn().mockResolvedValue([]),
  getCampaigns: vi.fn().mockResolvedValue({ campaigns: [] }),
  createCampaign: vi.fn(),
  deleteCampaign: vi.fn(),
  cloneCampaign: vi.fn(),
}));

describe("App Campaign Setup Layout", () => {
  it("renders main content area", () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    const main = document.querySelector(".App-main");
    expect(main).toBeInTheDocument();
  });

  it("renders campaign selection at root route", async () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>
    );

    await screen.findByText("Campaign Hub");
  });
});
