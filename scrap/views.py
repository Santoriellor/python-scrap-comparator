from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
import json

from .scrap import scrape_multiple_websites, scrap_migros, scrap_coop, scrap_aldi
from .models import Search

# Create your views here.
def search_products(request):
    query = request.GET.get('query')

    # Check if the query is empty
    if not query:
        messages.error(request, 'Please provide a search query')
        return redirect(request.META.get('HTTP_REFERER', 'index'))  # Redirect to the previous page
    
    # urls to scrap with the associated scrapping function
    urls_and_parsers = [
        (f"https://www.coop.ch/fr/search/?text={query}", scrap_coop),
        (f"https://www.migros.ch/fr/search?query={query}", scrap_migros),
        (f"https://www.aldi-now.ch/fr/search?q={query}", scrap_aldi)
    ]
    
    # Get searched products
    scraped_data = scrape_multiple_websites(urls_and_parsers)

    json_scraped_data = json.dumps(scraped_data)

    # Save the search query and its result to the database
    search = Search.objects.create(query=query, result=json_scraped_data)

    # Retrieve all Search objects from the database
    search_history = Search.objects.all()

    # Return the search results to the template
    return render(request, 'scrap/compare.html', {
        'query': query,
        'search_results': scraped_data,
        'search_history': search_history
        })


def view_history_result(request, query_id):
    # Retrieve the Search object based on the query id
    search_object = get_object_or_404(Search, id=query_id)
    # Parse the JSON string into a dictionary
    result_dict = json.loads(search_object.result)

    # Retrieve all Search objects from the database
    search_history = Search.objects.all()

    # Pass the search result to the template
    return render(request, 'scrap/compare.html', {
        'query': search_object.query,
        'search_results': result_dict,
        'search_history': search_history
        })


def update_history_result(request, query_id):
    # Retrieve the Search object based on the query id
    search_object = get_object_or_404(Search, id=query_id)
    query = search_object.query

    # urls to scrap with the associated scrapping function
    urls_and_parsers = [
        (f"https://www.coop.ch/fr/search/?text={query}", scrap_coop),
        (f"https://www.migros.ch/fr/search?query={query}", scrap_migros),
        (f"https://www.aldi-now.ch/fr/search?q={query}", scrap_aldi)
    ]

    # Get searched products
    scraped_data = scrape_multiple_websites(urls_and_parsers)

    json_scraped_data = json.dumps(scraped_data)

    # Update the existing Search object with the new result
    search_object.result = json_scraped_data
    search_object.created_at = timezone.now()  # Update the created_at field
    search_object.save()

    # Retrieve all Search objects from the database
    search_history = Search.objects.all()

    # Pass the search result to the template
    return render(request, 'scrap/compare.html', {
        'query': query,
        'search_results': scraped_data,
        'search_history': search_history
        })


def delete_history_result(request, search_id):
    try:
        # Get the search entry from the database
        search_entry = Search.objects.get(id=search_id)
        # Delete the search entry
        search_entry.delete()
        return JsonResponse({'success': True})
    except Search.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Search entry not found'})


def index(request):
    # urls to scrap with the associated scrapping function
    urls_and_parsers = [
        ("https://www.coop.ch/fr/search/?text=yaourt", scrap_coop),
        ("https://www.migros.ch/fr/search?query=yaourt", scrap_migros),
        ("https://www.aldi-now.ch/fr/search?q=yaourt", scrap_aldi)
    ]
    # Get searched products
    # scraped_data = scrape_multiple_websites(urls_and_parsers)
    
    # Save the scraped data to a JSON file
    # with open('scraped_data.json', 'w') as json_file:
    #     json.dump(scraped_data, json_file)

    # Load the scraped data from the JSON file
    with open('scraped_data.json', 'r') as json_file:
        scraped_data = json.load(json_file)

    # Retrieve all Search objects from the database
    search_history = Search.objects.all()

    # Render app template with context
    return render(request, 'scrap/compare.html', {
        'search_results': scraped_data,
        'search_history': search_history
        })