"""
MelusAI - Continuous Learning System
Vector DB Memory, Quality Scoring, Feedback Analysis, Prompt Optimization
"""
import os
import json
import uuid
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)

# ============= VECTOR DB MEMORY =============

class VectorMemory:
    """
    Persistent vector memory using ChromaDB.
    Stores: successful prompts, generated code, user feedback, agent performance.
    """
    
    def __init__(self, persist_dir: str = "/app/data/chromadb"):
        self.persist_dir = persist_dir
        self._client = None
        self._collections = {}
        
    def _get_client(self):
        """Lazy initialization of ChromaDB client"""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings
                
                os.makedirs(self.persist_dir, exist_ok=True)
                
                self._client = chromadb.PersistentClient(
                    path=self.persist_dir,
                    settings=Settings(anonymized_telemetry=False)
                )
                logger.info(f"ChromaDB initialized at {self.persist_dir}")
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB: {e}")
                return None
        return self._client
    
    def _get_collection(self, name: str):
        """Get or create a collection"""
        if name not in self._collections:
            client = self._get_client()
            if client:
                self._collections[name] = client.get_or_create_collection(
                    name=name,
                    metadata={"hnsw:space": "cosine"}
                )
        return self._collections.get(name)
    
    async def store_interaction(
        self,
        prompt: str,
        response: str,
        project_type: str,
        success: bool,
        metadata: Dict = None
    ) -> str:
        """Store a user interaction for learning"""
        collection = self._get_collection("interactions")
        if not collection:
            return None
        
        interaction_id = f"int_{uuid.uuid4().hex[:12]}"
        
        doc_metadata = {
            "project_type": project_type,
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt_length": len(prompt),
            "response_length": len(response),
            **(metadata or {})
        }
        
        try:
            collection.add(
                ids=[interaction_id],
                documents=[f"{prompt}\n\n---\n\n{response[:2000]}"],
                metadatas=[doc_metadata]
            )
            return interaction_id
        except Exception as e:
            logger.error(f"Failed to store interaction: {e}")
            return None
    
    async def store_successful_prompt(
        self,
        prompt: str,
        system_prompt: str,
        agent_role: str,
        quality_score: float,
        metadata: Dict = None
    ) -> str:
        """Store a successful prompt for future reference"""
        collection = self._get_collection("successful_prompts")
        if not collection:
            return None
        
        prompt_id = f"prm_{uuid.uuid4().hex[:12]}"
        
        doc_metadata = {
            "agent_role": agent_role,
            "quality_score": quality_score,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **(metadata or {})
        }
        
        try:
            collection.add(
                ids=[prompt_id],
                documents=[f"SYSTEM: {system_prompt[:500]}\n\nUSER: {prompt}"],
                metadatas=[doc_metadata]
            )
            return prompt_id
        except Exception as e:
            logger.error(f"Failed to store prompt: {e}")
            return None
    
    async def find_similar_prompts(
        self,
        query: str,
        agent_role: str = None,
        min_score: float = 0.7,
        limit: int = 5
    ) -> List[Dict]:
        """Find similar successful prompts for context"""
        collection = self._get_collection("successful_prompts")
        if not collection:
            return []
        
        try:
            where_filter = None
            if agent_role:
                where_filter = {"agent_role": agent_role}
            
            results = collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_filter
            )
            
            similar = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    if metadata.get('quality_score', 0) >= min_score:
                        similar.append({
                            "id": results['ids'][0][i],
                            "content": doc,
                            "metadata": metadata
                        })
            
            return similar
        except Exception as e:
            logger.error(f"Failed to find similar prompts: {e}")
            return []
    
    async def store_code_pattern(
        self,
        code: str,
        pattern_type: str,
        language: str,
        quality_score: float
    ) -> str:
        """Store successful code patterns"""
        collection = self._get_collection("code_patterns")
        if not collection:
            return None
        
        pattern_id = f"pat_{uuid.uuid4().hex[:12]}"
        
        try:
            collection.add(
                ids=[pattern_id],
                documents=[code[:5000]],
                metadatas={
                    "pattern_type": pattern_type,
                    "language": language,
                    "quality_score": quality_score,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            return pattern_id
        except Exception as e:
            logger.error(f"Failed to store code pattern: {e}")
            return None
    
    async def find_code_patterns(
        self,
        query: str,
        language: str = None,
        limit: int = 3
    ) -> List[Dict]:
        """Find relevant code patterns"""
        collection = self._get_collection("code_patterns")
        if not collection:
            return []
        
        try:
            where_filter = {"language": language} if language else None
            
            results = collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_filter
            )
            
            patterns = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    patterns.append({
                        "id": results['ids'][0][i],
                        "code": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {}
                    })
            
            return patterns
        except Exception as e:
            logger.error(f"Failed to find code patterns: {e}")
            return []


# ============= QUALITY SCORING SYSTEM =============

class QualityScorer:
    """
    Scoring system for measuring quality of generations.
    Tracks: success rate, user satisfaction, error rate, generation time.
    """
    
    def __init__(self, db):
        self.db = db
    
    async def record_generation(
        self,
        project_id: str,
        agent_role: str,
        generation_time: float,
        files_generated: int,
        errors: List[str] = None,
        model_used: str = "gpt-4o"
    ) -> str:
        """Record a generation event for scoring"""
        score_id = f"score_{uuid.uuid4().hex[:12]}"
        
        # Calculate initial score
        base_score = 100
        
        # Penalize for errors
        error_count = len(errors) if errors else 0
        base_score -= error_count * 10
        
        # Penalize for slow generation (>30s is slow)
        if generation_time > 30:
            base_score -= min(20, (generation_time - 30) / 2)
        
        # Bonus for more files (complex projects)
        if files_generated > 5:
            base_score += min(10, files_generated - 5)
        
        score = max(0, min(100, base_score))
        
        record = {
            "id": score_id,
            "project_id": project_id,
            "agent_role": agent_role,
            "generation_time": generation_time,
            "files_generated": files_generated,
            "error_count": error_count,
            "errors": errors or [],
            "model_used": model_used,
            "initial_score": score,
            "final_score": None,  # Set after user feedback
            "user_feedback": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.quality_scores.insert_one(record)
        
        return score_id
    
    async def record_user_feedback(
        self,
        score_id: str,
        rating: int,  # 1-5
        feedback_text: str = None,
        regenerated: bool = False
    ):
        """Record user feedback for a generation"""
        # Adjust final score based on feedback
        score_record = await self.db.quality_scores.find_one({"id": score_id})
        if not score_record:
            return
        
        initial = score_record.get("initial_score", 50)
        
        # Rating adjustments
        rating_adjustments = {1: -30, 2: -15, 3: 0, 4: 10, 5: 20}
        adjustment = rating_adjustments.get(rating, 0)
        
        # Regeneration penalty
        if regenerated:
            adjustment -= 15
        
        final_score = max(0, min(100, initial + adjustment))
        
        await self.db.quality_scores.update_one(
            {"id": score_id},
            {"$set": {
                "final_score": final_score,
                "user_feedback": {
                    "rating": rating,
                    "text": feedback_text,
                    "regenerated": regenerated,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }}
        )
        
        return final_score
    
    async def get_agent_performance(self, agent_role: str, days: int = 7) -> Dict:
        """Get performance metrics for an agent"""
        from datetime import timedelta
        
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        pipeline = [
            {"$match": {
                "agent_role": agent_role,
                "created_at": {"$gte": cutoff}
            }},
            {"$group": {
                "_id": None,
                "total_generations": {"$sum": 1},
                "avg_initial_score": {"$avg": "$initial_score"},
                "avg_final_score": {"$avg": {"$ifNull": ["$final_score", "$initial_score"]}},
                "avg_generation_time": {"$avg": "$generation_time"},
                "total_errors": {"$sum": "$error_count"},
                "avg_files": {"$avg": "$files_generated"}
            }}
        ]
        
        results = await self.db.quality_scores.aggregate(pipeline).to_list(1)
        
        if results:
            return {
                "agent_role": agent_role,
                "period_days": days,
                **results[0]
            }
        
        return {
            "agent_role": agent_role,
            "period_days": days,
            "total_generations": 0,
            "avg_initial_score": 0,
            "avg_final_score": 0
        }
    
    async def get_overall_metrics(self, days: int = 7) -> Dict:
        """Get overall system metrics"""
        from datetime import timedelta
        
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        # Aggregate by agent
        pipeline = [
            {"$match": {"created_at": {"$gte": cutoff}}},
            {"$group": {
                "_id": "$agent_role",
                "count": {"$sum": 1},
                "avg_score": {"$avg": {"$ifNull": ["$final_score", "$initial_score"]}},
                "avg_time": {"$avg": "$generation_time"}
            }}
        ]
        
        agent_stats = await self.db.quality_scores.aggregate(pipeline).to_list(20)
        
        # Overall stats
        total_pipeline = [
            {"$match": {"created_at": {"$gte": cutoff}}},
            {"$group": {
                "_id": None,
                "total": {"$sum": 1},
                "avg_score": {"$avg": {"$ifNull": ["$final_score", "$initial_score"]}},
                "with_feedback": {"$sum": {"$cond": [{"$ne": ["$user_feedback", None]}, 1, 0]}}
            }}
        ]
        
        overall = await self.db.quality_scores.aggregate(total_pipeline).to_list(1)
        
        return {
            "period_days": days,
            "overall": overall[0] if overall else {},
            "by_agent": {s["_id"]: s for s in agent_stats if s["_id"]}
        }


# ============= PROMPT OPTIMIZER =============

class PromptOptimizer:
    """
    Automatic prompt optimization based on performance.
    Learns which prompts work best for different scenarios.
    """
    
    def __init__(self, db, vector_memory: VectorMemory):
        self.db = db
        self.memory = vector_memory
        self.prompt_cache = {}
    
    async def get_optimized_prompt(
        self,
        base_prompt: str,
        agent_role: str,
        project_type: str
    ) -> Tuple[str, Dict]:
        """Get an optimized prompt based on historical performance"""
        
        # Find similar successful prompts
        similar = await self.memory.find_similar_prompts(
            query=base_prompt,
            agent_role=agent_role,
            min_score=0.75,
            limit=3
        )
        
        # Get best performing prompt variations for this agent
        best_prompts = await self._get_best_prompts(agent_role, project_type)
        
        # Build context from successful patterns
        context_additions = []
        
        if similar:
            context_additions.append("Based on similar successful generations:")
            for s in similar[:2]:
                context_additions.append(f"- {s['content'][:200]}...")
        
        if best_prompts:
            context_additions.append("\nOptimal patterns for this type:")
            for bp in best_prompts[:2]:
                if bp.get("pattern"):
                    context_additions.append(f"- {bp['pattern'][:150]}")
        
        # Find relevant code patterns
        code_patterns = await self.memory.find_code_patterns(
            query=base_prompt,
            limit=2
        )
        
        if code_patterns:
            context_additions.append("\nRelevant code examples:")
            for cp in code_patterns:
                context_additions.append(f"```\n{cp['code'][:300]}\n```")
        
        # Construct enhanced prompt
        if context_additions:
            enhanced_prompt = f"""{base_prompt}

[LEARNING CONTEXT]
{chr(10).join(context_additions)}
[END CONTEXT]"""
        else:
            enhanced_prompt = base_prompt
        
        metadata = {
            "similar_prompts_found": len(similar),
            "code_patterns_found": len(code_patterns),
            "optimization_applied": bool(context_additions)
        }
        
        return enhanced_prompt, metadata
    
    async def _get_best_prompts(self, agent_role: str, project_type: str) -> List[Dict]:
        """Get best performing prompts for agent and project type"""
        pipeline = [
            {"$match": {
                "agent_role": agent_role,
                "project_type": project_type,
                "final_score": {"$gte": 80}
            }},
            {"$sort": {"final_score": -1}},
            {"$limit": 5},
            {"$project": {
                "pattern": "$prompt_pattern",
                "score": "$final_score"
            }}
        ]
        
        return await self.db.prompt_performance.aggregate(pipeline).to_list(5)
    
    async def record_prompt_performance(
        self,
        prompt: str,
        agent_role: str,
        project_type: str,
        score: float
    ):
        """Record prompt performance for learning"""
        # Extract key pattern from prompt
        pattern = self._extract_pattern(prompt)
        
        record = {
            "id": f"perf_{uuid.uuid4().hex[:12]}",
            "prompt_hash": hashlib.md5(prompt.encode()).hexdigest(),
            "prompt_pattern": pattern,
            "agent_role": agent_role,
            "project_type": project_type,
            "final_score": score,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.prompt_performance.insert_one(record)
        
        # Store in vector memory if high quality
        if score >= 80:
            await self.memory.store_successful_prompt(
                prompt=prompt,
                system_prompt="",  # Would come from agent
                agent_role=agent_role,
                quality_score=score,
                metadata={"project_type": project_type}
            )
    
    def _extract_pattern(self, prompt: str) -> str:
        """Extract reusable pattern from prompt"""
        # Simple extraction - first 200 chars or first sentence
        if len(prompt) <= 200:
            return prompt
        
        # Find first sentence
        for delim in ['. ', '.\n', '\n\n']:
            if delim in prompt[:300]:
                return prompt[:prompt.index(delim) + 1]
        
        return prompt[:200] + "..."


# ============= FEEDBACK ANALYZER =============

class FeedbackAnalyzer:
    """
    Analyzes user feedback to improve the system.
    Identifies patterns in negative feedback to fix issues.
    """
    
    def __init__(self, db):
        self.db = db
    
    async def record_feedback(
        self,
        project_id: str,
        rating: int,  # 1-5 stars or thumbs up/down
        feedback_type: str,  # "rating", "thumbs", "comment"
        feedback_text: str = None,
        context: Dict = None
    ) -> str:
        """Record user feedback"""
        feedback_id = f"fb_{uuid.uuid4().hex[:12]}"
        
        feedback = {
            "id": feedback_id,
            "project_id": project_id,
            "rating": rating,
            "feedback_type": feedback_type,
            "feedback_text": feedback_text,
            "context": context or {},
            "analyzed": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.user_feedback.insert_one(feedback)
        
        # Trigger analysis for negative feedback
        if rating <= 2:
            await self._analyze_negative_feedback(feedback)
        
        return feedback_id
    
    async def _analyze_negative_feedback(self, feedback: Dict):
        """Analyze negative feedback to identify issues"""
        issues = []
        
        text = feedback.get("feedback_text", "").lower()
        context = feedback.get("context", {})
        
        # Common issue patterns
        issue_patterns = {
            "error": "code_errors",
            "bug": "code_errors",
            "doesn't work": "functionality",
            "no funciona": "functionality",
            "slow": "performance",
            "lento": "performance",
            "ugly": "design",
            "feo": "design",
            "incomplete": "completeness",
            "incompleto": "completeness",
            "wrong": "accuracy",
            "incorrect": "accuracy"
        }
        
        for pattern, issue_type in issue_patterns.items():
            if pattern in text:
                issues.append(issue_type)
        
        if issues:
            await self.db.user_feedback.update_one(
                {"id": feedback["id"]},
                {"$set": {
                    "analyzed": True,
                    "detected_issues": list(set(issues))
                }}
            )
            
            # Record issue for improvement tracking
            for issue in set(issues):
                await self._record_issue(
                    issue_type=issue,
                    project_id=feedback["project_id"],
                    feedback_id=feedback["id"]
                )
    
    async def _record_issue(self, issue_type: str, project_id: str, feedback_id: str):
        """Record an issue for tracking"""
        await self.db.improvement_issues.insert_one({
            "id": f"issue_{uuid.uuid4().hex[:12]}",
            "issue_type": issue_type,
            "project_id": project_id,
            "feedback_id": feedback_id,
            "status": "open",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    async def get_feedback_summary(self, days: int = 7) -> Dict:
        """Get summary of recent feedback"""
        from datetime import timedelta
        
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        # Rating distribution
        rating_pipeline = [
            {"$match": {"created_at": {"$gte": cutoff}}},
            {"$group": {
                "_id": "$rating",
                "count": {"$sum": 1}
            }}
        ]
        
        ratings = await self.db.user_feedback.aggregate(rating_pipeline).to_list(10)
        rating_dist = {r["_id"]: r["count"] for r in ratings}
        
        # Issue distribution
        issue_pipeline = [
            {"$match": {"created_at": {"$gte": cutoff}, "status": "open"}},
            {"$group": {
                "_id": "$issue_type",
                "count": {"$sum": 1}
            }}
        ]
        
        issues = await self.db.improvement_issues.aggregate(issue_pipeline).to_list(20)
        issue_dist = {i["_id"]: i["count"] for i in issues}
        
        # Calculate satisfaction score
        total_feedback = sum(rating_dist.values())
        positive = rating_dist.get(4, 0) + rating_dist.get(5, 0)
        satisfaction = (positive / total_feedback * 100) if total_feedback > 0 else 0
        
        return {
            "period_days": days,
            "total_feedback": total_feedback,
            "satisfaction_score": round(satisfaction, 1),
            "rating_distribution": rating_dist,
            "open_issues": issue_dist,
            "top_issues": sorted(issue_dist.items(), key=lambda x: x[1], reverse=True)[:5]
        }


# ============= INTELLIGENT AGENT ROUTER =============

class AgentRouter:
    """
    Intelligent router that learns which agent to use for different tasks.
    Optimizes model selection based on task complexity and performance.
    """
    
    def __init__(self, db, quality_scorer: QualityScorer):
        self.db = db
        self.scorer = quality_scorer
        
        # Agent capabilities
        self.agents = {
            "planner": {
                "strengths": ["architecture", "planning", "requirements"],
                "default_model": "gpt-4o"
            },
            "code": {
                "strengths": ["implementation", "coding", "debugging"],
                "default_model": "gpt-4o"
            },
            "reasoning": {
                "strengths": ["analysis", "design", "patterns"],
                "default_model": "gpt-4o"
            },
            "qa": {
                "strengths": ["testing", "validation", "review"],
                "default_model": "gpt-4o"
            },
            "security": {
                "strengths": ["security", "vulnerabilities", "audit"],
                "default_model": "gpt-4o"
            },
            "optimization": {
                "strengths": ["performance", "optimization", "speed"],
                "default_model": "gpt-4o"
            }
        }
    
    async def route_task(self, task_description: str, project_type: str) -> Dict:
        """Route a task to the best agent and model"""
        
        # Analyze task to determine best agent
        task_lower = task_description.lower()
        
        # Score each agent for this task
        agent_scores = {}
        
        for agent_name, config in self.agents.items():
            score = 0
            
            # Check strengths match
            for strength in config["strengths"]:
                if strength in task_lower:
                    score += 20
            
            # Get historical performance
            perf = await self.scorer.get_agent_performance(agent_name)
            if perf.get("avg_final_score"):
                score += perf["avg_final_score"] * 0.5
            
            agent_scores[agent_name] = score
        
        # Select best agent
        best_agent = max(agent_scores, key=agent_scores.get)
        
        # Determine model based on complexity
        model = await self._select_model(task_description, best_agent, project_type)
        
        return {
            "agent": best_agent,
            "model": model,
            "confidence": agent_scores[best_agent],
            "all_scores": agent_scores
        }
    
    async def _select_model(
        self,
        task: str,
        agent: str,
        project_type: str
    ) -> str:
        """Select the optimal model for the task"""
        
        # Simple complexity heuristics
        complexity_indicators = [
            "complex", "advanced", "full-stack", "complete",
            "production", "scalable", "enterprise"
        ]
        
        is_complex = any(ind in task.lower() for ind in complexity_indicators)
        
        # Check historical model performance for this agent
        pipeline = [
            {"$match": {
                "agent_role": agent,
                "final_score": {"$exists": True}
            }},
            {"$group": {
                "_id": "$model_used",
                "avg_score": {"$avg": "$final_score"},
                "count": {"$sum": 1}
            }},
            {"$match": {"count": {"$gte": 5}}}  # Need enough data
        ]
        
        model_stats = await self.db.quality_scores.aggregate(pipeline).to_list(5)
        
        if model_stats:
            # Use model with best average score
            best_model = max(model_stats, key=lambda x: x["avg_score"])
            if best_model["avg_score"] >= 75:
                return best_model["_id"]
        
        # Default to gpt-4o for complex tasks
        return "gpt-4o" if is_complex else "gpt-4o"
    
    async def record_routing_result(
        self,
        task_description: str,
        agent_used: str,
        model_used: str,
        success: bool,
        quality_score: float
    ):
        """Record routing decision outcome for learning"""
        await self.db.routing_history.insert_one({
            "id": f"route_{uuid.uuid4().hex[:12]}",
            "task_hash": hashlib.md5(task_description.encode()).hexdigest(),
            "task_preview": task_description[:200],
            "agent_used": agent_used,
            "model_used": model_used,
            "success": success,
            "quality_score": quality_score,
            "created_at": datetime.now(timezone.utc).isoformat()
        })


# ============= LEARNING COORDINATOR =============

class LearningCoordinator:
    """
    Main coordinator for the continuous learning system.
    Orchestrates all learning components.
    """
    
    def __init__(self, db):
        self.db = db
        self.vector_memory = VectorMemory()
        self.quality_scorer = QualityScorer(db)
        self.prompt_optimizer = PromptOptimizer(db, self.vector_memory)
        self.feedback_analyzer = FeedbackAnalyzer(db)
        self.agent_router = AgentRouter(db, self.quality_scorer)
    
    async def process_generation_start(
        self,
        project_id: str,
        prompt: str,
        project_type: str
    ) -> Dict:
        """Called when a generation starts - returns optimized settings"""
        
        # Get routing recommendation
        routing = await self.agent_router.route_task(prompt, project_type)
        
        # Get optimized prompt
        optimized_prompt, opt_metadata = await self.prompt_optimizer.get_optimized_prompt(
            base_prompt=prompt,
            agent_role=routing["agent"],
            project_type=project_type
        )
        
        return {
            "routing": routing,
            "optimized_prompt": optimized_prompt,
            "optimization_metadata": opt_metadata
        }
    
    async def process_generation_complete(
        self,
        project_id: str,
        prompt: str,
        response: str,
        agent_role: str,
        project_type: str,
        generation_time: float,
        files_generated: int,
        errors: List[str] = None,
        model_used: str = "gpt-4o"
    ) -> str:
        """Called when a generation completes - records metrics"""
        
        # Record quality score
        score_id = await self.quality_scorer.record_generation(
            project_id=project_id,
            agent_role=agent_role,
            generation_time=generation_time,
            files_generated=files_generated,
            errors=errors,
            model_used=model_used
        )
        
        # Store interaction in vector memory
        success = not errors or len(errors) == 0
        await self.vector_memory.store_interaction(
            prompt=prompt,
            response=response,
            project_type=project_type,
            success=success,
            metadata={
                "agent_role": agent_role,
                "generation_time": generation_time,
                "files_generated": files_generated
            }
        )
        
        return score_id
    
    async def process_user_feedback(
        self,
        project_id: str,
        score_id: str,
        rating: int,
        feedback_text: str = None,
        regenerated: bool = False
    ):
        """Called when user provides feedback"""
        
        # Record in quality scorer
        final_score = await self.quality_scorer.record_user_feedback(
            score_id=score_id,
            rating=rating,
            feedback_text=feedback_text,
            regenerated=regenerated
        )
        
        # Record in feedback analyzer
        await self.feedback_analyzer.record_feedback(
            project_id=project_id,
            rating=rating,
            feedback_type="rating",
            feedback_text=feedback_text,
            context={"score_id": score_id, "regenerated": regenerated}
        )
        
        # Update prompt performance if we have the data
        if final_score and final_score >= 70:
            # This would need prompt data from the generation
            pass
        
        return final_score
    
    async def get_system_insights(self) -> Dict:
        """Get insights about system performance for dashboard"""
        
        # Quality metrics
        metrics = await self.quality_scorer.get_overall_metrics(days=7)
        
        # Feedback summary
        feedback = await self.feedback_analyzer.get_feedback_summary(days=7)
        
        # Top performing agents
        agent_performance = {}
        for agent in ["planner", "code", "reasoning", "qa"]:
            perf = await self.quality_scorer.get_agent_performance(agent)
            agent_performance[agent] = perf
        
        return {
            "quality_metrics": metrics,
            "feedback_summary": feedback,
            "agent_performance": agent_performance,
            "recommendations": await self._generate_recommendations(metrics, feedback)
        }
    
    async def _generate_recommendations(self, metrics: Dict, feedback: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check satisfaction
        if feedback.get("satisfaction_score", 100) < 70:
            recommendations.append(
                "User satisfaction is below 70%. Review recent negative feedback."
            )
        
        # Check agent performance
        by_agent = metrics.get("by_agent", {})
        for agent, stats in by_agent.items():
            if stats.get("avg_score", 100) < 60:
                recommendations.append(
                    f"Agent '{agent}' has low average score ({stats['avg_score']:.0f}). "
                    "Consider reviewing system prompts."
                )
        
        # Check for common issues
        top_issues = feedback.get("top_issues", [])
        if top_issues:
            top_issue = top_issues[0]
            recommendations.append(
                f"Most common issue: '{top_issue[0]}' ({top_issue[1]} occurrences). "
                "Prioritize fixing this."
            )
        
        return recommendations
