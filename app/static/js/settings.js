
document.addEventListener('DOMContentLoaded', function() {

    /**
     * Initialise functions once dom has loaded.
     */
    dropdownSetup()
    slidersSetup()
    togglesSetup()
    setupSelects()
    handleFormSubmission()
})

function dropdownSetup() {

    /**
     * Apply event listeners to dropdown containers titles. Once clicked pass the container of interest and its siblings. 
     */

    var containers = document.querySelectorAll('.scroll-container')

    containers.forEach(function (container) {

        var containerTitle = container.querySelector('.scroll-container-title')

        containerTitle.addEventListener('click', function() {
            dropdownToggle(container, containers)
        })
    })
}

function slidersSetup() {

    /**
     * Apply event listeners to the sliders and get the values of the concerned slider.
     */

    document.querySelectorAll('.settings-container').forEach(container => {

        container.addEventListener('input', function (event) {
            if (event.target && event.target.matches('.slider')) {
                updateSliders(event.target)
            }
        })
    })
}

function dropdownToggle(currentContainer, containers) {

    /**
     * Once toggled by the user. Apply styling tweaks to either open or close the settings container 
     * through max_height adjustments. 
     */

    var currentContainerTitle = currentContainer.querySelector('.scroll-container-title')
    var currentContainerContent = currentContainer.querySelector('.settings-container')

    containers.forEach(function (container) {

        if (container != currentContainer) {

            var content = container.querySelector('.settings-container')
            var title = container.querySelector('.scroll-container-title')

            if (content.style.maxHeight) {
                content.style.maxHeight = null 
            } else {
                title.classList.remove('active')
            }
        }
    })

    currentContainerTitle.classList.toggle('active')

    if (currentContainerContent.style.maxHeight) {
        currentContainerContent.style.maxHeight = null
    } else {
        currentContainerContent.style.maxHeight = currentContainerContent.scrollHeight + 'px'
    }
}

function updateSliders(slider) {

    /**
     * Function to update sliders values and output that value in the html.
     */

    var output = document.getElementById('slider-output' + slider.id.slice(-1))

    if (output) {
        output.innerHTML = slider.value
    }
}

function togglesSetup() {

    /**
     * Apply event listeners to the sliders and get the values of the concerned slider.
     */

    document.querySelectorAll('.settings-container').forEach(container => {

        container.addEventListener('change', function (event) {
            if (event.target && event.target.matches('.toggle')) {
                updateToggles(event.target)
            }
        })
    })
}


function updateToggles(toggle) {

    /**
     * Function to update toggles values and output that value in the html.
     */

    var output = document.getElementById('toggle-output' + toggle.id.slice(-1))

    if (output) {

        if (output.id == 'toggle-output2') {
            output.innerHTML = toggle.checked ? 'Stills' : 'Clips'
        } else {
            output.innerHTML = toggle.checked ? true : false
        }
    }
}

function setupSelects() {

    /**
     * Apply event listeners to the sliders and get the values of the concerned slider.
     */

    document.querySelectorAll('.settings-container').forEach(container => {

        container.addEventListener('change', function (event) {
            if (event.target && event.target.matches('.select')) {
                updateSelects(event.target)
            }
        })
    })
}

function updateSelects(select) {

    /**
     * Function to update toggles values and output that value in the html.
     */

    var output = document.getElementById('select-output0')

    if (output) {
        
        output.innerHTML = select.value 
    }
}

function handleFormSubmission() {

    document.getElementById('settings-form').addEventListener('change', function (event) {

        event.preventDefault()

        var updatedSettings = new FormData(this)

        console.log(updatedSettings)

        fetch('/settings/update', {
            method: 'POST', 
            body: updatedSettings
        })
        .then(response => response.json())
        .then(data => {
            console.log('Settings Updated!', data)
        })
        .catch(error => console.error('Error updating settings!', error));
    })
}
