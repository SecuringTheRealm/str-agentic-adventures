#!/usr/bin/env python3
"""
Quick SRD Rules Compliance Checker - focused on key game elements.
"""

import re
from pathlib import Path


def check_basic_srd_compliance():
    """Check basic SRD compliance for core game elements."""
    repo_root = Path(__file__).resolve().parent

    # Core D&D 5e elements to check
    core_elements = {
        "classes": [
            "barbarian",
            "bard",
            "cleric",
            "druid",
            "fighter",
            "monk",
            "paladin",
            "ranger",
            "rogue",
            "sorcerer",
            "warlock",
            "wizard",
        ],
        "races": [
            "human",
            "elf",
            "dwarf",
            "halfling",
            "dragonborn",
            "gnome",
            "half-elf",
            "half-orc",
            "tiefling",
        ],
        "abilities": [
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        ],
        "conditions": [
            "blinded",
            "charmed",
            "deafened",
            "frightened",
            "grappled",
            "incapacitated",
            "invisible",
            "paralyzed",
            "petrified",
            "poisoned",
            "prone",
            "restrained",
            "stunned",
            "unconscious",
        ],
        "combat_actions": [
            "attack",
            "dodge",
            "dash",
            "disengage",
            "help",
            "hide",
            "ready",
            "search",
        ],
        "spell_levels": [
            "cantrip",
            "1st-level",
            "2nd-level",
            "3rd-level",
            "4th-level",
            "5th-level",
            "6th-level",
            "7th-level",
            "8th-level",
            "9th-level",
        ],
    }

    # Files to check for implementations
    py_files = list(repo_root.glob("**/*.py"))
    ts_files = list(repo_root.glob("**/*.ts")) + list(repo_root.glob("**/*.tsx"))

    all_content = ""
    for file_path in py_files + ts_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                all_content += f.read().lower() + "\n"
        except:
            continue

    # Check implementation coverage
    results = {}
    for category, elements in core_elements.items():
        implemented = []
        missing = []

        for element in elements:
            # Check various forms the element might appear in code
            patterns = [
                element,
                element.replace("-", "_"),
                element.replace(" ", "_"),
                f'"{element}"',
                f"'{element}'",
            ]

            if any(pattern in all_content for pattern in patterns):
                implemented.append(element)
            else:
                missing.append(element)

        results[category] = {
            "total": len(elements),
            "implemented": len(implemented),
            "missing": missing,
            "percentage": (len(implemented) / len(elements)) * 100 if elements else 0,
        }

    # Generate report
    report = []
    report.append("# Quick SRD 5.2.1 Compliance Check")
    report.append("=" * 50)
    report.append("")

    total_percentage = sum(cat["percentage"] for cat in results.values()) / len(results)
    report.append(f"## Overall Compliance: {total_percentage:.1f}%")
    report.append("")

    for category, data in results.items():
        status = (
            "🟢"
            if data["percentage"] >= 80
            else "🟡"
            if data["percentage"] >= 50
            else "🔴"
        )
        report.append(
            f"### {status} {category.upper()}: {data['percentage']:.1f}% ({data['implemented']}/{data['total']})"
        )

        if data["missing"]:
            report.append(f"**Missing**: {', '.join(data['missing'][:10])}")
        report.append("")

    # Specific recommendations
    report.append("## 🎯 Implementation Recommendations")
    report.append("")

    if results["classes"]["percentage"] < 100:
        report.append("### Character Classes")
        report.append(
            "- Implement missing character class support in character creation"
        )
        report.append("- Add class-specific features and abilities")
        report.append("")

    if results["spell_levels"]["percentage"] < 100:
        report.append("### Spell System")
        report.append("- Complete spell level implementation")
        report.append("- Add spell slot management for all levels")
        report.append("")

    if results["conditions"]["percentage"] < 100:
        report.append("### Status Conditions")
        report.append("- Implement missing status condition effects")
        report.append("- Add condition application and removal mechanics")
        report.append("")

    return "\n".join(report)


def main():
    report = check_basic_srd_compliance()

    # Save report
    report_file = Path(
        "/home/runner/work/str-agentic-adventures/str-agentic-adventures/docs/srd_compliance_report.md"
    )
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ Quick SRD compliance report saved to: {report_file}")
    print(report)


if __name__ == "__main__":
    main()
