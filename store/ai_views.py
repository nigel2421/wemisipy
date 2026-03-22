from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .ai_utils import get_ai_response, generate_blog_content

@csrf_exempt
def ai_chat_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            history = data.get('history', [])
            
            response_text = get_ai_response(user_message, history)
            
            return JsonResponse({'response': response_text})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def ai_generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            topic = data.get('topic', '')
            if not topic:
                return JsonResponse({'error': 'No topic provided'}, status=400)
            
            content = generate_blog_content(topic)
            return JsonResponse({'content': content})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
