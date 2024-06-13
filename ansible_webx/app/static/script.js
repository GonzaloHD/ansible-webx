

function addExtraVarInput() {
    var container = $('#extra-vars-container');
    // Count the number of existing tag inputs
    var numberOfTagInputs = $('.tag-input-divs').length;

    // Create extra_vars input field
    var input = $('<input>', {
        type: 'text',
        class: 'extra-var-input',
        name: 'extra_vars'
    });

    // Create remove button
    var removeButton = $('<button>', {
        type: 'button',
        id: 'remove-button-extra-var-' + numberOfTagInputs,
        class: 'remove-button-vars remove-button',
        text: 'Remove'
    });

    // Create container for input field and remove button
    var inputContainer = $('<div>').append(input, removeButton);

    // Append input field and remove button container to the main container
    container.append(inputContainer);
}


// Function to add a new tag input field
function addTagInput() {
    // Get tags container to place them
    var container = $('#tags-container');

    // Count the number of existing tag inputs
    var numberOfTagInputs = $('.tag-input-divs').length;

    // Clone the original tag input container
    var clonedTagInputDiv = $('#tag-input-div-0').clone(true);

    // Set unique IDs for cloned elements
    clonedTagInputDiv.attr('id', 'tag-input-div-' + numberOfTagInputs);
    clonedTagInputDiv.find('.tag-input').attr('id', 'tag-input-' + numberOfTagInputs);
    clonedTagInputDiv.find('.remove-button-tags').attr('id', 'remove-button-tag-' + numberOfTagInputs);

    // Clear the value of the cloned input field
    clonedTagInputDiv.find('.tag-input').val('');

    // Append the cloned tag input container to the main container
    container.append(clonedTagInputDiv);
}

// Add event listener to the document and delegate it the parent containers
document.addEventListener('click', function(event) {
    window.scrollTo(0, document.body.scrollHeight);
    var tagsContainer = document.getElementById('tags-container');
    // var extraVarsContainer = document.getElementById('extra-vars-container');
    var parentContainer = event.target.parentElement;
    if (event.target.classList.contains('remove-button-tags')) {
        var tagInputContainers = tagsContainer.querySelectorAll('.tag-input-divs');

        // Check if the parent container is for tags and there is more than one tag input container remaining
        if (tagInputContainers.length > 1) {
            // Remove the parent container
            parentContainer.remove();
        } else {
            // Clear the value of the tag input field
            parentContainer.querySelector('.tag-input').value = '';
        }
    } else if (event.target.classList.contains('remove-button-vars')) {
            // Remove the parent container
            parentContainer.remove();
    }
}, false);

// Load the dynamic and constant section when the page loads
$(document).ready(function() {
    loadDynamicSection(); // Load the dynamic section initially
    // // Set a delay before loading the constant section
    // setTimeout(function() {
    //     loadConstantSection(); // Load the constant section after the delay
    // }, 1000); // Adjust the delay time as needed (in milliseconds)

});

var firstLoad = true;

// Function to load the dynamic and extra vars sections using AJAX
function loadDynamicSection() {
    $.ajax({
        url: '/dynamic_section',
        method: 'GET',
        success: function(response) {
            // Update the dynamic section with the response
            $('#dynamic-section').html(response.dynamic_section_content);
            // Update the extra vars section with the response
            $('#extra-vars-sites-section').html(response.extra_vars_section_content);
            if (!firstLoad) {
                window.scrollTo(0, document.body.scrollHeight);                
            } else {
                firstLoad = false;
            }
        },
        error: function(xhr, status, error) {
            // Handle error if needed
        }
    });

}

function loadExtraVarsSitesSection() {
    $('#extra-vars-sites-section').load('/extra_vars_sites_section');
}

function loadConstantSection() {
    // Load the constant section
    $('#constant-section').load('/constant_section', function() {
        // Event listener to track scrolling by the user
        var messages = document.getElementById('messages');
        messages.addEventListener('scroll', function() {
        var scrollPos = messages.scrollTop + messages.clientHeight;
        var scrollBottom = messages.scrollHeight;
        // Check if user is at the bottom
        isScrolledToBottom = scrollPos === scrollBottom;
        });
    });

    // Socket setting to receive the data
    var socket = io();
    var isScrolledToBottom = true; // Flag to track if user is at the bottom initially

    socket.on('connect', function() {
        const sid = socket.id;  // Get the sid directly from the socket object
        console.log('Connected with sid:', sid);
    });
    socket.on('message', function(data) {
        var preElement = document.createElement('pre');
        preElement.innerHTML = data;
        preElement.classList.add('stdOutput');
        messages.appendChild(preElement);

        // Scroll to bottom if user is at the bottom or hasn't scrolled manually
        if (isScrolledToBottom) {
            messages.scrollTop = messages.scrollHeight;
        }
    });
}


// Variable to track if loadConstantSection() has been triggered
var constantSectionLoaded = false;

// Function to handle form submission asynchronously
function handleSubmit(event) {
    // Prevent default form submission
    event.preventDefault();

    // Set timeout based on whether loadConstantSection() has been triggered
    var timeout = constantSectionLoaded ? 0 : 2000;

    // Trigger loadConstantSection() if it hasn't been triggered before
    if (!constantSectionLoaded) {
        loadConstantSection();
        constantSectionLoaded = true;
    }

    setTimeout(function(){
        // Remove any existing error message
        var errorMessage = document.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
        // Remove any existing warning message
        var warningMessage = document.querySelector('.warning-message');
        if (warningMessage) {
            warningMessage.remove();
        }    

        // Remove any existing JSON response message
        var jsonResponse = document.querySelector('.output-response');
        if (jsonResponse) {
            jsonResponse.remove();
        }

        // Remove any existing Output messages
        var stdOutputs = document.querySelectorAll('.stdOutput');
        stdOutputs.forEach(function(stdOutput) {
            stdOutput.remove();
        });

        // Display loading message
        var loadMessage = document.querySelector('.load-message');
        if (loadMessage) {
            loadMessage.textContent = 'Loading...';
            window.scrollTo(0, document.body.scrollHeight);
        }

        // Your form submission logic here
        $.ajax({
            url: '/execute_ansible', // URL to submit the form data
            method: 'POST',
            data: $('form').serialize(), // Serialize form data
            success: function(response) {
                // Reload the dynamic section after form submission
                loadDynamicSection();            
            },
            error: function(xhr, status, error) {
                // Handle error if needed
            }
        });


    }, timeout)

}

// Function to handle tag selected
function handleSelected(event) {
    // Extract tags from inputs
    var tagsSelected = [];
    var extraVarsSelected = [];
    var serverSelected = $('.limit-input').val();
    var extraVarKeySelected = $('.extra-vars-sites-key-input').val();
    var extraVarValueSelected = $('.extra-vars-sites-value-input').val();

    var changedElement = event.target;
    var focusedElement;

    // Flag to indicate if a legitimate click on a Remove button has occurred
    var buttonClick = false;

    // Attach a blur event listener to track the element that receives focus next
    changedElement.addEventListener('blur', function (blurEvent) {
        focusedElement = blurEvent.relatedTarget;
        // Check if the focused element is a Remove button and a legitimate click has not occurred
        if ($(focusedElement).hasClass('extra-vars-sites-value-input') && !buttonClick) {
            // If not, prevent triggering the click event
            buttonClick = false;
        } else {
            // Otherwise, reset the flag for the next focus event
            buttonClick = false;
        }
    });

    // Attach a click event listener to all Remove buttons
    $('.extra-vars-sites-value-input').on('click', function () {
        // Set the flag to indicate a legitimate click on a Remove button
        buttonClick = true;
    });

    $('.tag-input').each(function () {
        tagsSelected.push($(this).val());
    });
    $('.extra-var-input').each(function () {
        extraVarsSelected.push($(this).val());
    });

    $.ajax({
        url: '/extra_vars_sites_section', 
        method: 'GET',
        data: {
            loadVars: true,
            tagsSelected: tagsSelected,
            serverSelected: serverSelected,
            extraVarsSelected: extraVarsSelected,
            extraVarKeySelected: extraVarKeySelected,
            extraVarValueSelected: extraVarValueSelected
        },
        success: function (response) {
            // Update the dynamic section with the response            
            $('#extra-vars-sites-section').html(response);
            var focusedElementId = $(focusedElement).attr('id');
            var focusedVal = $(focusedElement).val();
            var selector = '#' + focusedElementId;

            var elementToFocus = $(selector)

            if (elementToFocus.length > 0 && selector.includes("input")) {
                // Focus the element and set cursor position to the end
                elementToFocus.focus().val(focusedVal).prop('selectionStart', focusedVal.length).prop('selectionEnd', focusedVal.length);
            } else if ($(focusedElement).hasClass('extra-vars-sites-value-input') && buttonClick) {
                // Trigger button click only if focused element is a Remove button and a legitimate click has occurred
                elementToFocus.trigger('click');            

            } else {
                // console.error('Element to focus not found or not an input');
            }
        },
        error: function (xhr, status, error) {
            // Handle error if needed
        }
    });

}

// Function to load the dynamic section and Extra Vars Sites Section
function loadValues(id) {
    $.ajax({
        url: '/dynamic_section',
        method: 'GET',
        data: {
            id_input: id
        },
        success: function(response) {
            // Update the dynamic section div
            $('#dynamic-section').html(response.dynamic_section_content);
            // Update the Extra Vars Sites Section div
            $('#extra-vars-sites-section').html(response.extra_vars_section_content);
        },
        error: function(xhr, status, error) {
            // Handle error if needed
        }
    });
}

// Function to copy command executed to the clipboard
function copyText(id) {
    var liElement = document.getElementById(id);
    var liText = '';

    // Loop through child nodes and exclude buttons
    for (var i = 0; i < liElement.childNodes.length; i++) {
        var node = liElement.childNodes[i];
        if (node.nodeType === Node.TEXT_NODE) {
            liText += node.textContent.trim() + ' '; // Replace line breaks, consecutive spaces, and trim
        }
    }
    liText = liText.replace(/\n/g, ' ').replace(/\s+/g, ' ')

    // Copy text to clipboard
    navigator.clipboard.writeText(liText.trim()).then(function() {
        // Show notification that text was copied
        var notification = document.createElement('div');
        notification.textContent = 'Text copied!';
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.left = '50%';
        notification.style.transform = 'translateX(-50%)';
        notification.style.backgroundColor = '#007bff';
        notification.style.color = '#ffffff';
        notification.style.padding = '10px 20px';
        notification.style.borderRadius = '5px';
        notification.style.zIndex = '9999';
        document.body.appendChild(notification);

        // Remove notification after 1 seconds
        setTimeout(function() {
            document.body.removeChild(notification);
        }, 1000);
    }, function(err) {
        console.error('Unable to copy text: ', err);
    });
}


