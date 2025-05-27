function updateForm() {
    const eventType = document.getElementById('eventType').value;
    const dynamicField = document.getElementById('dynamicField');
    const dynamicLabel = document.getElementById('dynamicLabel');
    const dynamicInput = document.getElementById('dynamicInput');

    dynamicField.classList.remove('hidden');

    switch (eventType) {
        case 'Birthday':
            dynamicLabel.textContent = 'Name:';
            dynamicInput.placeholder = 'Enter name';
            break;
        case 'Anniversary':
            dynamicLabel.textContent = 'Names:';
            dynamicInput.placeholder = 'Enter names';
            break;
        case 'Football':
            dynamicLabel.textContent = 'Game:';
            dynamicInput.placeholder = 'Teams';
            break;
        case 'Miscellaneous':
            dynamicLabel.textContent = 'Describe Event:';
            dynamicInput.placeholder = 'Enter event description';
            break;
        default:
            dynamicField.classList.add('hidden');
            break;
    }
}