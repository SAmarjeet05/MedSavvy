import os
import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt

def whatsapp_webhook(request):
    VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', 'Amarjeet')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')

    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return HttpResponse(challenge, status=200)
        return HttpResponse('Verification failed', status=403)

    if request.method == 'POST':
        try:
            print('POST received at webhook')
            data = json.loads(request.body.decode('utf-8'))
            print('Request data:', data)
            # WhatsApp webhook structure
            entry = data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [])
            if messages:
                message = messages[0]
                text = message.get('text', {}).get('body', '').strip()
                from_number = message.get('from')
                print(f'Received message: {text} from {from_number}')

                # Check for required env vars
                if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
                    print('Missing ACCESS_TOKEN or PHONE_NUMBER_ID')
                    return JsonResponse({'error': 'Server misconfiguration'}, status=500)

                # Reply to any message for testing
                reply = f"You said: {text}\nHello, Welcome to MedSavvy! How may I help you?"
                url = f'https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages'
                headers = {
                    'Authorization': f'Bearer {ACCESS_TOKEN}',
                    'Content-Type': 'application/json'
                }
                payload = {
                    'messaging_product': 'whatsapp',
                    'to': from_number,
                    'type': 'text',
                    'text': {'body': reply}
                }
                try:
                    resp = requests.post(url, headers=headers, json=payload, timeout=10)
                    print('WhatsApp API response:', resp.status_code, resp.text)
                    if resp.status_code >= 400:
                        print('Error sending message to WhatsApp:', resp.text)
                except Exception as api_exc:
                    print('Exception sending message to WhatsApp:', str(api_exc))
            return JsonResponse({'status': 'received'})
        except Exception as e:
            print('Error in webhook:', str(e))
            return JsonResponse({'error': str(e)}, status=400)
    return HttpResponse(status=405)


