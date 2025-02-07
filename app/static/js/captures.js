
document.addEventListener('DOMContentLoaded', function () {

    const sortButton = document.querySelector('.sort-button')

    sortButton.addEventListener('click', (event) => {

        event.preventDefault()

        if (sortButton.textContent.trim() === 'Oldest') {
            sortButton.textContent = 'Newest'
        } else {
            sortButton.textContent = 'Oldest'
        }
    })

    // Implement searchbar functionality here. 

})