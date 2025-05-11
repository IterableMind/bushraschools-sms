function getStreams(url) { 
  document.getElementById('grade').addEventListener('change', function () {
    const selectedValue = this.value;  
    const url_path = url
    const selectStreamsDiv = document.getElementById('stream-fields');

    if (selectedValue) {
      fetch(url_path, { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ selectedValue }),  
      })
        .then(response => response.json()) 
        .then(data => { 
          if (data.length > 1) { 
            const dynamicSelect = document.getElementById('dynamicSelect');
             
            dynamicSelect.innerHTML = '';

            // Add a placeholder option
            const placeholderOption = document.createElement('option');
            placeholderOption.value = '';
            placeholderOption.textContent = 'Select stream';
            placeholderOption.disabled = true;
            placeholderOption.selected = true;
            dynamicSelect.appendChild(placeholderOption);

            // Populate the select field with options
            data.forEach(item => {
              const option = document.createElement('option');
              option.value = item;  
              option.textContent = item; 
              dynamicSelect.appendChild(option);
            });

            // Make the select field visible 
            selectStreamsDiv.style.display = 'block';
          } else {
            selectStreamsDiv.style.display = 'none';
          }
        })
        .catch(error => console.error('Error:', error));  
    }
  });
}