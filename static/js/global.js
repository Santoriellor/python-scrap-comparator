// GLOBAL FUNCTIONS
// function to get a cookie parameter
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Clear the message showed by the Django messages function
function clearDjangoMessages() {
    const messageContainer = document.getElementById('django-msg'); // Select the div by its ID
    if (messageContainer) {
        messageContainer.innerHTML = ''; // Clear the content of the div
    }
}

// Display placeholder for the store and hide the content
function displayPlaceholder(source) {
    $(`#${source}-placeholder`).css('display', 'flex');
    $(`#${source}-content`).hide();
}

// Update content with fetched data for the store and hide the placeholder
function updateContent(source, html) {
    $(`#${source}-placeholder`).hide();
    $(`#${source}-content`).html(html);  // Insert the fetched HTML content
    $(`#${source}-content`).show();
}

// function to update the store update-button
function refreshUpdateButton(searchId = null) {
    // Select all buttons with IDs starting with "btn-update-"
    const buttons = $('[id^="btn-update-"]');

    // Update the `data-search-id` attribute for each button
    buttons.each(function() {
        if (searchId) {
            $(this).attr('data-search-id', searchId);
            $(this).removeClass('disabled');
            $(this).text('Update');
        } else {
            $(this).addClass('disabled');
            $(this).text('No Search Available');
        }
    });
}

function disableSearch() {
    const searchButton = $('#button-search');
    const searchInput = $('#search-input'); 
    // Disable elements
    searchButton.prop('disabled', true);
    searchInput.prop('disabled', true);
    searchInput.val(''); // Clear the input text
    searchInput.attr('placeholder', 'Searching...');
}

function enableSearch() {
    const searchButton = $('#button-search');
    const searchInput = $('#search-input'); 
    // Disable elements
    searchButton.prop('disabled', false);
    searchInput.prop('disabled', false);
    searchInput.attr('placeholder', 'Search a product');
}

// function to update the title
async function refreshTitle(searchId) {
    try {
        const csrftoken = getCookie('csrftoken');
        const response = await $.ajax({
            url: `/get-search/`,
            method: 'POST',
            dataType: 'json',
            data: { searchId: searchId },
            headers: { 'X-CSRFToken': csrftoken },
        });

        if (response.query) {
            document.title = `Shop comparator - ${response.query}`; // Update the document's title
        } else {
            document.title = 'Shop comparator'; // Fallback title if query is not provided
        }
    } catch (error) {
        console.error('Error fetching title data:', error);
        document.title = 'Error'; // Optional: Indicate an error in the title
    }
}

// function to update the current search data
function refreshCurrentSearch(searchId) {
    $('#content').attr('data-current-search-id', searchId);
}

async function fetchAndUpdateContent(query = null, searchId = null, source, requestType = 'new') {
    displayPlaceholder(source);  // Show placeholder while data is fetched

    try {
        const csrftoken = getCookie('csrftoken');
        const response = await $.ajax({
            url: `/fetch-data/`,
            method: 'POST',
            dataType: 'json',
            data: {
                query: query,
                searchId: searchId,
                source: source,
                requestType: requestType
            },
            headers: { 'X-CSRFToken': csrftoken },
        });

        if (response.error) {
            // Display error message if an error is returned from the server
            console.error(`Error (ajax request) fetching data from ${source}: ${response.error}`);
            // Update content
            updateContent(source, "An error occured");  // Populate content
        } else {
            // Update content if HTML is returned successfully
            updateContent(source, response.html);
        }
    } catch (error) {
        console.error(`Error (try block) fetching data from ${source}:`, error);
        // Update content
        updateContent(source, "An error occured");  // Populate content
    }
}

// function to update the search history sidebar
function updateSearchHistorySidebar(searchId = null) {
    $.ajax({
        url: '/get-search-history/',
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            $('#search-history').empty();
            response.search_history.forEach(function(search_data) {
                // Determine if the button should be disabled
                let search_selected = false;
                if (searchId !== null && searchId === search_data.id) {
                    search_selected = true;
                    refreshUpdateButton(searchId);
                    refreshTitle(searchId);
                    refreshCurrentSearch(searchId);
                } else if (searchId === null && search_data.most_recent) {
                    search_selected = true;
                    refreshUpdateButton(search_data.id);
                    refreshTitle(search_data.id);
                    refreshCurrentSearch(search_data.id);
                }

                $('#search-history').append(`
                    <div
                        id="search-${search_data.id}"
                        class="mb-1 p-1 border rounded${search_selected ? ' bg-light border-dark' : ' border-light'}"
                    >
                        <p class="text-capitalize mb-1">
                            ${search_data.query}&nbsp;<i class="text-muted small">${search_data.created_at}</i>
                        </p>
                        <button
                            class="view-history-result btn btn-outline-success btn-sm"
                            style="font-size:0.7rem;"
                            data-search-id="${search_data.id}"${search_selected ? ' disabled' : ''}
                        >
                            View result
                        </button>
                        <button
                            class="update-history-result btn btn-outline-info btn-sm"
                            style="font-size:0.7rem;"
                            data-search-id="${search_data.id}"
                        >
                            Update
                        </button>
                        <button
                            class="delete-history-result btn btn-outline-danger btn-sm"
                            style="font-size:0.7rem;"
                            data-search-id="${search_data.id}"
                        >
                            Delete
                        </button>
                    </div>
                `);
            });
        },
        error: function(xhr, status, error) {
            console.error('Error fetching search history:', error);
        }
    });
}

// function to delete a search entry
function deleteSearchEntry(searchId) {
    $.ajax({
        url: '/delete-history-result/',
        type: 'DELETE',
        dataType: 'json',
        data: JSON.stringify({ searchId: searchId }),
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        success: async function(response) {
            if (response.success) {
                $('#search-' + searchId).remove();
                console.log('Search entry deleted:', searchId);
                
                // Check if the deleted search is currently displayed
                const currentSearchId = $('#content').data('current-search-id');
                if (currentSearchId === searchId) {
                    // If yes, load the most recent search
                    // Disabled the search input and button
                    disableSearch();
                    try {
                        await Promise.all([
                            fetchAndUpdateContent(null, null, 'coop', 'view'),
                            fetchAndUpdateContent(null, null, 'migros', 'view'),
                            fetchAndUpdateContent(null, null, 'aldi', 'view'),
                            fetchAndUpdateContent(null, null, 'lidl', 'view')
                        ]);
                    } catch (error) {
                        console.error('Error (try block) in delete-history-result:', error);
                    } finally {
                        enableSearch();
                    }
                }

                updateSearchHistorySidebar();

            } else {
                console.error('Error deleting search entry:', response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error deleting search entry:', error);
        }
    });
}


// Function to handle a query search
async function handleSearch() {
    const query = $('#search-input').val();
    clearDjangoMessages();

    // Disabled the search input and button
    disableSearch();
    try {
        await Promise.all([
            fetchAndUpdateContent(query, null, 'coop', 'new'),
            fetchAndUpdateContent(query, null, 'migros', 'new'),
            fetchAndUpdateContent(query, null, 'aldi', 'new'),
            fetchAndUpdateContent(query, null, 'lidl', 'new')
        ]);
        
        // Update history search sidebar
        updateSearchHistorySidebar();
        console.log('All data fetched');
    } catch (error) {
        console.error('Error (try block) fetching data:', error);
    } finally {
        enableSearch();
    }
}

// END OF GLOBAL FUNCTIONS

// EVENT LISTENERS
// Event listener for "search" button clicks
$('#button-search').on('click', handleSearch);

// Event listener for pressing Enter key in the search input
$('#search-input').on('keydown', function(event) {
    if (event.key === 'Enter') {
        handleSearch();
    }
});

// Event delegation for "update" from source button clicks
$(document).on('click', '.update-source-result', function() {
    const searchId = $(this).attr('data-search-id');
    const source = $(this).attr('data-source');
    console.log('click update source', searchId);
    fetchAndUpdateContent(null, searchId, source, 'update');
});

// Event delegation for "view result" button clicks
$(document).on('click', '.view-history-result', async function() {
    const searchId = $(this).data('search-id');
    console.log('click view', searchId);
    // Disabled the search input and button
    disableSearch();
    try {
        await Promise.all([
            fetchAndUpdateContent(null, searchId, 'coop', 'view'),
            fetchAndUpdateContent(null, searchId, 'migros', 'view'),
            fetchAndUpdateContent(null, searchId, 'aldi', 'view'),
            fetchAndUpdateContent(null, searchId, 'lidl', 'view')
        ]);
        updateSearchHistorySidebar(searchId);
    } catch (error) {
        console.error('Error (try block) in view-history-result:', error);
    } finally {
        enableSearch();
    }
});

// Event delegation for "update" button clicks
$(document).on('click', '.update-history-result', async function() {
    const searchId = $(this).data('search-id');
    console.log('click update', searchId);
    // Disabled the search input and button
    disableSearch();
    try {
        await Promise.all([
            fetchAndUpdateContent(null, searchId, 'coop', 'update'),
            fetchAndUpdateContent(null, searchId, 'migros', 'update'),
            fetchAndUpdateContent(null, searchId, 'aldi', 'update'),
            fetchAndUpdateContent(null, searchId, 'lidl', 'update')
        ]);
        updateSearchHistorySidebar(searchId);
    } catch (error) {
        console.error('Error (try block) in view-history-result:', error);
    } finally {
        enableSearch();
    }
});

// Event delegation for "delete" button clicks
$(document).on('click', '.delete-history-result', function() {
    const searchId = $(this).data('search-id');
    console.log('click delete', searchId);
    deleteSearchEntry(searchId);
});

// END OF EVENT LISTENERS

// update search history sidebar on document ready
$(document).ready(function() {
    // Call updateSearchHistorySidebar initially
    updateSearchHistorySidebar();
});
