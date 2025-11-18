"""
Automation Features for Freelance MCP Server

This module provides powerful automation capabilities including:
- Auto-bidding agent with intelligent proposal generation
- Portfolio auto-generation from past work
- Multi-channel notifications (Email, Slack, Discord, Webhook)
- Scheduled gig monitoring
- Automated follow-ups

Requires:
    pip install requests aiohttp jinja2 markdown
"""

import asyncio
import json
import os
import smtplib
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional
from enum import Enum

import aiohttp
from dotenv import load_dotenv

# Load environment
load_dotenv()


# ============================================================================
# DATA MODELS
# ============================================================================

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    WEBHOOK = "webhook"
    CONSOLE = "console"


@dataclass
class AutoBidConfig:
    """Configuration for auto-bidding"""
    enabled: bool = False
    min_match_score: float = 0.7
    max_bids_per_day: int = 5
    min_budget: float = 500
    max_budget: float = 10000
    preferred_platforms: List[str] = None
    auto_apply: bool = False  # If True, actually submit; if False, just notify
    required_skills: List[str] = None


@dataclass
class Portfolio:
    """Auto-generated portfolio"""
    title: str
    description: str
    projects: List[Dict[str, Any]]
    skills: List[str]
    total_value: float
    success_rate: float
    testimonials: List[str]
    generated_html: str
    generated_markdown: str


# ============================================================================
# AUTO-BIDDING AGENT
# ============================================================================

class AutoBiddingAgent:
    """Intelligent auto-bidding system"""

    def __init__(self, user_profile: Dict, config: AutoBidConfig):
        """
        Initialize auto-bidding agent

        Args:
            user_profile: User's profile and preferences
            config: Auto-bid configuration
        """
        self.user_profile = user_profile
        self.config = config
        self.bids_today = 0
        self.last_reset = datetime.now().date()

    async def scan_and_bid(self, available_gigs: List[Dict],
                           recommender=None) -> List[Dict]:
        """
        Scan gigs and automatically bid on suitable ones

        Args:
            available_gigs: List of available gigs
            recommender: Optional AI recommender instance

        Returns:
            List of bids placed
        """
        # Reset daily counter if new day
        if datetime.now().date() > self.last_reset:
            self.bids_today = 0
            self.last_reset = datetime.now().date()

        # Check if auto-bid is enabled
        if not self.config.enabled:
            return []

        # Check daily limit
        if self.bids_today >= self.config.max_bids_per_day:
            print(f"⚠️ Daily bid limit reached ({self.config.max_bids_per_day})")
            return []

        bids_placed = []

        # Filter eligible gigs
        eligible_gigs = self._filter_eligible_gigs(available_gigs)

        # Get AI recommendations if available
        if recommender:
            from ai_features import AIGigRecommender
            ai_recommender = AIGigRecommender(self.user_profile)
            recommendations = await ai_recommender.recommend_gigs(eligible_gigs, top_n=10)

            # Sort by recommendation score
            recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)

            # Process top recommendations
            for rec in recommendations[:min(5, self.config.max_bids_per_day - self.bids_today)]:
                # Find the original gig
                gig = next((g for g in eligible_gigs if g['id'] == rec.gig_id), None)

                if gig and rec.recommendation_score >= self.config.min_match_score:
                    # Generate proposal
                    proposal = await self._generate_proposal(gig, rec)

                    # Create bid
                    bid = {
                        "gig_id": gig['id'],
                        "gig_title": gig['title'],
                        "platform": gig['platform'],
                        "bid_amount": rec.optimal_bid_amount,
                        "proposal": proposal,
                        "recommendation_score": rec.recommendation_score,
                        "win_probability": rec.win_probability,
                        "timestamp": datetime.now().isoformat(),
                        "status": "submitted" if self.config.auto_apply else "draft"
                    }

                    # If auto_apply is enabled, submit the bid
                    if self.config.auto_apply:
                        success = await self._submit_bid(gig, bid)
                        if success:
                            bids_placed.append(bid)
                            self.bids_today += 1
                            print(f"✅ Auto-bid submitted: {gig['title']} - ${rec.optimal_bid_amount}")
                    else:
                        # Just save as draft
                        bids_placed.append(bid)
                        print(f"📝 Draft proposal created: {gig['title']}")

        else:
            # No AI recommender - use simple filtering
            for gig in eligible_gigs[:min(5, self.config.max_bids_per_day - self.bids_today)]:
                proposal = await self._generate_simple_proposal(gig)

                bid = {
                    "gig_id": gig['id'],
                    "gig_title": gig['title'],
                    "platform": gig['platform'],
                    "bid_amount": gig.get('budget_min', 1000),
                    "proposal": proposal,
                    "timestamp": datetime.now().isoformat(),
                    "status": "draft"
                }

                bids_placed.append(bid)

        return bids_placed

    def _filter_eligible_gigs(self, gigs: List[Dict]) -> List[Dict]:
        """Filter gigs that meet auto-bid criteria"""
        eligible = []

        for gig in gigs:
            # Check budget
            budget_max = gig.get('budget_max', 0)
            if budget_max and (budget_max < self.config.min_budget or
                              budget_max > self.config.max_budget):
                continue

            # Check platform
            if (self.config.preferred_platforms and
                gig.get('platform') not in self.config.preferred_platforms):
                continue

            # Check required skills
            if self.config.required_skills:
                gig_skills = [s.lower() for s in gig.get('skills_required', [])]
                has_required = any(req.lower() in gig_skills
                                 for req in self.config.required_skills)
                if not has_required:
                    continue

            eligible.append(gig)

        return eligible

    async def _generate_proposal(self, gig: Dict, recommendation) -> str:
        """Generate AI-powered proposal"""
        # Use LangChain if available
        try:
            from langchain_groq import ChatGroq
            from dotenv import load_dotenv

            load_dotenv()
            groq_key = os.getenv("GROQ_API_KEY")

            if groq_key:
                llm = ChatGroq(groq_api_key=groq_key, model_name="mixtral-8x7b-32768")

                prompt = f"""
                Generate a compelling, professional freelance proposal for this job:

                Job Title: {gig['title']}
                Description: {gig['description']}
                Budget: ${recommendation.optimal_bid_amount}
                Skills Required: {', '.join(gig.get('skills_required', []))}

                User Profile:
                Name: {self.user_profile.get('name', 'Freelancer')}
                Experience: {self.user_profile.get('years_experience', 3)} years
                Success Rate: {self.user_profile.get('success_rate', 90)}%

                Strategy: {recommendation.suggested_approach}

                Generate a proposal (200-300 words) that:
                1. Shows understanding of requirements
                2. Highlights relevant experience
                3. Provides clear value proposition
                4. Includes timeline and deliverables
                5. Ends with a call to action

                Be professional, confident, and client-focused.
                """

                response = llm.invoke(prompt)
                return response.content
        except Exception as e:
            print(f"⚠️ AI proposal generation failed: {e}")

        # Fallback to template
        return self._generate_simple_proposal(gig)

    async def _generate_simple_proposal(self, gig: Dict) -> str:
        """Generate template-based proposal"""
        template = f"""
        Dear Hiring Manager,

        I am excited to submit my proposal for "{gig['title']}".

        With {self.user_profile.get('years_experience', 3)} years of experience in {', '.join(gig.get('skills_required', [])[:3])}, I am confident I can deliver exceptional results for this project.

        My Approach:
        - Thorough understanding of your requirements
        - Clear communication throughout the project
        - Timely delivery with quality assurance
        - Post-project support

        I have a {self.user_profile.get('success_rate', 90)}% success rate and have completed similar projects with excellent client satisfaction.

        I would love to discuss how I can help you achieve your goals. Please feel free to review my portfolio and let me know if you have any questions.

        Looking forward to working with you!

        Best regards,
        {self.user_profile.get('name', 'Freelancer')}
        """

        return template.strip()

    async def _submit_bid(self, gig: Dict, bid: Dict) -> bool:
        """Submit bid to platform (placeholder - would integrate with real APIs)"""
        # This would integrate with Upwork/Freelancer APIs
        # For now, just log it
        print(f"🚀 Submitting bid to {gig['platform']}: {gig['title']}")
        print(f"   Amount: ${bid['bid_amount']}")
        print(f"   Proposal length: {len(bid['proposal'])} characters")

        # In production, this would call the platform's API
        # await platform_api.submit_proposal(gig_id, bid_amount, proposal)

        return True  # Assume success for now


# ============================================================================
# PORTFOLIO GENERATOR
# ============================================================================

class PortfolioGenerator:
    """Auto-generate professional portfolio"""

    def __init__(self, user_profile: Dict, project_history: List[Dict] = None):
        """
        Initialize portfolio generator

        Args:
            user_profile: User's profile
            project_history: Past completed projects
        """
        self.user_profile = user_profile
        self.project_history = project_history or []

    async def generate_portfolio(self, template: str = "modern") -> Portfolio:
        """
        Generate professional portfolio

        Args:
            template: Portfolio template style

        Returns:
            Portfolio object with HTML and Markdown
        """
        # Collect all skills from projects
        all_skills = set()
        total_value = 0
        successful_projects = 0

        for project in self.project_history:
            all_skills.update(project.get('skills', []))
            total_value += project.get('budget', 0)
            if project.get('success', True):
                successful_projects += 1

        success_rate = (successful_projects / len(self.project_history) * 100
                       if self.project_history else 0)

        # Generate HTML
        html = self._generate_html_portfolio(template, list(all_skills),
                                             total_value, success_rate)

        # Generate Markdown
        markdown = self._generate_markdown_portfolio(list(all_skills),
                                                     total_value, success_rate)

        return Portfolio(
            title=f"{self.user_profile.get('name', 'Professional')} - Portfolio",
            description=self.user_profile.get('title', 'Freelance Professional'),
            projects=self.project_history,
            skills=list(all_skills),
            total_value=total_value,
            success_rate=success_rate,
            testimonials=self._extract_testimonials(),
            generated_html=html,
            generated_markdown=markdown
        )

    def _generate_html_portfolio(self, template: str, skills: List[str],
                                 total_value: float, success_rate: float) -> str:
        """Generate HTML portfolio"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.user_profile.get('name', 'Portfolio')}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }}
                .stat-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .projects {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    margin-top: 20px;
                }}
                .project-card {{
                    border-left: 4px solid #667eea;
                    padding: 20px;
                    margin: 20px 0;
                    background: #f9f9f9;
                }}
                .skill-tag {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 5px 15px;
                    margin: 5px;
                    border-radius: 20px;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{self.user_profile.get('name', 'Professional Freelancer')}</h1>
                <h2>{self.user_profile.get('title', 'Full-Stack Developer')}</h2>
                <p>{self.user_profile.get('bio', 'Experienced freelance professional')}</p>
            </div>

            <div class="stats">
                <div class="stat-card">
                    <h3>📊 Success Rate</h3>
                    <h2>{success_rate:.1f}%</h2>
                </div>
                <div class="stat-card">
                    <h3>💼 Projects</h3>
                    <h2>{len(self.project_history)}</h2>
                </div>
                <div class="stat-card">
                    <h3>💰 Total Earned</h3>
                    <h2>${total_value:,.0f}</h2>
                </div>
                <div class="stat-card">
                    <h3>⏱️ Experience</h3>
                    <h2>{self.user_profile.get('years_experience', 3)} years</h2>
                </div>
            </div>

            <div class="projects">
                <h2>Skills</h2>
                <div>
                    {''.join([f'<span class="skill-tag">{skill}</span>' for skill in skills[:15]])}
                </div>

                <h2 style="margin-top: 40px;">Recent Projects</h2>
                {''.join([self._format_project_html(p) for p in self.project_history[:5]])}
            </div>
        </body>
        </html>
        """
        return html

    def _format_project_html(self, project: Dict) -> str:
        """Format single project as HTML"""
        return f"""
        <div class="project-card">
            <h3>{project.get('title', 'Project')}</h3>
            <p>{project.get('description', 'No description')}</p>
            <p><strong>Budget:</strong> ${project.get('budget', 0):,.0f}</p>
            <p><strong>Skills:</strong> {', '.join(project.get('skills', []))}</p>
            <p><strong>Status:</strong> {'✅ Successful' if project.get('success', True) else '⚠️ Completed'}</p>
        </div>
        """

    def _generate_markdown_portfolio(self, skills: List[str],
                                     total_value: float, success_rate: float) -> str:
        """Generate Markdown portfolio"""
        md = f"""
# {self.user_profile.get('name', 'Professional Freelancer')}
## {self.user_profile.get('title', 'Full-Stack Developer')}

{self.user_profile.get('bio', 'Experienced freelance professional')}

---

## 📊 Statistics

- **Success Rate:** {success_rate:.1f}%
- **Projects Completed:** {len(self.project_history)}
- **Total Earned:** ${total_value:,.0f}
- **Experience:** {self.user_profile.get('years_experience', 3)} years

---

## 💻 Skills

{', '.join([f'`{skill}`' for skill in skills[:20]])}

---

## 📁 Recent Projects

{''.join([self._format_project_markdown(p) for p in self.project_history[:10]])}

---

## 📧 Contact

Ready to work together? Let's discuss your project!

- **Email:** {self.user_profile.get('email', 'contact@example.com')}
- **Location:** {self.user_profile.get('location', 'Remote')}
"""
        return md

    def _format_project_markdown(self, project: Dict) -> str:
        """Format single project as Markdown"""
        return f"""
### {project.get('title', 'Project')}

{project.get('description', 'No description')}

- **Budget:** ${project.get('budget', 0):,.0f}
- **Skills:** {', '.join(project.get('skills', []))}
- **Status:** {'✅ Successful' if project.get('success', True) else '⚠️ Completed'}

---

"""

    def _extract_testimonials(self) -> List[str]:
        """Extract testimonials from project history"""
        testimonials = []
        for project in self.project_history:
            if 'testimonial' in project:
                testimonials.append(project['testimonial'])
        return testimonials


# ============================================================================
# NOTIFICATION SYSTEM
# ============================================================================

class NotificationSystem:
    """Multi-channel notification system"""

    def __init__(self):
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', 587)),
            'email_user': os.getenv('EMAIL_USER', ''),
            'email_password': os.getenv('EMAIL_PASSWORD', ''),
            'from_email': os.getenv('FROM_EMAIL', ''),
        }

        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL', '')

    async def send_notification(self, channel: NotificationChannel,
                               title: str, message: str,
                               data: Dict = None) -> bool:
        """
        Send notification through specified channel

        Args:
            channel: Notification channel
            title: Notification title
            message: Notification message
            data: Additional data

        Returns:
            True if sent successfully
        """
        try:
            if channel == NotificationChannel.EMAIL:
                return await self._send_email(title, message, data)
            elif channel == NotificationChannel.SLACK:
                return await self._send_slack(title, message, data)
            elif channel == NotificationChannel.DISCORD:
                return await self._send_discord(title, message, data)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(title, message, data)
            elif channel == NotificationChannel.CONSOLE:
                print(f"\n{'='*60}")
                print(f"📢 {title}")
                print(f"{'-'*60}")
                print(message)
                if data:
                    print(f"\nData: {json.dumps(data, indent=2)}")
                print(f"{'='*60}\n")
                return True
            else:
                print(f"⚠️ Unknown notification channel: {channel}")
                return False

        except Exception as e:
            print(f"❌ Notification failed ({channel}): {e}")
            return False

    async def _send_email(self, title: str, message: str, data: Dict = None) -> bool:
        """Send email notification"""
        if not self.email_config['email_user']:
            print("⚠️ Email not configured")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = title
            msg['From'] = self.email_config['from_email']
            msg['To'] = self.email_config['email_user']

            # Create HTML content
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #667eea;">{title}</h2>
                <p>{message}</p>
                {f'<pre>{json.dumps(data, indent=2)}</pre>' if data else ''}
                <hr>
                <p style="color: #666; font-size: 12px;">
                    Sent by Freelance MCP Server
                </p>
            </body>
            </html>
            """

            part = MIMEText(html_content, 'html')
            msg.attach(part)

            with smtplib.SMTP(self.email_config['smtp_server'],
                            self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['email_user'],
                           self.email_config['email_password'])
                server.send_message(msg)

            print(f"✅ Email sent: {title}")
            return True

        except Exception as e:
            print(f"❌ Email failed: {e}")
            return False

    async def _send_slack(self, title: str, message: str, data: Dict = None) -> bool:
        """Send Slack notification"""
        if not self.slack_webhook:
            print("⚠️ Slack webhook not configured")
            return False

        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": title
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                }
            ]
        }

        if data:
            payload["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{json.dumps(data, indent=2)}```"
                }
            })

        async with aiohttp.ClientSession() as session:
            async with session.post(self.slack_webhook, json=payload) as response:
                if response.status == 200:
                    print(f"✅ Slack notification sent: {title}")
                    return True
                else:
                    print(f"❌ Slack failed: {response.status}")
                    return False

    async def _send_discord(self, title: str, message: str, data: Dict = None) -> bool:
        """Send Discord notification"""
        if not self.discord_webhook:
            print("⚠️ Discord webhook not configured")
            return False

        embed = {
            "embeds": [{
                "title": title,
                "description": message,
                "color": 6697130,  # Purple
                "timestamp": datetime.now().isoformat()
            }]
        }

        if data:
            embed["embeds"][0]["fields"] = [
                {"name": "Details", "value": f"```json\n{json.dumps(data, indent=2)}\n```"}
            ]

        async with aiohttp.ClientSession() as session:
            async with session.post(self.discord_webhook, json=embed) as response:
                if response.status == 204:
                    print(f"✅ Discord notification sent: {title}")
                    return True
                else:
                    print(f"❌ Discord failed: {response.status}")
                    return False

    async def _send_webhook(self, title: str, message: str, data: Dict = None) -> bool:
        """Send custom webhook notification"""
        webhook_url = os.getenv('CUSTOM_WEBHOOK_URL', '')

        if not webhook_url:
            print("⚠️ Custom webhook not configured")
            return False

        payload = {
            "title": title,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status == 200:
                    print(f"✅ Webhook notification sent: {title}")
                    return True
                else:
                    print(f"❌ Webhook failed: {response.status}")
                    return False

    async def notify_new_gig(self, gig: Dict, recommendation_score: float = None):
        """Send notification about new matching gig"""
        title = f"🎯 New Gig Match: {gig['title']}"
        message = f"""
        Platform: {gig['platform']}
        Budget: {gig.get('budget', 'Not specified')}
        Skills: {', '.join(gig.get('skills_required', [])[:5])}
        {f'Match Score: {recommendation_score*100:.0f}%' if recommendation_score else ''}

        {gig.get('description', '')[:200]}...
        """

        # Send to all configured channels
        await asyncio.gather(
            self.send_notification(NotificationChannel.CONSOLE, title, message, gig),
            self.send_notification(NotificationChannel.EMAIL, title, message, gig),
            self.send_notification(NotificationChannel.SLACK, title, message, gig),
            self.send_notification(NotificationChannel.DISCORD, title, message, gig),
        )

    async def notify_bid_submitted(self, bid: Dict):
        """Notify when auto-bid is submitted"""
        title = f"✅ Bid Submitted: {bid['gig_title']}"
        message = f"""
        Platform: {bid['platform']}
        Bid Amount: ${bid['bid_amount']}
        Status: {bid['status']}
        """

        await self.send_notification(NotificationChannel.CONSOLE, title, message, bid)


# Test functions
if __name__ == "__main__":
    print("✅ Automation module loaded")
    print("Available features:")
    print("  - AutoBiddingAgent")
    print("  - PortfolioGenerator")
    print("  - NotificationSystem")
