document.addEventListener('DOMContentLoaded', function () {
    const dropdownToggle = document.getElementById('testDropdownToggle');
    const dropdownContent = document.getElementById('testDropdownContent');

    dropdownToggle.addEventListener('click', () => {
        console.log('Test dropdown toggle clicked');
        if (dropdownContent.style.display === 'block') {
            dropdownContent.style.display = 'none';
        } else {
            dropdownContent.style.display = 'block';
        }
    });
});
