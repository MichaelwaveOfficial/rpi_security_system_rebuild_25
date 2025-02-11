
document.addEventListener('DOMContentLoaded', function() {

    /**
     * Initialise functions once dom has loaded.
     */
    dropdownSetup()
    slidersSetup()
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

    var output = document.getElementById('output' + slider.id.slice(-1))

    if (output) {
        output.innerHTML - slider.value
    }
}

function handleFormSubmission() {

    /**
     * Dynamically handle values being updated by the user on the settings page leveraging AJAX to mitigate
     * page reloads upon submission.
     */

    var settingsForm = document.getElementById('settings-form')

    settingsForm.addEventListener('change', function(event) {

        const submittedData = new FormData(this)

        fetch(this.action, {
            method: 'POST',
            body : submittedData
        })
        .then(response => response.json())
        .then(data => {
            alert('Settings applied!')
            // Implement more dynamic user feedback.
        })
        .catch(error => {
            alert('There was an error applying settings!')
            // Same for errors, need onscreen popups.
        })
    })
}
