import google.generativeai as genai
from django.conf import settings
from .models import Product

def get_product_context():
    """
    Fetch all products and format them as a context string for the AI.
    """
    products = Product.objects.all()
    context = "Here are the products currently available in WEMISI store:\n\n"
    for p in products:
        context += f"- Product: {p.name}\n"
        context += f"  Price: Ksh {p.price}\n"
        context += f"  Category: {p.category.name}\n"
        context += f"  Description: {p.description or 'No description available.'}\n\n"
    return context

def get_ai_response(user_message, conversation_history=[]):
    """
    Send the user message and product context to Gemini and return the response.
    """
    api_key = getattr(settings, 'GOOGLE_API_KEY', None)
    
    if not api_key:
        return "AI Assistant is currently in demo mode. Please configure GOOGLE_API_KEY in settings.py to enable full functionality."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    product_context = get_product_context()
    
    system_prompt = (
        "You are the WEMISI Technical Stone Assistant. You help customers with questions about "
        "Marble, Granite, and Custom Fencing. You are polite, professional, and knowledgeable. "
        "Use the following product list to answer questions. If a product is not listed, "
        "politely inform the customer that we might not have it in stock but can source it if they contact us.\n\n"
        f"{product_context}\n"
        "Always recommend WhatsApp for final ordering or custom measurements."
    )
    
    # Simple history management
    full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAI:"
    
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def get_recommendations(target_product):
    """
    Use Gemini to suggest 4 products that complement the target_product.
    Returns a list of Product instances.
    """
    api_key = getattr(settings, 'GOOGLE_API_KEY', None)
    if not api_key:
        # Fallback: Just return 4 other products from the same category
        return Product.objects.filter(category=target_product.category).exclude(id=target_product.id)[:4]

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    all_products = Product.objects.exclude(id=target_product.id)
    catalog_summary = "\n".join([f"ID: {p.id}, Name: {p.name}, Category: {p.category.name}" for p in all_products])
    
    prompt = (
        f"The user is looking at: {target_product.name} (Category: {target_product.category.name}).\n"
        f"Based on the following catalog, pick up to 4 products that would complement this item for a construction project:\n\n"
        f"{catalog_summary}\n\n"
        "Return ONLY the product IDs as a comma-separated list, e.g., '1,2,3'. No other text."
    )
    
    try:
        response = model.generate_content(prompt)
        # Extract IDs from response
        ids = [int(i.strip()) for i in response.text.split(',') if i.strip().isdigit()]
        return Product.objects.filter(id__in=ids)
    except Exception:
        # Fallback on error
        return Product.objects.filter(category=target_product.category).exclude(id=target_product.id)[:4]

def generate_blog_content(topic):
    """
    Use Gemini to generate a high-quality blog post draft based on a topic.
    """
    api_key = getattr(settings, 'GOOGLE_API_KEY', None)
    if not api_key:
        return "AI is in Demo Mode. Please set GOOGLE_API_KEY to generate live content."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = (
        f"Write a professional, engaging blog post about: {topic}.\n"
        "The blog is for 'WEMISI', a premium building materials store specializing in Marble, Granite, and Fencing.\n"
        "Structure the post with HTML tags (h2, p, ul, li) suitable for a rich text editor.\n"
        "Include a concluding call to action to visit the Wemisi showroom or shop online."
    )
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating content: {str(e)}"
