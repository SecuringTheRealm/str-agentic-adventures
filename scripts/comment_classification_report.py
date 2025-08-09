#!/usr/bin/env python3
"""
Comment Classification Report Generator
Classifies and analyzes all comments in the repository into:
1. Annotation/documentation comments (type hints, docstrings, etc.)
2. Future work comments ("in a real implementation", TODO, FIXME, etc.)
"""

import os
import re
from pathlib import Path


class CommentClassifier:
    def __init__(self, repo_root: str) -> None:
        self.repo_root = Path(repo_root)
        self.future_work_patterns = [
            r"(?i)in a real implementation",
            r"(?i)todo\b",
            r"(?i)fixme\b",
            r"(?i)in a real system",
            r"(?i)in a real\b",
            r"(?i)would be\b.*(?:more|better|different)",
            r"(?i)placeholder\b",
            r"(?i)temporary\b",
            r"(?i)basic.*implementation",
            r"(?i)simple.*implementation",
        ]
        self.documentation_patterns = [
            r'^\s*""".*?"""',  # Python docstrings
            r"^\s*\'\'\'.*?\'\'\'",  # Python docstrings (single quotes)
            r"^\s*#\s*@param",  # Parameter documentation
            r"^\s*#\s*@return",  # Return documentation
            r"^\s*#\s*Args:",  # Function arguments
            r"^\s*#\s*Returns:",  # Function returns
            r"^\s*//\s*@",  # JSDoc style
            r"^\s*/\*\*",  # JSDoc start
            r"^\s*\*\s*@",  # JSDoc parameters
            r"Type:",  # Type annotations
            r"interface\s+\w+",  # TypeScript interfaces
        ]

        self.results = {"documentation": [], "future_work": [], "regular": []}

    def scan_file(self, file_path: Path) -> list[tuple[str, int, str, str]]:
        """Scan a file and return classified comments."""
        comments = []

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                comment_text = self.extract_comment(line, file_path.suffix)
                if comment_text:
                    classification = self.classify_comment(comment_text)
                    comments.append(
                        (
                            str(file_path.relative_to(self.repo_root)),
                            line_num,
                            comment_text.strip(),
                            classification,
                        )
                    )

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

        return comments

    def extract_comment(self, line: str, file_extension: str) -> str:
        """Extract comment text from a line based on file type."""
        line = line.strip()

        if file_extension in [".py"]:
            # Python comments
            if line.startswith("#"):
                return line[1:].strip()
            if '"""' in line or "'''" in line:
                return line  # Docstring

        elif file_extension in [".ts", ".tsx", ".js", ".jsx"]:
            # JavaScript/TypeScript comments
            if line.startswith("//"):
                return line[2:].strip()
            if line.startswith("/*") or line.startswith("*"):
                return line.lstrip("/*").lstrip("*").strip()

        elif file_extension in [".md"]:
            # Markdown comments (HTML style)
            if "<!--" in line:
                return line

        return ""

    def classify_comment(self, comment: str) -> str:
        """Classify a comment as documentation, future work, or regular."""

        # Check for future work patterns
        for pattern in self.future_work_patterns:
            if re.search(pattern, comment):
                return "future_work"

        # Check for documentation patterns
        for pattern in self.documentation_patterns:
            if re.search(pattern, comment):
                return "documentation"

        # Check for common documentation keywords
        doc_keywords = [
            "param",
            "return",
            "args",
            "type",
            "interface",
            "class",
            "function",
            "method",
        ]
        if any(keyword in comment.lower() for keyword in doc_keywords):
            return "documentation"

        return "regular"

    def scan_repository(self) -> None:
        """Scan the entire repository for comments."""
        file_extensions = [".py", ".ts", ".tsx", ".js", ".jsx", ".md"]
        exclude_dirs = {
            ".git",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            "build",
            "dist",
        }

        for root, dirs, files in os.walk(self.repo_root):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in file_extensions:
                    comments = self.scan_file(file_path)
                    for file_rel, line_num, comment, classification in comments:
                        self.results[classification].append(
                            {
                                "file": file_rel,
                                "line": line_num,
                                "comment": comment,
                                "classification": classification,
                            }
                        )

    def generate_report(self) -> str:
        """Generate a comprehensive classification report."""
        report = []
        report.append("# Comment Classification Report")
        report.append("=" * 50)
        report.append("")

        # Summary
        total_comments = sum(len(self.results[category]) for category in self.results)
        report.append("## Summary")
        report.append(f"- **Total Comments Found**: {total_comments}")
        report.append(
            f"- **Documentation Comments**: {len(self.results['documentation'])}"
        )
        report.append(f"- **Future Work Comments**: {len(self.results['future_work'])}")
        report.append(f"- **Regular Comments**: {len(self.results['regular'])}")
        report.append("")

        # Future Work Comments (Priority)
        report.append("## 🔴 FUTURE WORK COMMENTS (REQUIRES IMPLEMENTATION)")
        report.append("-" * 60)

        if self.results["future_work"]:
            # Group by file for better organization
            by_file = {}
            for comment in self.results["future_work"]:
                file_path = comment["file"]
                if file_path not in by_file:
                    by_file[file_path] = []
                by_file[file_path].append(comment)

            for file_path, comments in sorted(by_file.items()):
                report.append(f"\n### {file_path}")
                for comment in comments:
                    report.append(f"- **Line {comment['line']}**: {comment['comment']}")

        else:
            report.append("✅ No future work comments found!")

        report.append("")

        # Documentation Comments
        report.append("## 📚 DOCUMENTATION COMMENTS")
        report.append("-" * 40)

        if self.results["documentation"]:
            doc_files = {comment["file"] for comment in self.results["documentation"]}
            report.append(f"Found documentation comments in {len(doc_files)} files:")
            for file_path in sorted(doc_files):
                count = len(
                    [c for c in self.results["documentation"] if c["file"] == file_path]
                )
                report.append(f"- {file_path}: {count} documentation comments")
        else:
            report.append("No documentation comments found.")

        report.append("")

        # Regular Comments
        report.append("## 💬 REGULAR COMMENTS")
        report.append("-" * 25)

        if self.results["regular"]:
            regular_files = {comment["file"] for comment in self.results["regular"]}
            report.append(f"Found regular comments in {len(regular_files)} files:")
            for file_path in sorted(regular_files):
                count = len(
                    [c for c in self.results["regular"] if c["file"] == file_path]
                )
                report.append(f"- {file_path}: {count} regular comments")
        else:
            report.append("No regular comments found.")

        return "\n".join(report)


def main() -> None:
    """Main function to run the comment classification."""
    repo_root = os.path.dirname(os.path.abspath(__file__))

    print("🔍 Scanning repository for comments...")
    classifier = CommentClassifier(repo_root)
    classifier.scan_repository()

    print("📝 Generating classification report...")
    report = classifier.generate_report()

    # Save report to file (output to temp location to avoid committing generated reports)
    import tempfile

    temp_dir = Path(tempfile.gettempdir()) / "str-agentic-adventures"
    temp_dir.mkdir(exist_ok=True)
    report_file = temp_dir / "comment_classification_report.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ Report saved to: {report_file}")
    print("\n" + "=" * 60)
    print(report)


if __name__ == "__main__":
    main()
