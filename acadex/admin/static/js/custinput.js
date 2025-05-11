let radioBtns = document.getElementsByClassName('form-check-input');
let searchInput = document.getElementsByClassName('custom-form-control')[0];

function updateInputBasedOnCheckedRadio() {
  for (let i = 0; i < radioBtns.length; i++) {
    if (radioBtns[i].checked) {
      if (radioBtns[i].value == 'Enter adm no') {
        searchInput.setAttribute('placeholder', 'Enter adm no');
        searchInput.value = '';
        searchInput.setAttribute('type', 'number');
      } else if (radioBtns[i].value == 'Enter name') {
        searchInput.setAttribute('placeholder', 'Enter name');
        searchInput.value = '';
        searchInput.setAttribute('type', 'text');
      } else {
        searchInput.setAttribute('placeholder', 'Enter UPI no');
        searchInput.value = '';
        searchInput.setAttribute('type', 'text');
      }
      break; // Stop once the checked button is found
    }
  }
}

// Run once on page load
updateInputBasedOnCheckedRadio();

// Then run again on any change
for (let i = 0; i < radioBtns.length; i++) {
  radioBtns[i].addEventListener('change', updateInputBasedOnCheckedRadio);
}
