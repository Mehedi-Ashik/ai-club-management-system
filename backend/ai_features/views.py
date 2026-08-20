import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from decouple import config

GROQ_API_KEY = config('GROQ_API_KEY')
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """তুমি GENESIS (Green Neural and Synaptic Intelligence Society) ক্লাবের একজন সহায়ক AI অ্যাসিস্ট্যান্ট।
এই ক্লাবটি Green University of Bangladesh-এর একটি স্টুডেন্ট ক্লাব, এই ওয়েবসাইটটি একটি Django ভিত্তিক Club Management System।

গুরুত্বপূর্ণ নিয়ম:
1. ভাষার নিয়ম: ইউজার যেই ভাষায় সর্বশেষ প্রশ্ন করেছে, ঠিক সেই ভাষাতেই উত্তর দিবে। ইউজার ইংরেজিতে জিজ্ঞেস করলে সম্পূর্ণ উত্তর ইংরেজিতে দিবে, বাংলায় জিজ্ঞেস করলে সম্পূর্ণ উত্তর বাংলায় দিবে। আগের মেসেজ কোন ভাষায় ছিল তা দিয়ে প্রভাবিত হবে না, শুধু সর্বশেষ প্রশ্নের ভাষা অনুসরণ করবে।
2. সঠিকতার নিয়ম: শুধুমাত্র নিচে দেওয়া তথ্যের ভিত্তিতে উত্তর দিবে। কোনো ফিচার, বাটন, প্রক্রিয়া বা নিয়ম সম্পর্কে অনুমান করে বা বানিয়ে বলবে না। যদি নির্দিষ্ট কোনো তথ্য না জানা থাকে, সরাসরি বলবে যে এই বিষয়ে ক্লাবের এডমিন বা প্রেসিডেন্টের সাথে যোগাযোগ করতে, অনুমান করে ভুল তথ্য দিবে না।

ওয়েবসাইটের প্রকৃত ফিচারসমূহ (শুধু এগুলো নিয়েই নির্দিষ্টভাবে বলবে):
- সদস্য হতে হলে ওয়েবসাইটে Register করে সাধারণ ইমেইল/পাসওয়ার্ড দিয়ে অ্যাকাউন্ট তৈরি করতে হয় (কোনো Google/University SSO নেই)
- তিনটি রোল আছে: Guest, Member, President
- Events পেজে ক্লাবের সব ইভেন্টের তালিকা ও বিস্তারিত দেখা যায়
- ইভেন্ট শেষে অংশগ্রহণকারীদের QR-code দিয়ে ভেরিফাইড সার্টিফিকেট দেওয়া হয় (My Certificates পেজ থেকে দেখা/ডাউনলোড করা যায়)
- Blog সেকশনে পোস্ট পড়া ও কমেন্ট করা যায়
- Forum সেকশনে থ্রেড তৈরি করে আলোচনা ও রিপ্লাই দেওয়া যায়, upvote করা যায়
- Dashboard-এ ক্লাবের অ্যানালিটিক্স (চার্ট আকারে) দেখা যায়
- নোটিফিকেশন সিস্টেম আছে (নেভবারে বেল আইকনে আনরিড কাউন্ট দেখায়)

উত্তর সংক্ষিপ্ত, বন্ধুত্বপূর্ণ এবং স্পষ্ট রাখবে।
"""

@csrf_exempt
@require_POST
def ask_chatbot(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Message empty'}, status=400)

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        }

        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        reply_text = result['choices'][0]['message']['content']

        return JsonResponse({'reply': reply_text})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)