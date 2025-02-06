

document.addEventListener('DOMContentLoaded', function() {

    /* 

        Enhance the responsiveness of the dropdowns by leveraging JS. 

    */

    dropdownSetup()
    slidersSetup()
})

function dropdownSetup() {

    var containers = document.querySelectorAll('.scroll-container')

    containers.forEach(function (container) {

        var containerTitle = container.querySelector('.scroll-container-title')

        containerTitle.addEventListener('click', function() {
            dropdownToggle(container)
        })
    })
}

function slidersSetup() {

    document.querySelectorAll('.settings-container').forEach(container => {

        container.addEventListener('input', function (event) {
            if (event.target && event.target.matches('.slider')) {
                updateSliders(event.target)
            }
        })
    })
}

function dropdownToggle(container) {

    var containerTitle = container.querySelector('.scroll-container-title')
    var containerContent = container.querySelector('.settings-container')

    containerTitle.classList.toggle('active')

    if (containerContent.style.maxHeight) {
        containerContent.style.maxHeight = null
    } else {
        containerContent.style.maxHeight = containerContent.scrollHeight + 'px'
    }
}

function updateSliders(slider) {

    /**
     * Function to update sliders values,
     */

    var output = document.getElementById('output' + slider.id.slice(-1))

    if (output) {
        output.innerHTML - slider.value
    }
}
