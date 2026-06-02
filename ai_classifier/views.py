from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from .classifier import classify_incident


@login_required
@require_POST
def classify_view(request):
    """AJAX endpoint to classify an incident in real-time."""
    try:
        data = json.loads(request.body)
        title = data.get('title', '')
        description = data.get('description', '')

        if not title and not description:
            return JsonResponse({'error': 'Titre ou description requis'}, status=400)

        result = classify_incident(title, description)
        return JsonResponse({'success': True, 'result': result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
