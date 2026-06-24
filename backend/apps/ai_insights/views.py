from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers

from .services import AIInsightsService
from core.permissions import SubscriptionRequired


class GenerateInsightView(APIView):
    permission_classes = [SubscriptionRequired('professional')]

    def post(self, request):
        insight_type = request.data.get('type', 'weekly_summary')
        area_slug = request.data.get('area_slug')

        svc = AIInsightsService()
        try:
            if insight_type == 'weekly_summary':
                insight = svc.generate_weekly_market_summary(area_slug)
                return Response({
                    'title': insight.title,
                    'summary': insight.summary,
                    'full_analysis': insight.full_analysis,
                })
            elif insight_type == 'price_movement':
                property_type = request.data.get('property_type', 'apartment')
                if not area_slug:
                    return Response({'detail': 'area_slug required'}, status=status.HTTP_400_BAD_REQUEST)
                analysis = svc.analyze_price_movement(area_slug, property_type)
                return Response({'analysis': analysis})
            elif insight_type == 'investment_opportunities':
                budget = request.data.get('budget_egp')
                if not budget:
                    return Response({'detail': 'budget_egp required'}, status=status.HTTP_400_BAD_REQUEST)
                preferences = request.data.get('preferences', {})
                result = svc.identify_investment_opportunities(float(budget), preferences)
                return Response({'opportunities': result})
            else:
                return Response({'detail': 'Unknown insight type.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AskMarketQuestionView(APIView):
    permission_classes = [SubscriptionRequired('professional')]

    def post(self, request):
        question = request.data.get('question', '').strip()
        if not question:
            return Response({'detail': 'question is required'}, status=status.HTTP_400_BAD_REQUEST)

        context = request.data.get('context', {})
        svc = AIInsightsService()
        answer = svc.answer_market_question(question, context)
        return Response({'answer': answer})
