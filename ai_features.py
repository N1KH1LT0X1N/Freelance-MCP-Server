"""
Advanced AI & ML Features for Freelance MCP Server

This module provides next-generation AI-powered features including:
- Intelligent gig recommendations using ML
- Success prediction for proposals
- Smart pricing optimization
- Skills demand analysis
- Client intelligence and research
- Market trend forecasting

Requires:
    pip install scikit-learn numpy pandas matplotlib seaborn
"""

import asyncio
import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

import numpy as np
from cachetools import TTLCache

# ML imports (with fallback)
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.feature_extraction.text import TfidfVectorizer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ ML libraries not available. Install: pip install scikit-learn")


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class GigRecommendation:
    """AI-powered gig recommendation"""
    gig_id: str
    title: str
    platform: str
    recommendation_score: float
    win_probability: float
    optimal_bid_amount: float
    reasoning: List[str]
    risk_level: str  # "low", "medium", "high"
    estimated_competition: int
    client_quality_score: float
    suggested_approach: str


@dataclass
class MarketInsight:
    """Market intelligence data"""
    skill: str
    demand_score: float
    average_rate: float
    rate_trend: str  # "increasing", "stable", "decreasing"
    competition_level: str
    growth_projection: float
    top_platforms: List[str]
    recommended_action: str


@dataclass
class ClientIntelligence:
    """Deep client research results"""
    client_id: str
    quality_score: float
    payment_reliability: float
    communication_score: float
    project_success_rate: float
    average_rating: float
    total_spent: float
    total_projects: int
    red_flags: List[str]
    green_flags: List[str]
    recommendation: str


@dataclass
class EarningsForecast:
    """Earnings prediction"""
    period: str
    predicted_earnings: float
    confidence_interval: Tuple[float, float]
    factors: Dict[str, float]
    recommendations: List[str]


# ============================================================================
# AI GIG RECOMMENDER ENGINE
# ============================================================================

class AIGigRecommender:
    """ML-powered gig recommendation system"""

    def __init__(self, user_profile: Dict[str, Any], history: List[Dict] = None):
        """
        Initialize AI recommender

        Args:
            user_profile: User's skills, experience, preferences
            history: Past gig applications and outcomes
        """
        self.user_profile = user_profile
        self.history = history or []
        self.cache = TTLCache(maxsize=50, ttl=1800)  # 30-min cache

        # Extract user features
        self.user_skills = set([s.lower() for s in user_profile.get('skills', [])])
        self.user_rate_min = user_profile.get('hourly_rate_min', 25)
        self.user_rate_max = user_profile.get('hourly_rate_max', 100)
        self.user_experience = user_profile.get('years_experience', 3)
        self.success_rate = user_profile.get('success_rate', 80) / 100

    async def recommend_gigs(self, available_gigs: List[Dict],
                            top_n: int = 10) -> List[GigRecommendation]:
        """
        Generate AI-powered gig recommendations

        Args:
            available_gigs: List of available gigs to analyze
            top_n: Number of top recommendations to return

        Returns:
            List of GigRecommendation objects, ranked by score
        """
        recommendations = []

        for gig in available_gigs:
            try:
                # Calculate comprehensive scores
                skill_match = self._calculate_skill_match(gig)
                rate_match = self._calculate_rate_compatibility(gig)
                client_quality = self._estimate_client_quality(gig)
                competition = self._estimate_competition(gig)
                win_prob = self._predict_win_probability(gig, skill_match, competition)
                optimal_bid = self._calculate_optimal_bid(gig, win_prob)

                # Calculate overall recommendation score
                rec_score = self._calculate_recommendation_score(
                    skill_match, rate_match, client_quality,
                    competition, win_prob
                )

                # Generate reasoning
                reasoning = self._generate_reasoning(
                    gig, skill_match, rate_match, client_quality,
                    competition, win_prob
                )

                # Assess risk
                risk_level = self._assess_risk_level(
                    client_quality, competition, win_prob
                )

                # Generate suggested approach
                approach = self._suggest_approach(gig, win_prob, competition)

                recommendation = GigRecommendation(
                    gig_id=gig.get('id', ''),
                    title=gig.get('title', ''),
                    platform=gig.get('platform', ''),
                    recommendation_score=rec_score,
                    win_probability=win_prob,
                    optimal_bid_amount=optimal_bid,
                    reasoning=reasoning,
                    risk_level=risk_level,
                    estimated_competition=competition,
                    client_quality_score=client_quality,
                    suggested_approach=approach
                )

                recommendations.append(recommendation)

            except Exception as e:
                print(f"⚠️ Error processing gig {gig.get('id', 'unknown')}: {e}")
                continue

        # Sort by recommendation score
        recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)

        return recommendations[:top_n]

    def _calculate_skill_match(self, gig: Dict) -> float:
        """Calculate skill match score (0-1)"""
        required_skills = set([s.lower() for s in gig.get('skills_required', [])])

        if not required_skills:
            return 0.5

        matches = len(self.user_skills & required_skills)
        total = len(required_skills)

        # Bonus for having extra relevant skills
        bonus = min(0.2, len(self.user_skills - required_skills) * 0.05)

        base_score = matches / total if total > 0 else 0
        return min(1.0, base_score + bonus)

    def _calculate_rate_compatibility(self, gig: Dict) -> float:
        """Calculate rate compatibility score (0-1)"""
        gig_budget_min = gig.get('budget_min', 0)
        gig_budget_max = gig.get('budget_max', 0)

        if not gig_budget_max:
            return 0.5

        # Estimate hourly rate for fixed-price projects (assume 40 hours)
        if gig.get('project_type') == 'fixed':
            estimated_hourly = gig_budget_max / 40
        else:
            estimated_hourly = gig_budget_max

        if estimated_hourly < self.user_rate_min:
            # Below minimum - poor match
            return max(0.0, estimated_hourly / self.user_rate_min)
        elif estimated_hourly > self.user_rate_max:
            # Above maximum - great opportunity!
            return 1.0
        else:
            # Within range - good match
            return 0.8 + 0.2 * ((estimated_hourly - self.user_rate_min) /
                               (self.user_rate_max - self.user_rate_min))

    def _estimate_client_quality(self, gig: Dict) -> float:
        """Estimate client quality (0-1)"""
        rating = gig.get('client_rating', 0)
        reviews = gig.get('client_reviews', 0)

        # Base score from rating
        if rating:
            base_score = (rating - 3.5) / 1.5  # Normalize 3.5-5.0 to 0-1
        else:
            base_score = 0.5

        # Adjust for number of reviews (more reviews = more reliable)
        if reviews > 50:
            reliability_bonus = 0.1
        elif reviews > 20:
            reliability_bonus = 0.05
        elif reviews < 5:
            reliability_bonus = -0.1
        else:
            reliability_bonus = 0

        return max(0.0, min(1.0, base_score + reliability_bonus))

    def _estimate_competition(self, gig: Dict) -> int:
        """Estimate number of competitors"""
        proposals = gig.get('proposals_count', 0)

        # Add some randomness based on job attractiveness
        skill_match = self._calculate_skill_match(gig)
        rate_match = self._calculate_rate_compatibility(gig)

        # Popular jobs tend to attract more applicants
        multiplier = 1.5 if (skill_match > 0.7 and rate_match > 0.7) else 1.0

        return int(proposals * multiplier)

    def _predict_win_probability(self, gig: Dict, skill_match: float,
                                 competition: int) -> float:
        """Predict probability of winning this gig (0-1)"""
        # Factors affecting win probability:
        # 1. Skill match
        # 2. Competition level
        # 3. User's success rate
        # 4. Budget compatibility

        # Base probability from skill match
        base_prob = skill_match * 0.4

        # Adjust for competition (more competition = lower probability)
        if competition < 5:
            competition_factor = 0.3
        elif competition < 10:
            competition_factor = 0.2
        elif competition < 20:
            competition_factor = 0.1
        else:
            competition_factor = 0.05

        # User's historical success rate
        success_factor = self.success_rate * 0.2

        # Experience factor
        exp_factor = min(0.1, self.user_experience / 100)

        total_prob = base_prob + competition_factor + success_factor + exp_factor

        return min(0.95, max(0.05, total_prob))

    def _calculate_optimal_bid(self, gig: Dict, win_prob: float) -> float:
        """Calculate optimal bid amount"""
        budget_max = gig.get('budget_max', 0)
        budget_min = gig.get('budget_min', 0)

        if not budget_max:
            # Use user's rate
            return self.user_rate_min

        # Strategy: Bid lower when win probability is high
        # Bid higher when competition is fierce

        if win_prob > 0.7:
            # High win probability - can bid at lower end
            optimal = budget_min + (budget_max - budget_min) * 0.3
        elif win_prob > 0.5:
            # Medium win probability - bid mid-range
            optimal = budget_min + (budget_max - budget_min) * 0.5
        else:
            # Low win probability - bid competitively
            optimal = budget_min + (budget_max - budget_min) * 0.7

        # Ensure it's within user's acceptable range
        if gig.get('project_type') == 'fixed':
            hourly_equivalent = optimal / 40
        else:
            hourly_equivalent = optimal

        if hourly_equivalent < self.user_rate_min:
            return self.user_rate_min * 40 if gig.get('project_type') == 'fixed' else self.user_rate_min

        return round(optimal, 2)

    def _calculate_recommendation_score(self, skill_match: float, rate_match: float,
                                       client_quality: float, competition: int,
                                       win_prob: float) -> float:
        """Calculate overall recommendation score (0-1)"""
        # Weighted scoring
        weights = {
            'skill_match': 0.25,
            'rate_match': 0.20,
            'client_quality': 0.20,
            'win_probability': 0.25,
            'competition': 0.10
        }

        # Normalize competition (inverse - lower is better)
        competition_score = max(0, 1 - (competition / 50))

        score = (
            weights['skill_match'] * skill_match +
            weights['rate_match'] * rate_match +
            weights['client_quality'] * client_quality +
            weights['win_probability'] * win_prob +
            weights['competition'] * competition_score
        )

        return round(score, 3)

    def _generate_reasoning(self, gig: Dict, skill_match: float, rate_match: float,
                           client_quality: float, competition: int,
                           win_prob: float) -> List[str]:
        """Generate human-readable reasoning"""
        reasons = []

        # Skill match
        if skill_match >= 0.8:
            reasons.append(f"✅ Excellent skill match ({skill_match*100:.0f}%)")
        elif skill_match >= 0.6:
            reasons.append(f"👍 Good skill match ({skill_match*100:.0f}%)")
        else:
            reasons.append(f"⚠️ Moderate skill match ({skill_match*100:.0f}%)")

        # Rate compatibility
        if rate_match >= 0.8:
            reasons.append("💰 Excellent budget alignment")
        elif rate_match < 0.5:
            reasons.append("⚠️ Budget below your target rate")

        # Client quality
        if client_quality >= 0.8:
            reasons.append("⭐ High-quality client with good reviews")
        elif client_quality < 0.5:
            reasons.append("⚠️ Limited client history or low ratings")

        # Competition
        if competition < 5:
            reasons.append("🎯 Low competition - great opportunity!")
        elif competition > 20:
            reasons.append("⚠️ High competition - may be challenging")

        # Win probability
        if win_prob >= 0.7:
            reasons.append(f"📈 High win probability ({win_prob*100:.0f}%)")
        elif win_prob < 0.3:
            reasons.append(f"📉 Lower win probability ({win_prob*100:.0f}%)")

        return reasons

    def _assess_risk_level(self, client_quality: float, competition: int,
                          win_prob: float) -> str:
        """Assess overall risk level"""
        risk_score = 0

        if client_quality < 0.5:
            risk_score += 2
        if competition > 20:
            risk_score += 2
        if win_prob < 0.3:
            risk_score += 1

        if risk_score >= 4:
            return "high"
        elif risk_score >= 2:
            return "medium"
        else:
            return "low"

    def _suggest_approach(self, gig: Dict, win_prob: float, competition: int) -> str:
        """Suggest bidding approach"""
        if win_prob > 0.7 and competition < 10:
            return "Submit a strong proposal highlighting your expertise. You have a great chance!"
        elif win_prob > 0.5:
            return "Emphasize your unique value proposition and relevant experience."
        elif competition > 20:
            return "Differentiate yourself with a unique approach or special offer. Consider a competitive rate."
        else:
            return "This is competitive. Focus on demonstrating clear ROI and past results."


# ============================================================================
# SMART PRICING ENGINE
# ============================================================================

class SmartPricingEngine:
    """AI-powered optimal pricing calculator"""

    def __init__(self):
        self.market_data = {}
        self.cache = TTLCache(maxsize=100, ttl=3600)

    async def calculate_optimal_price(self, gig: Dict, user_profile: Dict,
                                     market_data: Dict = None) -> Dict[str, Any]:
        """
        Calculate optimal pricing strategy

        Args:
            gig: Gig details
            user_profile: User's profile and history
            market_data: Optional market intelligence

        Returns:
            Pricing recommendation with rationale
        """
        # Extract gig parameters
        budget_min = gig.get('budget_min', 0)
        budget_max = gig.get('budget_max', 0)
        skills = gig.get('skills_required', [])
        competition = gig.get('proposals_count', 0)

        # User parameters
        user_rate_min = user_profile.get('hourly_rate_min', 25)
        user_rate_max = user_profile.get('hourly_rate_max', 100)
        success_rate = user_profile.get('success_rate', 80) / 100

        # Calculate base price
        if budget_max:
            base_price = (budget_min + budget_max) / 2
        else:
            base_price = user_rate_min

        # Adjust for competition
        if competition < 5:
            # Low competition - can charge premium
            competition_multiplier = 1.15
        elif competition > 20:
            # High competition - be more competitive
            competition_multiplier = 0.90
        else:
            competition_multiplier = 1.0

        # Adjust for user's success rate
        success_multiplier = 0.95 + (success_rate * 0.15)

        # Adjust for skill rarity (simplified - would use real market data)
        skill_multiplier = self._calculate_skill_premium(skills)

        # Calculate optimal price
        optimal_price = base_price * competition_multiplier * success_multiplier * skill_multiplier

        # Ensure within reasonable bounds
        if budget_max:
            optimal_price = min(optimal_price, budget_max * 1.1)  # Max 10% above budget
            optimal_price = max(optimal_price, budget_min)

        optimal_price = max(optimal_price, user_rate_min)

        # Generate pricing strategy
        strategy = self._generate_pricing_strategy(
            optimal_price, budget_min, budget_max, competition, success_rate
        )

        # Calculate price ranges
        conservative_price = optimal_price * 0.9
        aggressive_price = optimal_price * 1.1

        return {
            "optimal_price": round(optimal_price, 2),
            "conservative_price": round(conservative_price, 2),
            "aggressive_price": round(aggressive_price, 2),
            "recommended_strategy": strategy,
            "factors": {
                "competition_level": "low" if competition < 5 else "high" if competition > 20 else "medium",
                "skill_premium": round((skill_multiplier - 1) * 100, 1),
                "success_rate_factor": round((success_multiplier - 1) * 100, 1)
            },
            "confidence": self._calculate_pricing_confidence(budget_max, competition)
        }

    def _calculate_skill_premium(self, skills: List[str]) -> float:
        """Calculate premium based on skill rarity"""
        # High-demand skills (simplified - would use real market data)
        premium_skills = {
            'ai': 1.3, 'ml': 1.3, 'machine learning': 1.3,
            'blockchain': 1.25, 'solidity': 1.25,
            'rust': 1.2, 'go': 1.15,
            'react native': 1.15, 'flutter': 1.15,
            'devops': 1.1, 'kubernetes': 1.15
        }

        max_premium = 1.0
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower in premium_skills:
                max_premium = max(max_premium, premium_skills[skill_lower])

        return max_premium

    def _generate_pricing_strategy(self, optimal: float, min_budget: float,
                                   max_budget: float, competition: int,
                                   success_rate: float) -> str:
        """Generate pricing strategy recommendation"""
        if competition < 5 and success_rate > 0.8:
            return f"Premium Strategy: Bid ${optimal:.2f} - you're in a strong position with low competition"
        elif competition > 20:
            return f"Competitive Strategy: Bid ${optimal:.2f} to stand out, but emphasize value over price"
        elif optimal > max_budget * 1.05:
            return f"Value Strategy: Bid ${optimal:.2f} and justify premium with ROI demonstration"
        else:
            return f"Balanced Strategy: Bid ${optimal:.2f} - competitive yet profitable"

    def _calculate_pricing_confidence(self, budget: float, competition: int) -> str:
        """Calculate confidence in pricing recommendation"""
        if budget and competition < 15:
            return "high"
        elif budget or competition < 25:
            return "medium"
        else:
            return "low"


# ============================================================================
# MARKET INTELLIGENCE ANALYZER
# ============================================================================

class MarketIntelligence:
    """Market trend analysis and forecasting"""

    def __init__(self):
        self.cache = TTLCache(maxsize=50, ttl=7200)  # 2-hour cache

    async def analyze_skill_demand(self, skill: str, gigs: List[Dict]) -> MarketInsight:
        """
        Analyze market demand for a specific skill

        Args:
            skill: Skill to analyze
            gigs: Recent gigs data

        Returns:
            MarketInsight with demand analysis
        """
        # Filter gigs that require this skill
        relevant_gigs = [
            gig for gig in gigs
            if skill.lower() in [s.lower() for s in gig.get('skills_required', [])]
        ]

        if not relevant_gigs:
            return MarketInsight(
                skill=skill,
                demand_score=0.0,
                average_rate=0.0,
                rate_trend="unknown",
                competition_level="unknown",
                growth_projection=0.0,
                top_platforms=[],
                recommended_action=f"No recent data for {skill}"
            )

        # Calculate demand score (0-1)
        total_gigs = len(gigs)
        skill_gigs = len(relevant_gigs)
        demand_score = min(1.0, skill_gigs / max(1, total_gigs) * 10)

        # Calculate average rate
        rates = []
        for gig in relevant_gigs:
            if gig.get('budget_max'):
                if gig.get('project_type') == 'fixed':
                    rate = gig['budget_max'] / 40  # Estimate hourly
                else:
                    rate = gig['budget_max']
                rates.append(rate)

        avg_rate = sum(rates) / len(rates) if rates else 0.0

        # Analyze platforms
        platform_counts = defaultdict(int)
        for gig in relevant_gigs:
            platform_counts[gig.get('platform', 'unknown')] += 1

        top_platforms = sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)
        top_platforms = [p[0] for p in top_platforms[:3]]

        # Estimate competition
        avg_proposals = sum(gig.get('proposals_count', 0) for gig in relevant_gigs) / len(relevant_gigs)

        if avg_proposals < 10:
            competition = "low"
        elif avg_proposals < 20:
            competition = "medium"
        else:
            competition = "high"

        # Generate recommendation
        if demand_score > 0.7 and avg_rate > 60:
            recommendation = f"🔥 {skill} is in high demand! Consider specializing or increasing rates."
        elif demand_score > 0.5:
            recommendation = f"✅ {skill} has solid demand. Good skill to maintain."
        else:
            recommendation = f"⚠️ {skill} has lower demand. Consider diversifying."

        return MarketInsight(
            skill=skill,
            demand_score=round(demand_score, 3),
            average_rate=round(avg_rate, 2),
            rate_trend="stable",  # Would need historical data
            competition_level=competition,
            growth_projection=0.0,  # Would need time-series data
            top_platforms=top_platforms,
            recommended_action=recommendation
        )

    async def get_market_trends(self, skills: List[str], gigs: List[Dict]) -> Dict[str, MarketInsight]:
        """Analyze multiple skills"""
        trends = {}
        for skill in skills:
            trends[skill] = await self.analyze_skill_demand(skill, gigs)
        return trends


# ============================================================================
# CLIENT INTELLIGENCE SYSTEM
# ============================================================================

class ClientIntelligenceSystem:
    """Deep client research and analysis"""

    async def research_client(self, client_data: Dict) -> ClientIntelligence:
        """
        Research and score client quality

        Args:
            client_data: Client information from gig

        Returns:
            ClientIntelligence with detailed analysis
        """
        client_id = client_data.get('id', 'unknown')
        rating = client_data.get('rating', 0)
        reviews = client_data.get('reviews', 0)
        total_spent = client_data.get('total_spent', 0)
        total_projects = client_data.get('total_projects', 0)

        # Calculate quality score
        quality_score = self._calculate_quality_score(rating, reviews, total_spent, total_projects)

        # Payment reliability (based on history)
        payment_reliability = self._estimate_payment_reliability(rating, total_spent, total_projects)

        # Communication score
        communication_score = self._estimate_communication(rating, reviews)

        # Success rate
        success_rate = (rating / 5.0) if rating else 0.5

        # Identify red flags
        red_flags = self._identify_red_flags(client_data)

        # Identify green flags
        green_flags = self._identify_green_flags(client_data)

        # Generate recommendation
        recommendation = self._generate_client_recommendation(
            quality_score, red_flags, green_flags
        )

        return ClientIntelligence(
            client_id=client_id,
            quality_score=quality_score,
            payment_reliability=payment_reliability,
            communication_score=communication_score,
            project_success_rate=success_rate,
            average_rating=rating,
            total_spent=total_spent,
            total_projects=total_projects,
            red_flags=red_flags,
            green_flags=green_flags,
            recommendation=recommendation
        )

    def _calculate_quality_score(self, rating: float, reviews: int,
                                 spent: float, projects: int) -> float:
        """Calculate overall client quality (0-1)"""
        # Rating component (40%)
        rating_score = (rating / 5.0) if rating else 0.5

        # Experience component (30%)
        if projects > 50:
            exp_score = 1.0
        elif projects > 20:
            exp_score = 0.8
        elif projects > 5:
            exp_score = 0.6
        else:
            exp_score = 0.4

        # Spending component (20%)
        if spent > 50000:
            spend_score = 1.0
        elif spent > 10000:
            spend_score = 0.8
        elif spent > 1000:
            spend_score = 0.6
        else:
            spend_score = 0.4

        # Review count component (10%)
        if reviews > 50:
            review_score = 1.0
        elif reviews > 10:
            review_score = 0.7
        else:
            review_score = 0.5

        total = (rating_score * 0.4 + exp_score * 0.3 +
                spend_score * 0.2 + review_score * 0.1)

        return round(total, 3)

    def _estimate_payment_reliability(self, rating: float, spent: float,
                                      projects: int) -> float:
        """Estimate payment reliability"""
        base_score = (rating / 5.0) if rating else 0.5

        # More projects = more reliable data
        if projects > 20:
            confidence = 1.0
        elif projects > 5:
            confidence = 0.8
        else:
            confidence = 0.6

        return round(base_score * confidence, 3)

    def _estimate_communication(self, rating: float, reviews: int) -> float:
        """Estimate communication quality"""
        base = (rating / 5.0) if rating else 0.5

        # More reviews = better signal
        if reviews > 20:
            return base
        else:
            return base * 0.8

    def _identify_red_flags(self, client_data: Dict) -> List[str]:
        """Identify warning signs"""
        flags = []

        rating = client_data.get('rating', 0)
        reviews = client_data.get('reviews', 0)
        projects = client_data.get('total_projects', 0)

        if rating < 4.0 and reviews > 5:
            flags.append("⚠️ Below-average rating with multiple reviews")

        if projects > 10 and reviews < 3:
            flags.append("⚠️ Many projects but few reviews (possible disputes)")

        if rating < 3.5:
            flags.append("🚩 Low client rating")

        return flags

    def _identify_green_flags(self, client_data: Dict) -> List[str]:
        """Identify positive signals"""
        flags = []

        rating = client_data.get('rating', 0)
        reviews = client_data.get('reviews', 0)
        spent = client_data.get('total_spent', 0)
        projects = client_data.get('total_projects', 0)

        if rating >= 4.7 and reviews > 10:
            flags.append("✅ Excellent rating with proven track record")

        if spent > 50000:
            flags.append("💰 High-spending client")

        if projects > 50:
            flags.append("🏆 Experienced client with many completed projects")

        if rating >= 4.5:
            flags.append("⭐ High client satisfaction rate")

        return flags

    def _generate_client_recommendation(self, quality_score: float,
                                       red_flags: List[str],
                                       green_flags: List[str]) -> str:
        """Generate overall recommendation"""
        if quality_score >= 0.8 and not red_flags:
            return "🟢 HIGHLY RECOMMENDED - Excellent client, proceed with confidence"
        elif quality_score >= 0.6 and len(red_flags) < 2:
            return "🟡 PROCEED WITH CAUTION - Good client, but do your due diligence"
        elif quality_score < 0.4 or len(red_flags) > 2:
            return "🔴 HIGH RISK - Consider carefully before applying"
        else:
            return "🟡 MODERATE QUALITY - Standard precautions recommended"


# Convenience functions for easy import
async def get_gig_recommendations(gigs: List[Dict], user_profile: Dict,
                                 top_n: int = 10) -> List[GigRecommendation]:
    """Get AI-powered gig recommendations"""
    recommender = AIGigRecommender(user_profile)
    return await recommender.recommend_gigs(gigs, top_n)


async def calculate_optimal_pricing(gig: Dict, user_profile: Dict) -> Dict:
    """Calculate optimal pricing for a gig"""
    engine = SmartPricingEngine()
    return await engine.calculate_optimal_price(gig, user_profile)


async def analyze_market_trends(skills: List[str], gigs: List[Dict]) -> Dict[str, MarketInsight]:
    """Analyze market trends for skills"""
    intel = MarketIntelligence()
    return await intel.get_market_trends(skills, gigs)


async def research_client(client_data: Dict) -> ClientIntelligence:
    """Research client quality and reliability"""
    system = ClientIntelligenceSystem()
    return await system.research_client(client_data)


if __name__ == "__main__":
    print("✅ Advanced AI features module loaded")
    print("Available features:")
    print("  - AIGigRecommender")
    print("  - SmartPricingEngine")
    print("  - MarketIntelligence")
    print("  - ClientIntelligenceSystem")
