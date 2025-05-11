// Dynamically control the set up of grade and streams.
var gradeSelect = document.getElementById('grade-select')
var streamsSelect = document.querySelector('.hidden-display')
var submitBtn = document.getElementById('submit-btn')
var streamsDiv = document.querySelector('.streams')
var singleStreamCheckBtn = document.getElementById('single-btn')

gradeSelect.addEventListener('change', () => {
  singleStreamCheckBtn.checked = true
  if (gradeSelect.value) {
    streamsSelect.style = "display: block;"
    submitBtn.style = "display: block;"
    removeMuiltStreamsInputs()
  } else {
    streamsSelect.style = "display: none;"
    submitBtn.style = "display: none;"
    removeMuiltStreamsInputs()
  }
})

// Display stream entry inputs.
function displayStreamsInputs() { 
  streamsDiv.style = 'display: block';
}
// Remove Stream entry inputs.
function removeMuiltStreamsInputs() {
  streamsDiv.style = 'display: none';
}

document.getElementById('muilt-btn').addEventListener('click', displayStreamsInputs)
singleStreamCheckBtn.addEventListener('click', removeMuiltStreamsInputs)