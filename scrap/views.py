from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

import json
import logging

from .scrap import fetch_html, scrap_migros, scrap_coop, scrap_aldi
from .models import Search

# logger = logging.getLogger(__name__)

# Create your views here.
@ensure_csrf_cookie
@transaction.atomic
def fetch_coop_data(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        search_id = request.POST.get('searchId')

        # Check if the query is empty
        if not query:
            return HttpResponse('Please provide a search query for Coop', status=400)
            
            # messages.error(request, 'Please provide a search query for Coop')
            # return redirect(request.META.get('HTTP_REFERER', 'index'))  # Redirect to the index page
        
        data_from = 'coop'
        # Get html content from the Coop search page
        soup = fetch_html(f"https://www.coop.ch/fr/search/?text={query}")
        # Scrape searched products
        scraped_data = scrap_coop(soup)

        # Use get_or_create to retrieve or create the Search object
        if search_id:
            search = get_object_or_404(Search.objects.select_for_update(), id=search_id)
            search.created_at = timezone.now()
        else:
            search, created = Search.objects.get_or_create(
                query=query
            )
            if not created:
                search.created_at = timezone.now()

        # render the search results with the template
        html = render_to_string('scrap/products.html', {
            'products': scraped_data,
            })

        search.products_from_coop = html
        search.save()

        # Return the html to the ajax function
        return HttpResponse(html)
    else:
        return HttpResponse('Invalid request method', status=405)


@ensure_csrf_cookie
@transaction.atomic
def fetch_migros_data(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        search_id = request.POST.get('searchId')

        # Check if the query is empty
        if not query:
            return HttpResponse('Please provide a search query for Migros', status=400)
            
        data_from = 'migros'
        # Get html content from the Migros search page
        soup = fetch_html(f"https://www.migros.ch/fr/search?query={query}")
        # Scrape searched products
        scraped_data = scrap_migros(soup)
                
        # Use get_or_create to retrieve or create the Search object
        if search_id:
            search = get_object_or_404(Search.objects.select_for_update(), id=search_id)
            search.created_at = timezone.now()
        else:
            search, created = Search.objects.get_or_create(
                query=query
            )
            if not created:
                search.created_at = timezone.now()

        # render the search results with the template
        html = render_to_string('scrap/products.html', {
            'products': scraped_data,
            })

        search.products_from_migros = html
        search.save()

        # Return the html to the ajax function
        return HttpResponse(html)
    else:
        return HttpResponse('Invalid request method', status=405)


@ensure_csrf_cookie
@transaction.atomic
def fetch_aldi_data(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        search_id = request.POST.get('searchId')

        # Check if the query is empty
        if not query:
            return HttpResponse('Please provide a search query for Aldi', status=400)
        
        data_from = 'aldi'
        # Get html content from the Aldi search page
        soup = fetch_html(f"https://www.aldi-now.ch/fr/search?q={query}")
        # Scrap searched products
        scraped_data = scrap_aldi(soup)
        
        # Use get_or_create to retrieve or create the Search object
        if search_id:
            search = get_object_or_404(Search.objects.select_for_update(), id=search_id)
            search.created_at = timezone.now()
        else:
            search, created = Search.objects.get_or_create(
                query=query,
            )
            if not created:
                search.created_at = timezone.now()

        # render the search results with the template
        html = render_to_string('scrap/products.html', {
            'products': scraped_data,
            })

        search.products_from_aldi = html
        search.save()

        # Return the html to the ajax function
        return HttpResponse(html)
    else:
        return HttpResponse('Invalid request method', status=405)


def view_history_result(request):
    query_id = request.GET.get('searchId')

    # Retrieve the Search object based on the query id
    search_object = get_object_or_404(Search, id=query_id)

    # Create a list of HTML contents from different sources
    products = [
        search_object.products_from_coop,
        search_object.products_from_migros,
        search_object.products_from_aldi
    ]

    # Return the list as a JSON response
    return JsonResponse({
        'products': products,
        'query': search_object.query,
        'searchId': search_object.id
        })   


def get_query_by_search_id(request):
    search_id = request.GET.get('searchId')
    if search_id:
        search_object = get_object_or_404(Search, id=search_id)
        return JsonResponse({'query': search_object.query})
    else:
        return JsonResponse({'error': 'Invalid search ID'}, status=400)
    

def get_search_history(request):
    search_history = Search.objects.all().order_by('-created_at')[:10]  # Assuming you want to limit to the last 10 searches
    search_data = [{'id': search.id, 'query': search.query, 'created_at': search.created_at.strftime('%d/%m/%Y %H:%M')} for search in search_history]
    return JsonResponse({'search_history': search_data})
    

@ensure_csrf_cookie
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


def index(request):
    # Retrieve the latest search object from the database
    latest_search = Search.objects.order_by('-created_at').first()

    # Extract the scraped data from the latest search
    if latest_search:
        all_products = {
            'coop': latest_search.products_from_coop,
            'migros': latest_search.products_from_migros,
            'aldi': latest_search.products_from_aldi
        }
        # Render the template with the context
        return render(request, 'scrap/compare.html', {
            'query': latest_search.query,
            'searchId': latest_search.id,
            'all_products': all_products
    })
    else:
        # If no search history is available, set scraped_data to an empty dictionary
        all_products = {}

        # Render the template with the context
        return render(request, 'scrap/compare.html', {
            'all_products': all_products
        })