export function openTab(evt, tabName) {
    // Hide all tab contents
    const tabContent = document.getElementsByClassName("tabcontent");
    for (let i = 0; i < tabContent.length; i++) {
        tabContent[i].style.display = "none";
    }

    // Remove the active class from all tab links
    const tabLinks = document.getElementsByClassName("tablinks");
    for (let i = 0; i < tabLinks.length; i++) {
        tabLinks[i].className = tabLinks[i].className.replace(" active", "");
    }

    // Show the selected tab's content and mark the link as active
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

// ################################################ moved items
onclick="openTab(event, 'Workers')"

// Attach event listeners for tab buttons (simplified)
const tabButtons = document.querySelectorAll('.tablinks');
tabButtons.forEach(button => {
    button.addEventListener('click', (evt) => {
        const tabName = button.getAttribute('data-tab');
        openTab(evt, tabName);
    });
});