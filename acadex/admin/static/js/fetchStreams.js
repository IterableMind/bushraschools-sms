function fetchAndDisplayStreams(fetchUrl) {
    const streamField = document.getElementById("stream-fields");
    const gradeSelect = document.getElementById('grade-select');
    const streamSelect = document.getElementById("dynamicSelect");
    const branchNameHolder = document.getElementById('branch-name');

    if (!gradeSelect || !streamField || !branchNameHolder || !streamSelect) return;

    gradeSelect.addEventListener('change', function () {
        const grade = this.value;
        const branchName = branchNameHolder.dataset.branchName;

        if (grade && branchName) {
            fetch(fetchUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ grade: grade, branch: branchName })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.streams.length > 0) {
                    streamField.style.display = "block";
                    streamSelect.innerHTML = '';

                    const defaultOption = document.createElement("option");
                    defaultOption.value = "";
                    defaultOption.textContent = "Select stream";
                    defaultOption.disabled = true;
                    defaultOption.selected = true;
                    streamSelect.appendChild(defaultOption);
                    streamSelect.setAttribute('required', 'required');

                    data.streams.forEach(stream => {
                        const option = document.createElement("option");
                        option.value = stream;
                        option.textContent = stream;
                        streamSelect.appendChild(option);
                    });

                    const option = document.createElement("option");
                    option.value = 'All Streams'
                    option.textContent = 'All Streams';
                    streamSelect.appendChild(option);

                } else {
                    streamField.style.display = "none";
                }
            })
            .catch(error => {
                console.error("Failed to fetch streams:", error);
                streamField.style.display = "none";
            });
        } else {
            streamField.style.display = "none";
        }
    });
}
