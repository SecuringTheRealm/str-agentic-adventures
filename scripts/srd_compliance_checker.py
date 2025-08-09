#!/usr/bin/env python3
"""
SRD Rules Compliance Checker
Parses the D&D 5e SRD document to extract rules and verify implementation compliance.
"""

import re
from pathlib import Path
from typing import Dict, List, Set


class SRDRulesChecker:
    def __init__(self, srd_path: str, repo_root: str):
        self.srd_path = Path(srd_path)
        self.repo_root = Path(repo_root)
        self.rules_found = {
            "spells": [],
            "classes": [],
            "races": [],
            "equipment": [],
            "combat_rules": [],
            "ability_scores": [],
            "skills": [],
            "conditions": [],
            "magic_items": [],
        }

    def parse_srd(self):
        """Parse the SRD document to extract rules and content."""
        print("📖 Parsing SRD document...")

        with open(self.srd_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract spells
        self._extract_spells(content)

        # Extract classes
        self._extract_classes(content)

        # Extract races
        self._extract_races(content)

        # Extract equipment
        self._extract_equipment(content)

        # Extract combat rules
        self._extract_combat_rules(content)

        # Extract conditions
        self._extract_conditions(content)

        print(
            f"✅ Parsed SRD: Found {sum(len(rules) for rules in self.rules_found.values())} rule elements"
        )

    def _extract_spells(self, content: str):
        """Extract spell names and details from SRD."""
        # Look for spell sections
        spell_pattern = r"(?:^|\n)#+\s*([A-Z][a-zA-Z\s\']+)\s*\n.*?(?:\*\*Level.*?\*\*|\*\*School.*?\*\*)"
        spells = re.findall(spell_pattern, content, re.MULTILINE | re.DOTALL)

        # Also look for direct spell entries
        spell_entries = re.findall(
            r"\n([A-Z][a-zA-Z\s\']+)\n.*?(?:1st-level|2nd-level|3rd-level|4th-level|5th-level|6th-level|7th-level|8th-level|9th-level|cantrip)",
            content,
            re.MULTILINE,
        )

        all_spells = set(spells + spell_entries)

        # Filter common words that aren't spells
        common_words = {
            "The",
            "A",
            "An",
            "And",
            "Or",
            "But",
            "In",
            "On",
            "At",
            "To",
            "For",
            "Of",
            "With",
            "By",
        }
        spell_list = [
            spell.strip()
            for spell in all_spells
            if spell.strip() not in common_words and len(spell.strip()) > 2
        ]

        self.rules_found["spells"] = spell_list[:100]  # Limit for demo

    def _extract_classes(self, content: str):
        """Extract character class information."""
        # Look for class sections
        class_pattern = r"## ([A-Z][a-z]+)\s*\n.*?(?=## [A-Z]|$)"
        classes = re.findall(class_pattern, content, re.MULTILINE | re.DOTALL)

        # Known D&D 5e classes
        known_classes = [
            "Barbarian",
            "Bard",
            "Cleric",
            "Druid",
            "Fighter",
            "Monk",
            "Paladin",
            "Ranger",
            "Rogue",
            "Sorcerer",
            "Warlock",
            "Wizard",
        ]

        found_classes = [cls for cls in classes if cls in known_classes]
        self.rules_found["classes"] = found_classes

    def _extract_races(self, content: str):
        """Extract character race information."""
        # Look for race sections
        race_pattern = (
            r"### ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\n.*?(?:size|speed|ability)"
        )
        races = re.findall(
            race_pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE
        )

        # Known D&D 5e races
        known_races = [
            "Human",
            "Elf",
            "Dwarf",
            "Halfling",
            "Dragonborn",
            "Gnome",
            "Half-Elf",
            "Half-Orc",
            "Tiefling",
        ]

        found_races = [
            race
            for race in races
            if any(known_race in race for known_race in known_races)
        ]
        self.rules_found["races"] = found_races[:20]  # Limit for demo

    def _extract_equipment(self, content: str):
        """Extract equipment and weapon information."""
        # Look for equipment tables and weapon entries
        equipment_pattern = r"\|\s*([A-Z][a-zA-Z\s]+)\s*\|\s*\d+\s*(?:gp|sp|cp)"
        equipment = re.findall(equipment_pattern, content)

        self.rules_found["equipment"] = list(set(equipment))[:50]  # Limit for demo

    def _extract_combat_rules(self, content: str):
        """Extract combat-related rules."""
        combat_sections = [
            "Attack Rolls",
            "Damage Rolls",
            "Initiative",
            "Actions in Combat",
            "Bonus Actions",
            "Reactions",
            "Movement",
            "Opportunity Attacks",
        ]

        found_rules = []
        for rule in combat_sections:
            if rule.lower() in content.lower():
                found_rules.append(rule)

        self.rules_found["combat_rules"] = found_rules

    def _extract_conditions(self, content: str):
        """Extract status conditions."""
        conditions = [
            "Blinded",
            "Charmed",
            "Deafened",
            "Frightened",
            "Grappled",
            "Incapacitated",
            "Invisible",
            "Paralyzed",
            "Petrified",
            "Poisoned",
            "Prone",
            "Restrained",
            "Stunned",
            "Unconscious",
        ]

        found_conditions = []
        for condition in conditions:
            if condition.lower() in content.lower():
                found_conditions.append(condition)

        self.rules_found["conditions"] = found_conditions

    def check_implementation_compliance(self) -> Dict[str, Dict[str, any]]:
        """Check if SRD rules are implemented in the codebase."""
        print("🔍 Checking implementation compliance...")

        compliance_report = {}

        # Check spell implementation
        compliance_report["spells"] = self._check_spell_compliance()

        # Check class implementation
        compliance_report["classes"] = self._check_class_compliance()

        # Check race implementation
        compliance_report["races"] = self._check_race_compliance()

        # Check equipment implementation
        compliance_report["equipment"] = self._check_equipment_compliance()

        # Check combat rules implementation
        compliance_report["combat_rules"] = self._check_combat_compliance()

        return compliance_report

    def _check_spell_compliance(self) -> Dict[str, any]:
        """Check if spells are implemented."""
        # Look for spell implementations in code
        spell_files = list(self.repo_root.glob("**/*spell*.py")) + list(
            self.repo_root.glob("**/*magic*.py")
        )

        implemented_spells = set()
        for file_path in spell_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    for spell in self.rules_found["spells"]:
                        if (
                            spell.lower().replace(" ", "_") in content
                            or spell.lower().replace(" ", "") in content
                        ):
                            implemented_spells.add(spell)
            except Exception:
                continue

        total_spells = len(self.rules_found["spells"])
        implemented_count = len(implemented_spells)

        return {
            "total": total_spells,
            "implemented": implemented_count,
            "percentage": (implemented_count / total_spells * 100)
            if total_spells > 0
            else 0,
            "missing": list(set(self.rules_found["spells"]) - implemented_spells)[
                :10
            ],  # Show first 10 missing
        }

    def _check_class_compliance(self) -> Dict[str, any]:
        """Check if character classes are implemented."""
        # Look for class implementations
        class_files = list(self.repo_root.glob("**/*class*.py")) + list(
            self.repo_root.glob("**/*character*.py")
        )

        implemented_classes = set()
        for file_path in class_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    for char_class in self.rules_found["classes"]:
                        if char_class.lower() in content:
                            implemented_classes.add(char_class)
            except Exception:
                continue

        total_classes = len(self.rules_found["classes"])
        implemented_count = len(implemented_classes)

        return {
            "total": total_classes,
            "implemented": implemented_count,
            "percentage": (implemented_count / total_classes * 100)
            if total_classes > 0
            else 0,
            "missing": list(set(self.rules_found["classes"]) - implemented_classes),
        }

    def _check_race_compliance(self) -> Dict[str, any]:
        """Check if character races are implemented."""
        race_files = list(self.repo_root.glob("**/*race*.py")) + list(
            self.repo_root.glob("**/*character*.py")
        )

        implemented_races = set()
        for file_path in race_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    for race in self.rules_found["races"]:
                        if race.lower() in content:
                            implemented_races.add(race)
            except Exception:
                continue

        total_races = len(self.rules_found["races"])
        implemented_count = len(implemented_races)

        return {
            "total": total_races,
            "implemented": implemented_count,
            "percentage": (implemented_count / total_races * 100)
            if total_races > 0
            else 0,
            "missing": list(set(self.rules_found["races"]) - implemented_races)[:10],
        }

    def _check_equipment_compliance(self) -> Dict[str, any]:
        """Check if equipment is implemented."""
        equipment_files = (
            list(self.repo_root.glob("**/*equipment*.py"))
            + list(self.repo_root.glob("**/*inventory*.py"))
            + list(self.repo_root.glob("**/*item*.py"))
        )

        implemented_equipment = set()
        for file_path in equipment_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    for item in self.rules_found["equipment"]:
                        if item.lower() in content:
                            implemented_equipment.add(item)
            except Exception:
                continue

        total_equipment = len(self.rules_found["equipment"])
        implemented_count = len(implemented_equipment)

        return {
            "total": total_equipment,
            "implemented": implemented_count,
            "percentage": (implemented_count / total_equipment * 100)
            if total_equipment > 0
            else 0,
            "missing": list(set(self.rules_found["equipment"]) - implemented_equipment)[
                :10
            ],
        }

    def _check_combat_compliance(self) -> Dict[str, any]:
        """Check if combat rules are implemented."""
        combat_files = (
            list(self.repo_root.glob("**/*combat*.py"))
            + list(self.repo_root.glob("**/*battle*.py"))
            + list(self.repo_root.glob("**/*fight*.py"))
        )

        implemented_rules = set()
        for file_path in combat_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    for rule in self.rules_found["combat_rules"]:
                        if (
                            rule.lower().replace(" ", "_") in content
                            or rule.lower().replace(" ", "") in content
                        ):
                            implemented_rules.add(rule)
            except Exception:
                continue

        total_rules = len(self.rules_found["combat_rules"])
        implemented_count = len(implemented_rules)

        return {
            "total": total_rules,
            "implemented": implemented_count,
            "percentage": (implemented_count / total_rules * 100)
            if total_rules > 0
            else 0,
            "missing": list(set(self.rules_found["combat_rules"]) - implemented_rules),
        }

    def generate_compliance_report(self, compliance_data: Dict) -> str:
        """Generate a comprehensive compliance report."""
        report = []
        report.append("# SRD 5.2.1 Rules Compliance Report")
        report.append("=" * 50)
        report.append("")

        total_percentage = sum(
            category["percentage"] for category in compliance_data.values()
        ) / len(compliance_data)
        report.append(f"## Overall Compliance: {total_percentage:.1f}%")
        report.append("")

        for category, data in compliance_data.items():
            status_icon = (
                "🟢"
                if data["percentage"] >= 80
                else "🟡"
                if data["percentage"] >= 50
                else "🔴"
            )
            report.append(
                f"### {status_icon} {category.upper()} - {data['percentage']:.1f}% Implemented"
            )
            report.append(f"- **Total in SRD**: {data['total']}")
            report.append(f"- **Implemented**: {data['implemented']}")
            report.append(f"- **Missing**: {len(data['missing'])}")

            if data["missing"]:
                report.append(
                    f"- **Examples of Missing**: {', '.join(data['missing'][:5])}"
                )
            report.append("")

        return "\n".join(report)


def main():
    """Main function to run SRD compliance checking."""
    repo_root = "/home/runner/work/str-agentic-adventures/str-agentic-adventures"
    srd_path = f"{repo_root}/docs/reference/srd-5.2.1.md"

    checker = SRDRulesChecker(srd_path, repo_root)
    checker.parse_srd()

    compliance_data = checker.check_implementation_compliance()
    report = checker.generate_compliance_report(compliance_data)

    # Save report (output to temp location to avoid committing generated reports)
    import tempfile

    temp_dir = Path(tempfile.gettempdir()) / "str-agentic-adventures"
    temp_dir.mkdir(exist_ok=True)
    report_file = temp_dir / "srd_compliance_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ SRD compliance report saved to: {report_file}")
    print("\n" + "=" * 60)
    print(report)


if __name__ == "__main__":
    main()
