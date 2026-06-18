#!/usr/bin/env python3
"""
Grok Memory System — ALDRIG glem
Auto-save efter HVER besked. Persistent langtidshukommelse.
AUTO-LOAD ved startup — læser ALTID sidste session.
"""

import json
import os
import hashlib
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path

try:
    from .config import FACTS_FILE, MEMORY_DIR, GROK_HOME, MEMORY_SHORT_TERM_SIZE, MEMORY_AUTO_SAVE
except ImportError:
    from config import FACTS_FILE, MEMORY_DIR, GROK_HOME, MEMORY_SHORT_TERM_SIZE, MEMORY_AUTO_SAVE


@dataclass
class Message:
    """En besked i samtalen"""
    role: str
    content: str
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content, "timestamp": self.timestamp}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", ""),
            timestamp=data.get("timestamp", "")
        )


class ShortTermMemory:
    """
    Korttidshukommelse — samtale kontekst.
    Auto-trim når den bliver for lang.
    """
    
    def __init__(self, max_messages: int = None):
        self.max_messages = max_messages or MEMORY_SHORT_TERM_SIZE
        self.messages: List[Message] = []
    
    def add(self, role: str, content: str) -> Message:
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        
        # Auto-trim — behold system prompt
        while len(self.messages) > self.max_messages:
            if self.messages[0].role == "system":
                # Slet den anden (behold system)
                if len(self.messages) > 1:
                    self.messages.pop(1)
                else:
                    break
            else:
                self.messages.pop(0)
        
        return msg
    
    def get_chat_messages(self) -> List[dict]:
        """Format til LLM chat"""
        return [{"role": m.role, "content": m.content} for m in self.messages]
    
    def get_context_string(self) -> str:
        """Som tekst til prompt"""
        lines = []
        for msg in self.messages:
            lines.append(f"[{msg.role.upper()}]: {msg.content[:200]}")
        return "\n".join(lines)
    
    def clear(self):
        """Ryd korttidshukommelse (ikke system prompt)"""
        system_msgs = [m for m in self.messages if m.role == "system"]
        self.messages = system_msgs
    
    def count(self) -> int:
        return len(self.messages)


class LongTermMemory:
    """
    Langtidshukommelse — facts der overlever genstart.
    Auto-save efter ÆNDRING.
    """
    
    def __init__(self, facts_file: Path = None):
        self.facts_file = facts_file or FACTS_FILE
        self.facts: Dict[str, Dict[str, Any]] = {}
        self.load()
    
    def load(self):
        """Indlæs facts fra disk"""
        if self.facts_file.exists():
            try:
                with open(self.facts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.facts = data.get("facts", {})
            except Exception:
                self.facts = {}
    
    def save(self):
        """Gem facts til disk"""
        self.facts_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.facts_file, 'w', encoding='utf-8') as f:
            json.dump({"facts": self.facts}, f, indent=2, ensure_ascii=False)
    
    def set_fact(self, key: str, value: str, metadata: dict = None):
        """Gem et fact"""
        self.facts[key] = {
            "value": value,
            "updated": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.save()  # AUTO-SAVE
    
    def get_fact(self, key: str) -> Optional[str]:
        """Hent et fact"""
        if key in self.facts:
            return self.facts[key].get("value")
        return None
    
    def search(self, query: str) -> List[str]:
        """Søg i facts"""
        query = query.lower()
        results = []
        for key, data in self.facts.items():
            val = data.get("value", "")
            if query in key.lower() or query in val.lower():
                results.append(f"{key}: {val}")
        return results
    
    def delete_fact(self, key: str) -> bool:
        """Slet et fact"""
        if key in self.facts:
            del self.facts[key]
            self.save()
            return True
        return False
    
    def get_all_facts(self) -> Dict[str, str]:
        """Hent alle facts som simpel dict"""
        return {k: v.get("value", "") for k, v in self.facts.items()}
    
    def get_context_for_prompt(self) -> str:
        """Facts formateret til system prompt"""
        if not self.facts:
            return ""
        
        lines = ["HUSK — Fakta om brugeren:"]
        for key, data in list(self.facts.items())[:20]:
            lines.append(f"- {key}: {data.get('value', '')}")
        return "\n".join(lines)
    
    def count(self) -> int:
        return len(self.facts)


class MemoryManager:
    """
    Samlet hukommelse — kort + langtid.
    Auto-save efter HVER operation.
    AUTO-LOAD ved startup — læser ALTID sidste session.
    """
    
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
    
    def add_message(self, role: str, content: str):
        """Tilføj besked til korttidshukommelsen"""
        return self.short_term.add(role, content)
    
    def add_system(self, content: str):
        """Tilføj system prompt"""
        return self.short_term.add("system", content)
    
    def remember(self, key: str, value: str, metadata: dict = None):
        """Gem i langtidshukommelsen (auto-saves)"""
        self.long_term.set_fact(key, value, metadata)
    
    def recall(self, key: str) -> Optional[str]:
        """Hent fra langtidshukommelsen"""
        return self.long_term.get_fact(key)
    
    def search_memory(self, query: str) -> List[str]:
        """Søg i langtidshukommelsen"""
        return self.long_term.search(query)
    
    def get_chat_messages(self) -> List[dict]:
        """Korttidshukommelse formateret til LLM"""
        return self.short_term.get_chat_messages()
    
    def get_full_system_prompt(self, base_prompt: str) -> str:
        """
        Byg fuld system prompt med langtidshukommelse.
        Inkluderer alle facts der er relevante.
        """
        facts = self.long_term.get_context_for_prompt()
        if facts:
            return f"{base_prompt}\n\n{facts}"
        return base_prompt
    
    def clear_conversation(self):
        """Ryd korttidshukommelse, behold system + langtid"""
        self.short_term.clear()
    
    def load_last_session(self, n_messages: int = 10) -> Optional[str]:
        """
        Load sidste session fra disk og inject de sidste N beskeder
        i korttidshukommelsen. Returnerer session_id eller None.
        """
        if not MEMORY_DIR.exists():
            return None
        
        sessions = sorted(MEMORY_DIR.glob("session_*.json"), reverse=True)
        if not sessions:
            return None
        
        # Load nyeste session
        session_file = sessions[0]
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
        
        messages = data.get("messages", [])
        if not messages:
            return None
        
        # Tag kun de sidste N beskeder (spring system prompts over)
        user_msgs = [m for m in messages if m.get("role") in ("user", "assistant")]
        recent = user_msgs[-n_messages:]
        
        for msg in recent:
            self.short_term.add(
                msg.get("role", "user"),
                msg.get("content", "")
            )
        
        # FIX: Sæt _current_session_id til den loadede session
        # så save_session() overskriver SAMME fil i stedet for at oprette ny
        self._current_session_id = data.get("session_id", session_file.stem.replace("session_", ""))
        
        return data.get("session_id", session_file.stem)
    
    def get_recent_messages(self, n: int = 10) -> List[dict]:
        """
        Hent de sidste N beskeder fra nyeste session fil.
        Bruges til at vise brugeren hvad der skete sidst.
        """
        if not MEMORY_DIR.exists():
            return []
        
        sessions = sorted(MEMORY_DIR.glob("session_*.json"), reverse=True)
        if not sessions:
            return []
        
        try:
            with open(sessions[0], 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
        
        messages = data.get("messages", [])
        user_msgs = [m for m in messages if m.get("role") in ("user", "assistant")]
        return user_msgs[-n:]
    
    # Fast session ID — overskriver SAMME fil, ikke opretter 1269 nye
    _current_session_id: str = None
    
    def save_session(self, session_id: str = None):
        """Gem hele session til disk — bruger FAST session ID så samme fil overskrives"""
        if session_id is None:
            if self._current_session_id is None:
                self._current_session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            session_id = self._current_session_id
        else:
            self._current_session_id = session_id
        session_file = MEMORY_DIR / f"session_{session_id}.json"
        
        data = {
            "session_id": session_id,
            "saved_at": datetime.now().isoformat(),
            "messages": [m.to_dict() for m in self.short_term.messages],
            "facts": self.long_term.get_all_facts()
        }
        
        session_file.parent.mkdir(parents=True, exist_ok=True)
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(session_file)
    
    def get_status(self) -> Dict[str, Any]:
        """Status for hukommelsen"""
        return {
            "short_term_count": self.short_term.count(),
            "long_term_count": self.long_term.count(),
            "auto_save": MEMORY_AUTO_SAVE,
        }