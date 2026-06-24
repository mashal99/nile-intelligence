import anthropic
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from apps.market.models import MarketInsight, MarketSnapshot
from apps.properties.models import Area, Developer


class AIInsightsService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = 'claude-sonnet-4-6'

    def _call(self, system: str, user: str, max_tokens: int = 1500) -> tuple[str, int]:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{'role': 'user', 'content': user}],
        )
        return message.content[0].text, message.usage.input_tokens + message.usage.output_tokens

    def generate_weekly_market_summary(self, area_slug: str = None) -> MarketInsight:
        from apps.market.services import MarketAnalyticsService

        heatmap = MarketAnalyticsService.get_area_heatmap()
        rankings = MarketAnalyticsService.get_developer_rankings(10)
        inventory = MarketAnalyticsService.get_inventory_summary()

        if area_slug:
            trend = MarketAnalyticsService.get_price_trend(area_slug, 'apartment', 30)
        else:
            trend = []

        market_data = {
            'heatmap': heatmap[:10],
            'developer_rankings': rankings,
            'inventory': inventory,
            'price_trend': trend,
        }

        import json
        system_prompt = """You are a senior real estate market analyst specializing in the Egyptian property market.
You produce concise, data-driven market intelligence reports for real estate professionals.
Write in clear English. Be specific with numbers. Focus on actionable insights.
Format: executive summary (2-3 sentences), key trends (bullet points), outlook (1 paragraph)."""

        user_prompt = f"""Analyze this Egyptian real estate market data for the past week and produce a market intelligence report:

{json.dumps(market_data, indent=2, default=str)}

Include:
1. Executive summary
2. Top 3 market trends
3. Best performing areas by price/sqm
4. Developer activity highlights
5. Investment outlook
"""

        text, tokens = self._call(system_prompt, user_prompt, max_tokens=2000)

        area = Area.objects.filter(slug=area_slug).first() if area_slug else None

        title_suffix = f' - {area.name}' if area else ''
        return MarketInsight.objects.create(
            insight_type=MarketInsight.InsightType.WEEKLY_SUMMARY,
            title=f'Weekly Market Report{title_suffix} - {timezone.now().strftime("%B %d, %Y")}',
            summary=text[:500],
            full_analysis=text,
            area=area,
            ai_model=self.model,
            tokens_used=tokens,
            valid_until=timezone.now() + timedelta(days=7),
        )

    def analyze_price_movement(self, area_slug: str, property_type: str) -> str:
        from apps.market.services import MarketAnalyticsService

        trend_90 = MarketAnalyticsService.get_price_trend(area_slug, property_type, 90)
        trend_30 = MarketAnalyticsService.get_price_trend(area_slug, property_type, 30)

        import json
        system_prompt = """You are a real estate economist. Explain price movements in plain language
for real estate investors and brokers in the Egyptian market. Be data-driven and specific."""

        user_prompt = f"""Explain the price movement for {property_type}s in {area_slug} based on this data:

Last 90 days: {json.dumps(trend_90[-10:], default=str)}
Last 30 days: {json.dumps(trend_30[-5:], default=str)}

Explain: What happened? Why likely happened? What should investors expect?"""

        text, _ = self._call(system_prompt, user_prompt, max_tokens=800)
        return text

    def identify_investment_opportunities(self, budget_egp: float, preferences: dict) -> str:
        from apps.market.services import MarketAnalyticsService

        heatmap = MarketAnalyticsService.get_area_heatmap()
        affordable_areas = [a for a in heatmap if a.get('avg_psm', 0) > 0]

        import json
        system_prompt = """You are an Egyptian real estate investment advisor.
Identify concrete investment opportunities based on market data.
Be specific about locations, expected returns, and risks."""

        user_prompt = f"""Find investment opportunities for a budget of {budget_egp:,.0f} EGP.

Investor preferences: {json.dumps(preferences)}

Current market by area (price per sqm):
{json.dumps(affordable_areas[:15], indent=2, default=str)}

Provide:
1. Top 3 recommended areas with justification
2. Expected property type and specs for budget
3. Potential ROI estimate
4. Risks to consider"""

        text, _ = self._call(system_prompt, user_prompt, max_tokens=1200)
        return text

    def generate_executive_summary(self, report_data: dict) -> str:
        import json
        system_prompt = """You are a C-suite advisor producing board-level real estate intelligence.
Write in concise, executive prose. Lead with the most important finding."""

        user_prompt = f"""Generate a 200-word executive summary of this real estate report:

{json.dumps(report_data, indent=2, default=str)}"""

        text, _ = self._call(system_prompt, user_prompt, max_tokens=400)
        return text

    def answer_market_question(self, question: str, context: dict = None) -> str:
        import json
        system_prompt = """You are a knowledgeable Egyptian real estate market expert.
Answer questions accurately using the provided market context.
If data is insufficient, say so explicitly rather than guessing."""

        ctx_str = f"\n\nMarket context: {json.dumps(context, default=str)}" if context else ""
        text, _ = self._call(system_prompt, f"{question}{ctx_str}", max_tokens=1000)
        return text
