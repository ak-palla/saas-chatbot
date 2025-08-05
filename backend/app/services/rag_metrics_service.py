"""
RAG Performance Metrics Service
Collects and logs comprehensive metrics for RAG system performance monitoring
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)

# Create dedicated metrics logger
metrics_logger = logging.getLogger("rag_metrics")
metrics_logger.setLevel(logging.INFO)

# Create file handler for metrics if not exists
if not metrics_logger.handlers:
    metrics_handler = logging.FileHandler('rag_metrics.log')
    metrics_formatter = logging.Formatter(
        '%(asctime)s - RAG_METRICS - %(levelname)s - %(message)s'
    )
    metrics_handler.setFormatter(metrics_formatter)
    metrics_logger.addHandler(metrics_handler)


@dataclass
class RetrievalMetrics:
    """Metrics for document retrieval operations"""
    query: str
    chatbot_id: str
    retrieval_method: str  # 'vector', 'hybrid', 'reranked'
    start_time: float
    end_time: float
    duration_ms: float
    contexts_retrieved: int
    contexts_used: int
    similarity_scores: List[float]
    avg_similarity: float
    max_similarity: float
    min_similarity: float
    embedding_time_ms: float
    search_time_ms: float
    reranking_time_ms: Optional[float] = None
    hybrid_scores: Optional[List[float]] = None
    query_length: int = 0
    query_complexity: str = "moderate"
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class ResponseMetrics:
    """Metrics for response generation"""
    query: str
    chatbot_id: str
    response_length: int
    contexts_count: int
    generation_time_ms: float
    model_used: str
    rag_enabled: bool
    voice_optimized: bool = False
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class SessionMetrics:
    """Aggregated metrics for a conversation session"""
    session_id: str
    chatbot_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_queries: int = 0
    successful_retrievals: int = 0
    avg_retrieval_time_ms: float = 0.0
    avg_response_time_ms: float = 0.0
    avg_contexts_per_query: float = 0.0
    avg_similarity_score: float = 0.0
    retrieval_methods_used: Dict[str, int] = None
    voice_queries: int = 0
    text_queries: int = 0


class RAGMetricsService:
    """Service for collecting and logging RAG performance metrics"""
    
    def __init__(self):
        self.lock = threading.Lock()
        
        # In-memory storage for recent metrics (last 1000 operations)
        self.recent_retrievals = deque(maxlen=1000)
        self.recent_responses = deque(maxlen=1000)
        self.active_sessions = {}
        
        # Aggregated statistics
        self.daily_stats = defaultdict(lambda: {
            'queries': 0,
            'successful_retrievals': 0,
            'avg_retrieval_time': 0.0,
            'avg_similarity': 0.0,
            'methods_used': defaultdict(int)
        })
        
        # Performance thresholds for alerting
        self.thresholds = {
            'retrieval_time_ms': 2000,  # Alert if retrieval takes > 2s
            'response_time_ms': 5000,   # Alert if response takes > 5s
            'min_similarity': 0.3,      # Alert if similarity too low
            'min_contexts': 1           # Alert if no contexts retrieved
        }
    
    def start_retrieval_tracking(
        self,
        query: str,
        chatbot_id: str,
        method: str = "vector"
    ) -> str:
        """Start tracking a retrieval operation"""
        tracking_id = f"{chatbot_id}_{int(time.time() * 1000)}"
        
        with self.lock:
            # Store start time and basic info
            self.active_retrievals = getattr(self, 'active_retrievals', {})
            self.active_retrievals[tracking_id] = {
                'query': query,
                'chatbot_id': chatbot_id,
                'method': method,
                'start_time': time.time(),
                'embedding_start': None,
                'search_start': None,
                'reranking_start': None
            }
        
        return tracking_id
    
    def log_embedding_phase(self, tracking_id: str):
        """Log start of embedding generation phase"""
        with self.lock:
            if hasattr(self, 'active_retrievals') and tracking_id in self.active_retrievals:
                self.active_retrievals[tracking_id]['embedding_start'] = time.time()
    
    def log_search_phase(self, tracking_id: str):
        """Log start of search phase"""
        with self.lock:
            if hasattr(self, 'active_retrievals') and tracking_id in self.active_retrievals:
                self.active_retrievals[tracking_id]['search_start'] = time.time()
    
    def log_reranking_phase(self, tracking_id: str):
        """Log start of reranking phase"""
        with self.lock:
            if hasattr(self, 'active_retrievals') and tracking_id in self.active_retrievals:
                self.active_retrievals[tracking_id]['reranking_start'] = time.time()
    
    def complete_retrieval_tracking(
        self,
        tracking_id: str,
        contexts: List[str],
        metadata: List[Dict[str, Any]],
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Complete retrieval tracking and log metrics"""
        
        with self.lock:
            if not hasattr(self, 'active_retrievals') or tracking_id not in self.active_retrievals:
                return
            
            tracking_data = self.active_retrievals.pop(tracking_id)
            end_time = time.time()
            
            # Calculate timing metrics
            total_duration = (end_time - tracking_data['start_time']) * 1000
            
            embedding_time = 0.0
            if tracking_data.get('embedding_start') is not None:
                search_start = tracking_data.get('search_start')
                if search_start is not None:
                    embedding_time = (search_start - tracking_data['embedding_start']) * 1000
                else:
                    embedding_time = (end_time - tracking_data['embedding_start']) * 1000
            
            search_time = 0.0
            if tracking_data.get('search_start') is not None:
                reranking_start = tracking_data.get('reranking_start')
                if reranking_start is not None:
                    search_time = (reranking_start - tracking_data['search_start']) * 1000
                else:
                    search_time = (end_time - tracking_data['search_start']) * 1000
            
            reranking_time = 0.0
            if tracking_data.get('reranking_start') is not None:
                reranking_time = (end_time - tracking_data['reranking_start']) * 1000
            
            # Extract similarity scores
            similarity_scores = []
            hybrid_scores = []
            
            for meta in metadata:
                if 'similarity' in meta and meta['similarity'] is not None:
                    similarity_scores.append(meta['similarity'])
                if 'hybrid_score' in meta and meta['hybrid_score'] is not None:
                    hybrid_scores.append(meta['hybrid_score'])
            
            # Calculate statistics (filter out None values)
            valid_similarity_scores = [score for score in similarity_scores if score is not None]
            avg_similarity = sum(valid_similarity_scores) / len(valid_similarity_scores) if valid_similarity_scores else 0.0
            max_similarity = max(valid_similarity_scores) if valid_similarity_scores else 0.0
            min_similarity = min(valid_similarity_scores) if valid_similarity_scores else 0.0
            
            # Assess query complexity
            query_complexity = self._assess_query_complexity(tracking_data['query'])
            
            # Create metrics object
            metrics = RetrievalMetrics(
                query=tracking_data['query'],
                chatbot_id=tracking_data['chatbot_id'],
                retrieval_method=tracking_data['method'],
                start_time=tracking_data['start_time'],
                end_time=end_time,
                duration_ms=total_duration,
                contexts_retrieved=len(contexts),
                contexts_used=len([c for c in contexts if c.strip()]),
                similarity_scores=similarity_scores,
                avg_similarity=avg_similarity,
                max_similarity=max_similarity,
                min_similarity=min_similarity,
                embedding_time_ms=embedding_time,
                search_time_ms=search_time,
                reranking_time_ms=reranking_time,
                hybrid_scores=hybrid_scores if hybrid_scores else None,
                query_length=len(tracking_data['query']),
                query_complexity=query_complexity,
                success=success,
                error_message=error_message
            )
            
            # Store and log metrics
            self.recent_retrievals.append(metrics)
            self._log_retrieval_metrics(metrics)
            self._update_aggregated_stats(metrics)
            self._check_performance_alerts(metrics)
    
    def log_response_metrics(
        self,
        query: str,
        chatbot_id: str,
        response: str,
        contexts_count: int,
        generation_time_ms: float,
        model_used: str,
        rag_enabled: bool = True,
        voice_optimized: bool = False,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log response generation metrics"""
        
        metrics = ResponseMetrics(
            query=query,
            chatbot_id=chatbot_id,
            response_length=len(response),
            contexts_count=contexts_count,
            generation_time_ms=generation_time_ms,
            model_used=model_used,
            rag_enabled=rag_enabled,
            voice_optimized=voice_optimized,
            success=success,
            error_message=error_message
        )
        
        with self.lock:
            self.recent_responses.append(metrics)
        
        self._log_response_metrics(metrics)
    
    def start_session_tracking(self, session_id: str, chatbot_id: str):
        """Start tracking a conversation session"""
        with self.lock:
            self.active_sessions[session_id] = SessionMetrics(
                session_id=session_id,
                chatbot_id=chatbot_id,
                start_time=datetime.utcnow(),
                retrieval_methods_used=defaultdict(int)
            )
    
    def update_session_metrics(
        self,
        session_id: str,
        retrieval_time_ms: float,
        response_time_ms: float,
        contexts_count: int,
        similarity_score: float,
        method: str,
        is_voice: bool = False
    ):
        """Update session metrics with new query data"""
        with self.lock:
            if session_id not in self.active_sessions:
                return
            
            session = self.active_sessions[session_id]
            session.total_queries += 1
            session.successful_retrievals += 1
            
            # Update averages
            total = session.total_queries
            session.avg_retrieval_time_ms = (
                (session.avg_retrieval_time_ms * (total - 1) + retrieval_time_ms) / total
            )
            session.avg_response_time_ms = (
                (session.avg_response_time_ms * (total - 1) + response_time_ms) / total
            )
            session.avg_contexts_per_query = (
                (session.avg_contexts_per_query * (total - 1) + contexts_count) / total
            )
            session.avg_similarity_score = (
                (session.avg_similarity_score * (total - 1) + similarity_score) / total
            )
            
            # Update method counts
            session.retrieval_methods_used[method] += 1
            
            # Update query type counts
            if is_voice:
                session.voice_queries += 1
            else:
                session.text_queries += 1
    
    def end_session_tracking(self, session_id: str):
        """End session tracking and log final metrics"""
        with self.lock:
            if session_id not in self.active_sessions:
                return
            
            session = self.active_sessions.pop(session_id)
            session.end_time = datetime.utcnow()
        
        self._log_session_metrics(session)
    
    def _assess_query_complexity(self, query: str) -> str:
        """Assess query complexity for metrics"""
        words = query.split()
        
        if len(words) <= 5:
            return "simple"
        elif len(words) <= 12:
            return "moderate"
        else:
            return "complex"
    
    def _log_retrieval_metrics(self, metrics: RetrievalMetrics):
        """Log detailed retrieval metrics"""
        
        log_data = {
            "event_type": "RETRIEVAL_COMPLETED",
            "timestamp": datetime.utcnow().isoformat(),
            "query_hash": hash(metrics.query) % 10000,  # Hash for privacy
            "query_length": metrics.query_length,
            "query_complexity": metrics.query_complexity,
            "chatbot_id": metrics.chatbot_id,
            "method": metrics.retrieval_method,
            "duration_ms": round(metrics.duration_ms, 2),
            "embedding_time_ms": round(metrics.embedding_time_ms, 2),
            "search_time_ms": round(metrics.search_time_ms, 2),
            "reranking_time_ms": round(metrics.reranking_time_ms, 2) if metrics.reranking_time_ms else None,
            "contexts_retrieved": metrics.contexts_retrieved,
            "contexts_used": metrics.contexts_used,
            "avg_similarity": round(metrics.avg_similarity, 4),
            "max_similarity": round(metrics.max_similarity, 4),
            "min_similarity": round(metrics.min_similarity, 4),
            "success": metrics.success,
            "error": metrics.error_message
        }
        
        metrics_logger.info(f"RETRIEVAL_METRICS: {json.dumps(log_data)}")
        
        # Log performance breakdown
        if metrics.duration_ms > 0:
            breakdown = {
                "embedding_pct": round((metrics.embedding_time_ms / metrics.duration_ms) * 100, 1),
                "search_pct": round((metrics.search_time_ms / metrics.duration_ms) * 100, 1),
                "reranking_pct": round((metrics.reranking_time_ms / metrics.duration_ms) * 100, 1) if metrics.reranking_time_ms and metrics.duration_ms > 0 else 0
            }
            metrics_logger.info(f"RETRIEVAL_BREAKDOWN: {json.dumps(breakdown)}")
    
    def _log_response_metrics(self, metrics: ResponseMetrics):
        """Log response generation metrics"""
        
        log_data = {
            "event_type": "RESPONSE_GENERATED",
            "timestamp": datetime.utcnow().isoformat(),
            "query_hash": hash(metrics.query) % 10000,
            "chatbot_id": metrics.chatbot_id,
            "response_length": metrics.response_length,
            "contexts_count": metrics.contexts_count,
            "generation_time_ms": round(metrics.generation_time_ms, 2),
            "model_used": metrics.model_used,
            "rag_enabled": metrics.rag_enabled,
            "voice_optimized": metrics.voice_optimized,
            "success": metrics.success,
            "error": metrics.error_message
        }
        
        metrics_logger.info(f"RESPONSE_METRICS: {json.dumps(log_data)}")
    
    def _log_session_metrics(self, session: SessionMetrics):
        """Log session summary metrics"""
        
        duration_minutes = 0
        if session.end_time:
            duration_minutes = (session.end_time - session.start_time).total_seconds() / 60
        
        log_data = {
            "event_type": "SESSION_COMPLETED", 
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session.session_id,
            "chatbot_id": session.chatbot_id,
            "duration_minutes": round(duration_minutes, 2),
            "total_queries": session.total_queries,
            "successful_retrievals": session.successful_retrievals,
            "success_rate": round(session.successful_retrievals / max(session.total_queries, 1), 4),
            "avg_retrieval_time_ms": round(session.avg_retrieval_time_ms, 2),
            "avg_response_time_ms": round(session.avg_response_time_ms, 2),
            "avg_contexts_per_query": round(session.avg_contexts_per_query, 2),
            "avg_similarity_score": round(session.avg_similarity_score, 4),
            "methods_used": dict(session.retrieval_methods_used),
            "voice_queries": session.voice_queries,
            "text_queries": session.text_queries,
            "voice_percentage": round((session.voice_queries / max(session.total_queries, 1)) * 100, 1)
        }
        
        metrics_logger.info(f"SESSION_METRICS: {json.dumps(log_data)}")
    
    def _update_aggregated_stats(self, metrics: RetrievalMetrics):
        """Update daily aggregated statistics"""
        today = datetime.utcnow().date().isoformat()
        
        stats = self.daily_stats[today]
        stats['queries'] += 1
        
        if metrics.success:
            stats['successful_retrievals'] += 1
            
            # Update running averages
            total_successful = stats['successful_retrievals']
            stats['avg_retrieval_time'] = (
                (stats['avg_retrieval_time'] * (total_successful - 1) + metrics.duration_ms) / total_successful
            )
            stats['avg_similarity'] = (
                (stats['avg_similarity'] * (total_successful - 1) + metrics.avg_similarity) / total_successful
            )
        
        stats['methods_used'][metrics.retrieval_method] += 1
    
    def _check_performance_alerts(self, metrics: RetrievalMetrics):
        """Check for performance issues and log alerts"""
        
        alerts = []
        
        if metrics.duration_ms > self.thresholds['retrieval_time_ms']:
            alerts.append(f"SLOW_RETRIEVAL: {metrics.duration_ms}ms > {self.thresholds['retrieval_time_ms']}ms")
        
        if metrics.avg_similarity < self.thresholds['min_similarity']:
            alerts.append(f"LOW_SIMILARITY: {metrics.avg_similarity} < {self.thresholds['min_similarity']}")
        
        if metrics.contexts_retrieved < self.thresholds['min_contexts']:
            alerts.append(f"NO_CONTEXTS: {metrics.contexts_retrieved} contexts retrieved")
        
        if not metrics.success:
            alerts.append(f"RETRIEVAL_FAILURE: {metrics.error_message}")
        
        for alert in alerts:
            alert_data = {
                "event_type": "PERFORMANCE_ALERT",
                "timestamp": datetime.utcnow().isoformat(),
                "alert": alert,
                "chatbot_id": metrics.chatbot_id,
                "query_hash": hash(metrics.query) % 10000,
                "method": metrics.retrieval_method
            }
            
            metrics_logger.warning(f"RAG_ALERT: {json.dumps(alert_data)}")
    
    def log_daily_summary(self):
        """Log daily performance summary"""
        today = datetime.utcnow().date().isoformat()
        
        if today in self.daily_stats:
            stats = self.daily_stats[today]
            
            summary = {
                "event_type": "DAILY_SUMMARY",
                "date": today,
                "timestamp": datetime.utcnow().isoformat(),
                "total_queries": stats['queries'],
                "successful_retrievals": stats['successful_retrievals'],
                "success_rate": round(stats['successful_retrievals'] / max(stats['queries'], 1), 4),
                "avg_retrieval_time_ms": round(stats['avg_retrieval_time'], 2),
                "avg_similarity": round(stats['avg_similarity'], 4),
                "methods_used": dict(stats['methods_used'])
            }
            
            metrics_logger.info(f"DAILY_SUMMARY: {json.dumps(summary)}")
    
    def get_recent_performance_stats(self, limit: int = 100) -> Dict[str, Any]:
        """Get recent performance statistics for monitoring"""
        with self.lock:
            recent_retrievals = list(self.recent_retrievals)[-limit:]
            recent_responses = list(self.recent_responses)[-limit:]
        
        if not recent_retrievals:
            return {"message": "No recent retrieval data available"}
        
        # Calculate aggregate statistics
        successful_retrievals = [r for r in recent_retrievals if r.success]
        
        avg_retrieval_time = sum(r.duration_ms for r in successful_retrievals) / len(successful_retrievals) if successful_retrievals else 0
        avg_similarity = sum(r.avg_similarity for r in successful_retrievals) / len(successful_retrievals) if successful_retrievals else 0
        avg_contexts = sum(r.contexts_retrieved for r in successful_retrievals) / len(successful_retrievals) if successful_retrievals else 0
        
        method_counts = defaultdict(int)
        for r in recent_retrievals:
            method_counts[r.retrieval_method] += 1
        
        return {
            "recent_queries": len(recent_retrievals),
            "success_rate": len(successful_retrievals) / len(recent_retrievals),
            "avg_retrieval_time_ms": round(avg_retrieval_time, 2),
            "avg_similarity_score": round(avg_similarity, 4),
            "avg_contexts_retrieved": round(avg_contexts, 2),
            "methods_distribution": dict(method_counts),
            "active_sessions": len(self.active_sessions)
        }


# Global instance
rag_metrics_service = RAGMetricsService()