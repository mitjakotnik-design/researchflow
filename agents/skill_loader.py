"""
ResearchFlow Skills Integration Module

Provides Python interface to load and use SKILL.md documentation.

Usage:
    from agents.skills import SkillLoader, get_skill
    
    # Load a skill
    research_skill = get_skill("research-cluster")
    
    # Access skill metadata
    print(research_skill.name)
    print(research_skill.description)
    
    # Get system prompt for an agent
    prompt = get_system_prompt("researcher")
"""

import logging
import os
import re
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class SkillMetadata:
    """Parsed SKILL.md metadata."""
    name: str
    description: str
    argument_hint: Optional[str] = None
    user_invocable: bool = False
    apply_to: Optional[str] = None
    tools: List[str] = field(default_factory=list)
    model: Optional[str] = None
    
    # Parsed content sections
    sections: Dict[str, str] = field(default_factory=dict)
    
    # Path info
    file_path: Optional[Path] = None
    cluster: Optional[str] = None
    agent_name: Optional[str] = None


class SkillLoader:
    """Load and parse SKILL.md files."""
    
    def __init__(self, skills_dir: Optional[Path] = None):
        if skills_dir is None:
            # Default to the skills directory relative to this file
            skills_dir = Path(__file__).parent / "skills"
        self.skills_dir = Path(skills_dir)
        self._cache: Dict[str, SkillMetadata] = {}
        logger.debug(f"SkillLoader initialized with skills_dir: {self.skills_dir}")
    
    def load_skill(self, skill_path: str) -> SkillMetadata:
        """
        Load a skill by path.
        
        Args:
            skill_path: Relative path like "research-cluster" or 
                       "research-cluster/researcher"
        
        Returns:
            SkillMetadata with parsed content
        """
        cache_key = skill_path
        if cache_key in self._cache:
            logger.debug(f"Returning cached skill: {skill_path}")
            return self._cache[cache_key]
        
        # Find SKILL.md file
        full_path = self.skills_dir / skill_path / "SKILL.md"
        if not full_path.exists():
            raise FileNotFoundError(f"Skill not found: {full_path}")
        
        # Parse the file
        metadata = self._parse_skill_file(full_path)
        
        # Add path info
        parts = skill_path.split("/")
        if len(parts) == 1:
            metadata.cluster = parts[0]
        elif len(parts) == 2:
            metadata.cluster = parts[0]
            metadata.agent_name = parts[1]
        
        self._cache[cache_key] = metadata
        return metadata
    
    def _parse_skill_file(self, file_path: Path) -> SkillMetadata:
        """Parse a SKILL.md file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract YAML frontmatter
        yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not yaml_match:
            raise ValueError(f"No YAML frontmatter in {file_path}")
        
        yaml_content = yaml_match.group(1)
        frontmatter = yaml.safe_load(yaml_content)
        
        # Extract markdown body
        body = content[yaml_match.end():].strip()
        
        # Parse sections
        sections = self._parse_sections(body)
        
        return SkillMetadata(
            name=frontmatter.get('name', ''),
            description=frontmatter.get('description', ''),
            argument_hint=frontmatter.get('argument-hint'),
            user_invocable=frontmatter.get('user-invocable', False),
            apply_to=frontmatter.get('applyTo'),
            tools=frontmatter.get('tools', []),
            model=frontmatter.get('model'),
            sections=sections,
            file_path=file_path
        )
    
    def _parse_sections(self, body: str) -> Dict[str, str]:
        """Parse markdown sections by headers."""
        sections = {}
        current_section = "intro"
        current_content = []
        
        for line in body.split('\n'):
            if line.startswith('## '):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                # Start new section
                current_section = line[3:].strip().lower().replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def list_skills(self) -> List[str]:
        """List all available skills."""
        skills = []
        
        for cluster_dir in self.skills_dir.iterdir():
            if cluster_dir.is_dir() and not cluster_dir.name.startswith('.'):
                # Cluster level
                skill_file = cluster_dir / "SKILL.md"
                if skill_file.exists():
                    skills.append(cluster_dir.name)
                
                # Agent level
                for agent_dir in cluster_dir.iterdir():
                    if agent_dir.is_dir():
                        agent_skill = agent_dir / "SKILL.md"
                        if agent_skill.exists():
                            skills.append(f"{cluster_dir.name}/{agent_dir.name}")
        
        return sorted(skills)
    
    def get_system_prompt(self, agent_name: str) -> Optional[str]:
        """
        Extract system prompt for an agent.
        
        Args:
            agent_name: Agent name like "researcher" or "writer"
        
        Returns:
            System prompt text or None if not found
        """
        # Search for agent skill
        for cluster in ["research-cluster", "writing-cluster", "quality-cluster"]:
            try:
                skill = self.load_skill(f"{cluster}/{agent_name}")
                system_prompt_section = skill.sections.get('system_prompt', '')
                
                # Extract code block content
                code_match = re.search(r'```(?:text)?\s*\n(.*?)\n```', 
                                       system_prompt_section, re.DOTALL)
                if code_match:
                    return code_match.group(1).strip()
            except FileNotFoundError:
                continue
        
        return None
    
    def get_actions(self, agent_name: str) -> List[Dict[str, str]]:
        """
        Get available actions for an agent.
        
        Args:
            agent_name: Agent name like "researcher"
        
        Returns:
            List of action dictionaries with name, description, parameters
        """
        for cluster in ["research-cluster", "writing-cluster", "quality-cluster"]:
            try:
                skill = self.load_skill(f"{cluster}/{agent_name}")
                actions_section = skill.sections.get('akcije', '') or skill.sections.get('actions', '')
                
                # Parse markdown table
                actions = []
                for line in actions_section.split('\n'):
                    if line.startswith('|') and '|--|' not in line:
                        parts = [p.strip() for p in line.split('|')[1:-1]]
                        if len(parts) >= 3 and parts[0] and not parts[0].startswith('Akcija'):
                            actions.append({
                                "name": parts[0].strip('`'),
                                "description": parts[1],
                                "parameters": parts[2] if len(parts) > 2 else ""
                            })
                
                return actions
            except FileNotFoundError:
                continue
        
        return []


# Module-level singleton
_loader: Optional[SkillLoader] = None


def get_loader() -> SkillLoader:
    """Get or create the skill loader singleton."""
    global _loader
    if _loader is None:
        _loader = SkillLoader()
    return _loader


def get_skill(skill_path: str) -> SkillMetadata:
    """
    Get a skill by path.
    
    Args:
        skill_path: Like "research-cluster" or "research-cluster/researcher"
    
    Returns:
        SkillMetadata object
    """
    return get_loader().load_skill(skill_path)


def get_system_prompt(agent_name: str) -> Optional[str]:
    """
    Get system prompt for an agent.
    
    Args:
        agent_name: Like "researcher", "writer", "fact_checker"
    
    Returns:
        System prompt text or None
    """
    # Normalize name (underscores to dashes)
    normalized = agent_name.replace('_', '-')
    return get_loader().get_system_prompt(normalized)


def list_all_skills() -> List[str]:
    """List all available skills."""
    return get_loader().list_skills()


# Config loader
def load_config() -> Dict[str, Any]:
    """Load the skills config.yaml."""
    config_path = Path(__file__).parent / "skills" / "config.yaml"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


if __name__ == "__main__":
    # Demo
    print("Available Skills:")
    for skill in list_all_skills():
        print(f"  - {skill}")
    
    print("\nLoading research-cluster skill:")
    skill = get_skill("research-cluster")
    print(f"  Name: {skill.name}")
    print(f"  User Invocable: {skill.user_invocable}")
    
    print("\nSystem prompt for 'researcher':")
    prompt = get_system_prompt("researcher")
    if prompt:
        print(f"  {prompt[:200]}...")
