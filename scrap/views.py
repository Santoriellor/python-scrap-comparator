from django.db import transaction
from django.shortcuts import render
from django.template.loader import render_to_string
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

import json

from .scrap import fetch_html, scrap_migros, scrap_coop, scrap_aldi, scrap_lidl
from .models import Search, Product

# Create your views here.

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib import messages
from django.contrib.messages import get_messages
from django.db import transaction
from django.views.decorators.csrf import ensure_csrf_cookie

# list of the different stores
sources = ["coop", "migros", "aldi", "lidl"]

@ensure_csrf_cookie
@transaction.atomic
def fetch_data(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    # Retrieve data from the POST request
    search_id = request.POST.get('searchId')
    source = request.POST.get('source')
    request_type = request.POST.get('requestType', 'new')  # Expecting 'new', 'update', or 'view'

    # Validate the source parameter
    if not source:
        return JsonResponse({'error': 'Source is required'}, status=400)
    
    # Retrieve the Search instance if provided
    search = None
    if search_id:
        try:
            search = Search.objects.get(id=search_id)
        except Search.DoesNotExist:
            return JsonResponse({'error': f'Search ID {search_id} does not exist'}, status=404)
        
    # Handle 'view' mode
    if request_type == 'view':
        if not search:
            # Retrieve the latest search object from the database
            search = Search.objects.order_by('-created_at').first()
        
        # Call the get_product_by_search_id helper function
        response = get_product_by_search_id(search.id, source)            

        # Check if the response contains an 'error' field (i.e., if there's an issue with the data)
        if response.status_code == 200:
            response_data = json.loads(response.content)
            products = response_data.get('products', [])
            error_message = response_data.get('error', '')

            # If no products are found, set a specific error message
            if not products:
                error_message = f"No products found for source {source}"

            # Prepare the data for rendering
            data = {
                'products': products,
                'error_message': error_message
            }

            # Render the HTML for the product list
            html = render_to_string('scrap/products_list.html', {
                'search': search,
                'source': source,
                'data': data
            })

            # Return the rendered HTML in a JSON response
            return JsonResponse({'html': html, 'error': ''})
        else:
            return JsonResponse({'error': 'Error loading products'}, status=500)
    
    # Handle 'new' or 'update' modes
    if request_type in ['new', 'update']:
        # Ensure the search instance exists or create a new one
        if not search:
            query = request.POST.get('query', '').strip().lower()  # Normalize query to lowercase and remove leading/trailing spaces
            if not query:
                messages.info(request, "No query. Please initiate a search.")
                return JsonResponse({'error': 'Search query is required for a new search'}, status=400)
            
            # Create or update the Search object
            search, created = Search.objects.get_or_create(query=query)
            
            # Update created_at if the object already exists
            if not created:
                Search.objects.filter(id=search.id).update(created_at=timezone.now())
            else:
                print("Search was newly created.")
        else :
            Search.objects.filter(id=search.id).update(created_at=timezone.now())
        
        # Scrape data for the given source    
        try:
            if source == 'coop':
                soup = fetch_html(f"https://www.coop.ch/fr/search/?text={search.query}")
                products_data = scrap_coop(soup)
            elif source == 'migros':
                soup = fetch_html(f"https://www.migros.ch/fr/search?query={search.query}")
                products_data = scrap_migros(soup)
            elif source == 'aldi':
                soup = fetch_html(f"https://www.aldi-now.ch/fr/search?q={search.query}")
                products_data = scrap_aldi(soup)
            elif source == 'lidl':
                soup = fetch_html(f"https://sortiment.lidl.ch/fr/catalogsearch/result/?q={search.query}")
                products_data = scrap_lidl(soup)
            else:
                return JsonResponse({'error': f'Unknown source: {source}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f"Error scraping data from {source}: {str(e)}"}, status=500)

        # Save scraped products linked to the search
        try:
            # Remove existing products for this source and search
            Product.objects.filter(search=search, product_from=source).delete()
            
            if isinstance(products_data, list) and all(isinstance(p, dict) for p in products_data):
                Product.objects.bulk_create([
                    Product(
                        name=product_data['product_name'],
                        img_src=product_data.get('image_src'),
                        img_srcset=product_data.get('image_srcset'),
                        price=product_data.get('product_price', 0.0),
                        product_from=source,
                        search=search
                    )
                    for product_data in products_data
                ])
            else:
                return JsonResponse({'error': 'Invalid product data format'}, status=500)
        except Exception as e:
            return JsonResponse({'error': f"Error saving product data: {str(e)}"}, status=500)
    
        # Render HTML for the newly fetched data
        products = Product.objects.filter(search=search, product_from=source)
        data = {
            'products': products,
            'error_message': '' if products.exists() else f"No products found for source {source}."
        }
        
        html = render_to_string('scrap/products_list.html', {
                    'search': search,
                    'source': source,
                    'data': data
                })

        # Return JSON response
        return JsonResponse({'html': html, 'error': ''})
    
    # Default response for invalid conditions
    return JsonResponse({'error': 'Invalid request type or missing parameters'}, status=400)

def get_product_by_search_id(search_id, source):
    """ helper function for viewing existing search products

    Args:
        search_id (Search model key: int): _description_
        source (string): _description_

    Returns:
        jsonresponse: a json response containing an 'products' dictionnary and an 'error' fields
    """
    try:
        products = Product.objects.filter(search=search_id, product_from=source)
        
        # Serialize the QuerySet into a JSON-serializable format
        serialized_products = list(products.values('id', 'name', 'img_src', 'img_srcset', 'price', 'product_from'))
        
        return JsonResponse({'products': serialized_products, 'error': ''})
    except Exception as e:
        return JsonResponse({'error': f"Error loading existing search: {str(e)}"}, status=500)

def get_search_history(request):
    # Retrieve the latest search object from the database
    latest_search = Search.objects.order_by('-created_at').first()
    
    # Retrieve all search history, ordered by the most recent
    search_history = Search.objects.all().order_by('-created_at')[:10]  # Limit to the last 10 searches
    
    search_data = []
    
    for search in search_history:
        # Add most_recent field to indicate whether this search is the most recent one
        is_most_recent = (search.id == latest_search.id) if latest_search else False
        
        # Format the `created_at` date
        formatted_created_at = search.created_at.strftime('%d/%m/%Y %H:%M')

        search_data.append({
            'id': search.id,
            'query': search.query,
            'created_at': formatted_created_at,  # Pass the formatted date
            'most_recent': is_most_recent  # Add the most_recent field
        })
    
    return JsonResponse({'search_history': search_data})

def get_search(request):
    search_id = request.POST.get('searchId')
    if not search_id:
        return JsonResponse({'error': 'Search ID is required'}, status=400)

    try:
        search = Search.objects.get(id=search_id)
        return JsonResponse({'query': search.query})
    except Search.DoesNotExist:
        return JsonResponse({'error': f'Search ID {search_id} does not exist'}, status=404)
        
def delete_history_result(request):
    if request.method == 'DELETE':
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            search_id = body.get('searchId')

            # Get the search entry from the database
            search_entry = Search.objects.get(id=search_id)
            # Delete the search entry
            search_entry.delete()

            return JsonResponse({'success': True})
        
        except Search.DoesNotExist:
            return JsonResponse({'success': False, 'error': f'Search entry not found for {search_id}'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON format'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid HTTP method'}, status=405)

@ensure_csrf_cookie
def index(request):
    # Retrieve the latest search object from the database
    latest_search = Search.objects.order_by('-created_at').first()

    # Dictionary to store products and errors for each source
    store_data = {source: {'products': '', 'error_message': '' } for source in sources}

    if latest_search:
        for source in sources:
            # Call get_product_by_search_id for each source
            response = get_product_by_search_id(latest_search.id, source)
            if isinstance(response, JsonResponse):
                # Access the data passed into the JsonResponse
                response_data = json.loads(response.content)  # Use response.content to decode JSON data
                store_data[source]['products'] = response_data.get('products', '')
                store_data[source]['error_message'] = response_data.get('error', '')
            else:
                store_data[source]['error_message'] = "An unexpected error occurred (data is not JSON)."
    else:
        # No search history is available
        if not latest_search and not messages.get_messages(request):
            messages.info(request, "No search history available. Please initiate a search.")
        for source in sources:
            store_data[source]['products'] = []
            store_data[source]['error_message'] = f"No data available for {source}"
            
    # Render the template with all source HTML and error messages
    return render(request, 'scrap/store_list.html', {
        'search': latest_search if latest_search else None,
        'store_data': store_data  # Contains HTML and error messages for each source
    })