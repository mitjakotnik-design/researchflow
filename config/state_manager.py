"""Article state management with persistence and rollback."""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from .sections_config import SectionState, SectionStatus


class ArticlePhase(Enum):
    """Overall article processing phase."""
    INITIALIZATION = "initialization"
    RESEARCH = "research"
    DATA_EXTRACTION = "data_extraction"
    SYNTHESIS = "synthesis"
    WRITING = "writing"
    QUALITY_ASSURANCE = "quality_assurance"
    FINALIZATION = "finalization"
    COMPLETED = "completed"


class OrchestratorState(Enum):
    """Meta-orchestrator state."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_HUMAN = "waiting_human"
    ERROR = "error"
    COMPLETED = "completed"


@dataclass
class ResearchCache:
    """Cache for research results."""
    
    queries_executed: dict[str, list[dict]] = field(default_factory=dict)
    documents_retrieved: dict[str, dict] = field(default_factory=dict)
    synthesis_cache: dict[str, str] = field(default_factory=dict)
    
    def add_query_result(self, query: str, results: list[dict]) -> None:
        """Cache query results."""
        self.queries_executed[query] = results
    
    def get_cached_query(self, query: str) -> Optional[list[dict]]:
        """Get cached query results if available."""
        return self.queries_executed.get(query)


@dataclass
class QualitySnapshot:
    """Snapshot of quality metrics at a point in time."""
    
    timestamp: str
    iteration: int
    section_scores: dict[str, int]
    overall_score: float
    gates_status: dict[str, bool]
    issues_count: int


@dataclass
class ArticleState:
    """Complete state of the article being written."""
    
    # Identity
    article_id: str
    title: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Phase tracking
    current_phase: ArticlePhase = ArticlePhase.INITIALIZATION
    orchestrator_state: OrchestratorState = OrchestratorState.IDLE
    
    # Section states
    sections: dict[str, SectionState] = field(default_factory=dict)
    
    # Configuration
    target_journal: str = ""
    target_word_count: int = 8000
    language: str = "en"
    
    # Research cache
    research_cache: ResearchCache = field(default_factory=ResearchCache)
    
    # Quality history
    quality_snapshots: list[QualitySnapshot] = field(default_factory=list)
    
    # Agent activity log
    agent_calls: list[dict] = field(default_factory=list)
    
    # Error tracking
    errors: list[dict] = field(default_factory=list)
    warnings: list[dict] = field(default_factory=list)
    
    # Human review
    human_review_requests: list[dict] = field(default_factory=list)
    human_decisions: list[dict] = field(default_factory=list)
    
    # Checkpoints for rollback
    checkpoints: list[str] = field(default_factory=list)
    
    def update_modified(self) -> None:
        """Update last modified timestamp."""
        self.last_modified = datetime.now().isoformat()
    
    def log_agent_call(
        self, 
        agent_name: str, 
        action: str, 
        input_summary: str,
        output_summary: str,
        duration_ms: int
    ) -> None:
        """Log an agent call for observability."""
        self.agent_calls.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "input": input_summary,
            "output": output_summary,
            "duration_ms": duration_ms
        })
    
    def log_error(self, agent: str, error_type: str, message: str) -> None:
        """Log an error."""
        self.errors.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "type": error_type,
            "message": message
        })
    
    def request_human_review(self, reason: str, context: dict) -> None:
        """Request human review."""
        self.human_review_requests.append({
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "context": context,
            "resolved": False
        })
        self.orchestrator_state = OrchestratorState.WAITING_HUMAN
    
    def take_quality_snapshot(self) -> QualitySnapshot:
        """Take a snapshot of current quality metrics."""
        section_scores = {
            sid: state.current_score 
            for sid, state in self.sections.items()
        }
        
        overall = (
            sum(section_scores.values()) / len(section_scores) 
            if section_scores else 0
        )
        
        gates_status = {
            sid: state.gates_passed
            for sid, state in self.sections.items()
        }
        
        issues_count = sum(
            len(state.quality_issues)
            for state in self.sections.values()
        )
        
        iteration = max(
            (state.current_iteration for state in self.sections.values()),
            default=0
        )
        
        snapshot = QualitySnapshot(
            timestamp=datetime.now().isoformat(),
            iteration=iteration,
            section_scores=section_scores,
            overall_score=overall,
            gates_status=gates_status,
            issues_count=issues_count
        )
        
        self.quality_snapshots.append(snapshot)
        return snapshot
    
    def get_overall_progress(self) -> dict[str, Any]:
        """Get overall article progress."""
        approved = sum(
            1 for s in self.sections.values() 
            if s.status == SectionStatus.APPROVED
        )
        total = len(self.sections)
        
        return {
            "phase": self.current_phase.value,
            "state": self.orchestrator_state.value,
            "sections_approved": f"{approved}/{total}",
            "progress_pct": (approved / total * 100) if total > 0 else 0,
            "errors_count": len(self.errors),
            "pending_human_reviews": sum(
                1 for r in self.human_review_requests if not r.get("resolved")
            )
        }


class StateManager:
    """Manages article state with persistence and rollback."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.checkpoints_dir = self.data_dir / "checkpoints"
        self.states_dir = self.data_dir / "states"
        
        # Create directories
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.states_dir.mkdir(parents=True, exist_ok=True)
        
        self._current_state: Optional[ArticleState] = None
    
    @property
    def state(self) -> ArticleState:
        """Get current state."""
        if self._current_state is None:
            raise RuntimeError("No article state initialized")
        return self._current_state
    
    def create_new_article(
        self, 
        article_id: str, 
        title: str,
        target_journal: str = "",
        language: str = "en"
    ) -> ArticleState:
        """Create a new article state."""
        self._current_state = ArticleState(
            article_id=article_id,
            title=title,
            target_journal=target_journal,
            language=language
        )
        
        # Initialize sections from config
        from .sections_config import REVIEW_SECTIONS
        for section_id in REVIEW_SECTIONS:
            self._current_state.sections[section_id] = SectionState(
                section_id=section_id
            )
        
        # Save initial state
        self.save_state()
        
        return self._current_state
    
    def load_state(self, article_id: str) -> ArticleState:
        """Load article state from disk."""
        state_file = self.states_dir / f"{article_id}.json"
        
        if not state_file.exists():
            raise FileNotFoundError(f"No state found for article: {article_id}")
        
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self._current_state = self._dict_to_state(data)
        return self._current_state
    
    def save_state(self) -> str:
        """Save current state to disk."""
        if self._current_state is None:
            raise RuntimeError("No state to save")
        
        self._current_state.update_modified()
        
        state_file = self.states_dir / f"{self._current_state.article_id}.json"
        
        data = self._state_to_dict(self._current_state)
        
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(state_file)
    
    def create_checkpoint(self, name: Optional[str] = None) -> str:
        """Create a checkpoint for rollback."""
        if self._current_state is None:
            raise RuntimeError("No state to checkpoint")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_name = name or f"checkpoint_{timestamp}"
        
        checkpoint_file = self.checkpoints_dir / f"{self._current_state.article_id}_{checkpoint_name}.json"
        
        data = self._state_to_dict(self._current_state)
        
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self._current_state.checkpoints.append(checkpoint_name)
        
        return checkpoint_name
    
    def rollback_to_checkpoint(self, checkpoint_name: str) -> ArticleState:
        """Rollback to a previous checkpoint."""
        if self._current_state is None:
            raise RuntimeError("No state to rollback")
        
        checkpoint_file = self.checkpoints_dir / f"{self._current_state.article_id}_{checkpoint_name}.json"
        
        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_name}")
        
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self._current_state = self._dict_to_state(data)
        
        # Log rollback
        self._current_state.agent_calls.append({
            "timestamp": datetime.now().isoformat(),
            "agent": "state_manager",
            "action": "rollback",
            "input": checkpoint_name,
            "output": "success",
            "duration_ms": 0
        })
        
        return self._current_state
    
    def list_checkpoints(self) -> list[dict]:
        """List available checkpoints for current article."""
        if self._current_state is None:
            return []
        
        prefix = f"{self._current_state.article_id}_"
        checkpoints = []
        
        for f in self.checkpoints_dir.glob(f"{prefix}*.json"):
            name = f.stem.replace(prefix, "")
            stat = f.stat()
            checkpoints.append({
                "name": name,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "size_kb": stat.st_size / 1024
            })
        
        return sorted(checkpoints, key=lambda x: x["created"], reverse=True)
    
    def _state_to_dict(self, state: ArticleState) -> dict:
        """Convert state to serializable dict."""
        def serialize(obj):
            if isinstance(obj, Enum):
                return obj.value
            elif hasattr(obj, "__dict__"):
                return {k: serialize(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize(i) for i in obj]
            else:
                return obj
        
        return serialize(state)
    
    def _dict_to_state(self, data: dict) -> ArticleState:
        """Convert dict back to ArticleState."""
        # Restore enums
        data["current_phase"] = ArticlePhase(data["current_phase"])
        data["orchestrator_state"] = OrchestratorState(data["orchestrator_state"])
        
        # Restore sections
        sections = {}
        for sid, sdata in data.get("sections", {}).items():
            sdata["status"] = SectionStatus(sdata["status"])
            sections[sid] = SectionState(**sdata)
        data["sections"] = sections
        
        # Restore research cache
        cache_data = data.get("research_cache", {})
        data["research_cache"] = ResearchCache(**cache_data)
        
        # Restore quality snapshots
        snapshots = [
            QualitySnapshot(**s) 
            for s in data.get("quality_snapshots", [])
        ]
        data["quality_snapshots"] = snapshots
        
        return ArticleState(**data)
    
    def export_for_review(self, output_path: str) -> str:
        """Export state in human-readable format for review."""
        if self._current_state is None:
            raise RuntimeError("No state to export")
        
        lines = [
            f"# Article Review Export",
            f"",
            f"**Title:** {self._current_state.title}",
            f"**ID:** {self._current_state.article_id}",
            f"**Phase:** {self._current_state.current_phase.value}",
            f"**Last Modified:** {self._current_state.last_modified}",
            f"",
            f"## Progress",
            f""
        ]
        
        progress = self._current_state.get_overall_progress()
        lines.append(f"- Sections: {progress['sections_approved']}")
        lines.append(f"- Progress: {progress['progress_pct']:.1f}%")
        lines.append(f"- Errors: {progress['errors_count']}")
        lines.append(f"")
        
        lines.append(f"## Section Status")
        lines.append(f"")
        
        for sid, section in sorted(
            self._current_state.sections.items(),
            key=lambda x: x[1].current_iteration
        ):
            lines.append(f"### {sid}")
            lines.append(f"- Status: {section.status.value}")
            lines.append(f"- Score: {section.current_score}/100")
            lines.append(f"- Iteration: {section.current_iteration}")
            lines.append(f"- Words: {section.word_count}")
            lines.append(f"- Gates Passed: {section.gates_passed}")
            lines.append(f"")
        
        if self._current_state.errors:
            lines.append(f"## Errors")
            lines.append(f"")
            for err in self._current_state.errors[-10:]:
                lines.append(f"- [{err['agent']}] {err['type']}: {err['message']}")
            lines.append(f"")
        
        content = "\n".join(lines)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return output_path
