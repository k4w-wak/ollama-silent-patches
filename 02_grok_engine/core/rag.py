#!/usr/bin/env python3
"""
Grok RAG Module — Lokal Vector Database med Embeddings
Gemmer fund, recon-resultater, og viden til genbrug.
Bruger Ollama nomic-embed-text til embeddings + lokal cosine search.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict

try:
    from .config import OLLAMA_BASE_URL, GROK_HOME
except ImportError:
    from config import OLLAMA_BASE_URL, GROK_HOME

RAG_DIR = GROK_HOME / "rag"
RAG_INDEX_FILE = RAG_DIR / "index.json"
RAG_CHUNKS_FILE = RAG_DIR / "chunks.json"
RAG_EMBEDDINGS_FILE = RAG_DIR / "embeddings.npy"


@dataclass
class RAGChunk:
    """Et dokument-chunk med metadata"""
    id: str
    text: str
    source: str  # "vuln_report", "recon", "notion", "finding", "sop", "manual"
    target: str = ""  # domæne/IP hvis relevant
    severity: str = ""
    tags: List[str] = None
    timestamp: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "source": self.source,
            "target": self.target,
            "severity": self.severity,
            "tags": self.tags,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'RAGChunk':
        return cls(
            id=data.get("id", ""),
            text=data.get("text", ""),
            source=data.get("source", "manual"),
            target=data.get("target", ""),
            severity=data.get("severity", ""),
            tags=data.get("tags", []),
            timestamp=data.get("timestamp", ""),
            metadata=data.get("metadata", {}),
        )


class EmbeddingEngine:
    """Ollama embeddings via nomic-embed-text + cloud fallback"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or OLLAMA_BASE_URL
        self._cache: Dict[str, List[float]] = {}
    
    def embed(self, text: str, model: str = "nomic-embed-text") -> Optional[List[float]]:
        """Generate embedding for a single text string."""
        import requests as req
        
        # Cache check
        cache_key = f"{model}:{text[:200]}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        payload = {
            "model": model,
            "input": text.strip()[:8000],
            "keep_alive": "30m",
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = req.post(f"{self.base_url}/api/embed", json=payload, timeout=90)
                if response.status_code == 200:
                    data = response.json()
                    embeddings = data.get("embeddings", [[]])
                    if embeddings and isinstance(embeddings[0], list):
                        emb = embeddings[0]
                        self._cache[cache_key] = emb
                        return emb
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                continue
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(10 * (attempt + 1))
                    continue
                print(f"[RAG] Embedding timeout efter {max_retries} forsøg")
                return None
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                print(f"[RAG] Embedding fejl: {e}")
                return None
        return None
    
    def embed_batch(self, texts: List[str], model: str = "nomic-embed-text") -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts."""
        results = []
        for text in texts:
            emb = self.embed(text, model)
            results.append(emb)
            time.sleep(0.5)  # Rate limit — grok bruger ogsaa GPU'en
        return results


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Beregning af cosine similarity mellem to vektorer."""
    if not a or not b or len(a) != len(b):
        return 0.0
    
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)


class RAGStore:
    """
    Lokal Vector Database for Grok.
    
    Features:
    - Gem fund, recon-resultater, SOPs, Notion sider
    - Semantisk søgning via Ollama embeddings
    - Auto-index når nye chunks tilføjes
    - Genbrug viden fra tidligere missioner
    - Target-baseret filtrering
    """
    
    def __init__(self):
        self.chunks: List[RAGChunk] = []
        self.embeddings: Dict[str, List[float]] = {}  # chunk_id -> embedding
        self.embedder = EmbeddingEngine()
        self._load()
    
    def _load(self):
        """Indlæs eksisterende data fra disk."""
        RAG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Indlæs chunks
        if RAG_CHUNKS_FILE.exists():
            try:
                with open(RAG_CHUNKS_FILE, 'r', encoding='utf-8', errors='surrogatepass') as f:
                    data = json.load(f)
                    self.chunks = [RAGChunk.from_dict(c) for c in data]
            except Exception:
                self.chunks = []
        
        # Indlæs embeddings
        emb_file = RAG_DIR / "embeddings.json"
        if emb_file.exists():
            try:
                with open(emb_file, 'r', encoding='utf-8', errors='surrogatepass') as f:
                    self.embeddings = json.load(f)
            except Exception:
                self.embeddings = {}
    
    def _save(self):
        """Gem chunks og embeddings til disk."""
        RAG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Gem chunks
        with open(RAG_CHUNKS_FILE, 'w', encoding='utf-8', errors='surrogatepass') as f:
            json.dump([c.to_dict() for c in self.chunks], f, indent=2, ensure_ascii=True)
        
        # Gem embeddings
        emb_file = RAG_DIR / "embeddings.json"
        with open(emb_file, 'w', encoding='utf-8', errors='surrogatepass') as f:
            json.dump(self.embeddings, f)
    
    def add(
        self,
        text: str,
        source: str = "manual",
        target: str = "",
        severity: str = "",
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """
        Tilføj et dokument til RAG databasen.
        
        Args:
            text: Tekstindhold
            source: "vuln_report", "recon", "notion", "finding", "sop", "manual"
            target: Domæne eller IP hvis relevant
            severity: Severity niveau hvis finding
            tags: Tags for kategorisering
            metadata: Ekstra metadata
        
        Returns:
            Chunk ID
        """
        import hashlib
        chunk_id = hashlib.sha256(f"{text[:100]}:{time.time()}".encode()).hexdigest()[:16]
        
        chunk = RAGChunk(
            id=chunk_id,
            text=text,
            source=source,
            target=target,
            severity=severity,
            tags=tags or [],
            metadata=metadata or {},
        )
        
        # Generer embedding
        embedding = self.embedder.embed(text)
        if embedding:
            self.embeddings[chunk_id] = embedding
        
        self.chunks.append(chunk)
        self._save()
        
        return chunk_id
    
    def add_finding(
        self,
        name: str,
        severity: str,
        vuln_type: str,
        evidence: str,
        target: str = "",
        fp_check: str = "Needs Manual",
        reasoning: str = "",
    ) -> str:
        """
        Tilføj et fund i standard Finding-format.
        Matcher FP-filter og Finding output format fra config.
        """
        text = f"""## Finding: {name}
- Severity: {severity}
- Type: {vuln_type}
- Target: {target}
- Evidence: {evidence}
- FP Check: {fp_check}
- Reasoning: {reasoning}"""
        
        tags = [vuln_type, severity.lower()]
        if "xss" in vuln_type.lower():
            tags.append("injection")
        if "rce" in vuln_type.lower():
            tags.append("critical")
        
        return self.add(
            text=text,
            source="finding",
            target=target,
            severity=severity,
            tags=tags,
            metadata={
                "vuln_type": vuln_type,
                "fp_check": fp_check,
            },
        )
    
    def add_recon_result(
        self,
        target: str,
        phase: str,
        output: str,
        tools_used: List[str] = None,
    ) -> str:
        """Tilføj recon-resultat."""
        text = f"""## Recon: {target} — {phase}
{output}"""
        
        return self.add(
            text=text,
            source="recon",
            target=target,
            tags=tools_used or [phase],
            metadata={"phase": phase},
        )
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        source: str = None,
        target: str = None,
        severity: str = None,
        tags: List[str] = None,
        min_similarity: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Semantisk søgning i RAG databasen.
        
        Args:
            query: Søgeforespørgsel
            top_k: Antal resultater
            source: Filtrer efter kilde (vuln_report, recon, finding, etc.)
            target: Filtrer efter target domæne/IP
            severity: Filtrer efter severity
            tags: Filtrer efter tags
            min_similarity: Minimum cosine similarity threshold
        
        Returns:
            Liste af resultater med chunk, similarity score og metadata
        """
        query_embedding = self.embedder.embed(query)
        if not query_embedding:
            # Fallback til keyword search
            return self._keyword_search(query, top_k, source, target, severity, tags)
        
        results = []
        for chunk in self.chunks:
            # Filtrer metadata
            if source and chunk.source != source:
                continue
            if target and chunk.target != target:
                # Delvis match — subdomain etc.
                if target not in chunk.target and chunk.target not in target:
                    continue
            if severity and chunk.severity.lower() != severity.lower():
                continue
            if tags and not any(t in chunk.tags for t in tags):
                continue
            
            # Cosine similarity
            chunk_emb = self.embeddings.get(chunk.id)
            if chunk_emb:
                sim = cosine_similarity(query_embedding, chunk_emb)
            else:
                # Ingen embedding — brug keyword fallback
                sim = self._text_similarity(query, chunk.text)
            
            if sim >= min_similarity:
                results.append({
                    "chunk": chunk.to_dict(),
                    "similarity": round(sim, 4),
                    "text": chunk.text,
                    "source": chunk.source,
                    "target": chunk.target,
                    "severity": chunk.severity,
                    "tags": chunk.tags,
                })
        
        # Sorter efter similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def _keyword_search(
        self,
        query: str,
        top_k: int = 5,
        source: str = None,
        target: str = None,
        severity: str = None,
        tags: List[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fallback keyword-søgning når embeddings ikke er tilgængelige."""
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for chunk in self.chunks:
            if source and chunk.source != source:
                continue
            if target and target not in chunk.target:
                continue
            if severity and chunk.severity.lower() != severity.lower():
                continue
            if tags and not any(t in chunk.tags for t in tags):
                continue
            
            # TF score
            text_lower = chunk.text.lower()
            words = set(text_lower.split())
            overlap = query_words & words
            score = len(overlap) / max(len(query_words), 1)
            
            if score > 0.1:
                results.append({
                    "chunk": chunk.to_dict(),
                    "similarity": round(score, 4),
                    "text": chunk.text,
                    "source": chunk.source,
                    "target": chunk.target,
                    "severity": chunk.severity,
                    "tags": chunk.tags,
                })
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def _text_similarity(self, query: str, text: str) -> float:
        """Simpel tekst-similaritet som fallback."""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        if not query_words:
            return 0.0
        overlap = query_words & text_words
        return len(overlap) / len(query_words)
    
    def find_similar_targets(self, target: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Find tidligere missioner for lignende targets."""
        return self.search(
            query=f"recon vulnerability finding {target}",
            top_k=top_k,
            source=None,  # Søg i alt
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistik over RAG databasen."""
        sources = {}
        severities = {}
        targets = set()
        
        for chunk in self.chunks:
            sources[chunk.source] = sources.get(chunk.source, 0) + 1
            if chunk.severity:
                severities[chunk.severity] = severities.get(chunk.severity, 0) + 1
            if chunk.target:
                targets.add(chunk.target)
        
        return {
            "total_chunks": len(self.chunks),
            "total_embeddings": len(self.embeddings),
            "sources": sources,
            "severities": severities,
            "unique_targets": len(targets),
            "targets": sorted(targets)[:20],
        }
    
    def clear(self, source: str = None, target: str = None):
        """Slet chunks. Valgfrit filter."""
        if source:
            self.chunks = [c for c in self.chunks if c.source != source]
        elif target:
            self.chunks = [c for c in self.chunks if c.target != target]
        else:
            self.chunks = []
            self.embeddings = {}
        self._save()
    
    def index_all(self, batch_size: int = 3):
        """Regenerer embeddings for alle chunks der mangler.
        Bruger keep_alive=30m for at holde modellen i hukommelsen.
        Kører i baggrund — tjek /tmp/rag_index.log for progress.
        """
        missing = [c for c in self.chunks if c.id not in self.embeddings]
        if not missing:
            return len(self.chunks)
        
        print(f"[RAG] Generer embeddings for {len(missing)} chunks (batch={batch_size})...")
        success = 0
        failed = 0
        for i in range(0, len(missing), batch_size):
            batch = missing[i:i+batch_size]
            for chunk in batch:
                try:
                    emb = self.embedder.embed(chunk.text)
                    if emb:
                        self.embeddings[chunk.id] = emb
                        success += 1
                    else:
                        failed += 1
                        time.sleep(1)
                except Exception:
                    failed += 1
                    time.sleep(2)
            # Gem efter hver batch
            self._save()
            done = min(i + batch_size, len(missing))
            print(f"[RAG] {done}/{len(missing)} done (OK={success}, FAIL={failed})")
        
        print(f"[RAG] Færdig! {success} indexed, {failed} failed, {len(self.chunks)} total")
        return len(self.chunks)


# ── Tool funktioner til integration med tools.py ──

def rag_add_tool(data: str) -> str:
    """Add document to RAG knowledge base. Input: text or JSON with text, source, target, tags."""
    import json
    
    # Prøv JSON parse
    try:
        parsed = json.loads(data)
        text = parsed.get("text", data)
        source = parsed.get("source", "manual")
        target = parsed.get("target", "")
        severity = parsed.get("severity", "")
        tags = parsed.get("tags", [])
        metadata = parsed.get("metadata", {})
    except (json.JSONDecodeError, TypeError):
        text = data
        source = "manual"
        target = ""
        severity = ""
        tags = []
        metadata = {}
    
    store = RAGStore()
    chunk_id = store.add(text=text, source=source, target=target, severity=severity, tags=tags, metadata=metadata)
    stats = store.get_stats()
    return json.dumps({
        "status": "added",
        "chunk_id": chunk_id,
        "total_chunks": stats["total_chunks"],
        "total_embeddings": stats["total_embeddings"],
    }, indent=2, ensure_ascii=True)


def rag_search_tool(query: str) -> str:
    """Search RAG knowledge base for similar past findings, recon results, and knowledge. Input: search query or JSON with query, top_k, source, target."""
    import json
    
    # Prøv JSON parse for avancerede parametre
    try:
        parsed = json.loads(query)
        q = parsed.get("query", query)
        top_k = parsed.get("top_k", 5)
        source = parsed.get("source")
        target = parsed.get("target")
        severity = parsed.get("severity")
        tags = parsed.get("tags")
    except (json.JSONDecodeError, TypeError):
        q = query
        top_k = 5
        source = None
        target = None
        severity = None
        tags = None
    
    store = RAGStore()
    results = store.search(query=q, top_k=top_k, source=source, target=target, severity=severity, tags=tags)
    
    if not results:
        return f"[RAG] Ingen resultater for '{q}'. Prøv at tilføje data med rag_add først."
    
    lines = [f"[RAG] {len(results)} resultater for '{q}':\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"--- Resultat {i} (similaritet: {r['similarity']:.2%}) ---")
        lines.append(f"Kilde: {r['source']} | Target: {r.get('target', 'N/A')} | Severity: {r.get('severity', 'N/A')}")
        lines.append(r['text'][:500])
        lines.append("")
    
    return "\n".join(lines)


def rag_find_similar_tool(target: str) -> str:
    """Find similar past targets and their findings in RAG. Input: domain or IP."""
    store = RAGStore()
    results = store.find_similar_targets(target)
    
    if not results:
        return f"[RAG] Ingen lignende targets for '{target}'."
    
    lines = [f"[RAG] Lignende targets for '{target}':\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"--- Lignende {i} (similaritet: {r['similarity']:.2%}) ---")
        lines.append(f"Target: {r.get('target', 'N/A')}")
        lines.append(r['text'][:500])
        lines.append("")
    
    return "\n".join(lines)


def rag_stats_tool(query: str = "") -> str:
    """Show RAG knowledge base statistics. Input: empty."""
    import json
    store = RAGStore()
    stats = store.get_stats()
    return json.dumps(stats, indent=2, ensure_ascii=True)


def rag_index_tool(query: str = "") -> str:
    """Re-index all RAG chunks that are missing embeddings. Input: empty."""
    store = RAGStore()
    total = store.index_all()
    return f"[RAG] Indexering komplet. Total chunks: {total}, Embeddings: {len(store.embeddings)}"


def rag_clear_tool(data: str) -> str:
    """Clear RAG knowledge base. Input: 'all', 'source:recon', or 'target:example.com'."""
    store = RAGStore()
    if data.strip().lower() == "all":
        store.clear()
        return "[RAG] Hele databasen slettet"
    elif data.strip().startswith("source:"):
        source = data.strip().split(":", 1)[1]
        store.clear(source=source)
        return f"[RAG] Slettet alle chunks med source='{source}'"
    elif data.strip().startswith("target:"):
        target = data.strip().split(":", 1)[1]
        store.clear(target=target)
        return f"[RAG] Slettet alle chunks med target='{target}'"
    else:
        return "[RAG] Brug: 'all', 'source:recon', eller 'target:example.com'"
