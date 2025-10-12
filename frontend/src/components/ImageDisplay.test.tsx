import { render, screen } from "@testing-library/react";
import ImageDisplay from "./ImageDisplay";
import styles from "./ImageDisplay.module.css";

describe("ImageDisplay", () => {
  it("renders image when imageUrl is provided", () => {
    const imageUrl = "https://example.com/test-image.jpg";
    render(<ImageDisplay imageUrl={imageUrl} />);

    const image = screen.getByRole("img");
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute("src", imageUrl);
    expect(image).toHaveAttribute("alt", "Game Visualization");
  });

  it("renders empty state when imageUrl is null", () => {
    render(<ImageDisplay imageUrl={null} />);

    expect(screen.getByText("No image available")).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("renders empty state when imageUrl is empty string", () => {
    render(<ImageDisplay imageUrl="" />);

    expect(screen.getByText("No image available")).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("has correct CSS classes", () => {
    const { container } = render(<ImageDisplay imageUrl="test.jpg" />);

    expect(
      container.querySelector(`.${styles.imageDisplay}`)
    ).toBeInTheDocument();
    expect(
      container.querySelector(`.${styles.imageContainer}`)
    ).toBeInTheDocument();
  });

  it("has correct CSS classes for empty state", () => {
    const { container } = render(<ImageDisplay imageUrl={null} />);

    expect(
      container.querySelector(`.${styles.imageDisplay}`)
    ).toBeInTheDocument();
    expect(
      container.querySelector(`.${styles.imageContainer}`)
    ).toBeInTheDocument();
    expect(
      container.querySelector(`.${styles.emptyImageState}`)
    ).toBeInTheDocument();
  });
});
