(function () {
    document.addEventListener('DOMContentLoaded', function () {
        // Safe DOM element lookups
        const checkbox = document.getElementById('is_center_manager');
        const branchGroup = document.getElementById('center_branch_group');
        const branchSelect = document.getElementById('center_branch');
        const teacherRole = document.getElementById('teacher-role');
        const gradeSelectDiv = document.getElementById('class-teacher-grade');
        const gradeSelect = document.getElementById('grade-select');
        const error = document.getElementById('grade-error');

        // Exit early if key elements are missing
        if (!checkbox || !branchGroup || !branchSelect || !teacherRole || !gradeSelectDiv || !gradeSelect) {
            console.warn('Some required DOM elements are missing. Skipping role form behavior.');
            return;
        }

        function toggleField({ triggerValue, triggerElement, targetElement, inputElement, expectedValue }) {
            if (triggerElement.value === expectedValue || triggerElement.checked) {
                targetElement.classList.remove('d-none');
                inputElement?.setAttribute('required', 'required');
            } else {
                targetElement.classList.add('d-none');
                inputElement?.removeAttribute('required');
            }
        }

        function handleInitialState() {
            toggleField({
                triggerElement: checkbox,
                targetElement: branchGroup,
                inputElement: branchSelect
            });

            toggleField({
                triggerValue: teacherRole.value,
                triggerElement: teacherRole,
                targetElement: gradeSelectDiv,
                inputElement: gradeSelect,
                expectedValue: 'classteacher'
            });

            // Handle form resubmission with error
            if (error && teacherRole.value === 'classteacher') {
                gradeSelectDiv.classList.remove('d-none');
                gradeSelect.setAttribute('required', 'required');
            }
        }

        // Initial setup
        handleInitialState();

        // Event listeners
        checkbox.addEventListener('change', () => {
            toggleField({
                triggerElement: checkbox,
                targetElement: branchGroup,
                inputElement: branchSelect
            });
        });

        teacherRole.addEventListener('change', () => {
            toggleField({
                triggerValue: teacherRole.value,
                triggerElement: teacherRole,
                targetElement: gradeSelectDiv,
                inputElement: gradeSelect,
                expectedValue: 'classteacher'
            });
        });

        
        
        gradeSelect.addEventListener('change', function() {
            // Handle streams display.
            const branch_name = document.getElementById('branch-holder').dataset.branchName;
            fetch(STREAM_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ grade: this.value, branch: branch_name })
            })
            .then(response => response.json())
            .then(data => {
                const streamDiv = document.getElementById('stream-select-div');
                const streamSelect = document.getElementById('stream-select');

                // Clear existing options except the placeholder
                streamSelect.innerHTML = '<option value="">Select a stream</option>';

                if (data.success && Array.isArray(data.streams) && data.streams.length > 0) {
                    // Add new stream options
                    data.streams.forEach(stream => {
                        const option = document.createElement('option');
                        option.value = stream;   // or stream.name if that's what you use
                        option.textContent = stream;
                        streamSelect.appendChild(option);
                    });

                    // Show and require the stream select field
                    streamDiv.classList.remove('d-none');
                    streamSelect.setAttribute('required', 'required');
                } else {
                    // Hide the stream field and make it not required
                    streamDiv.classList.add('d-none');
                    streamSelect.removeAttribute('required');
                }
            })
            .catch(error => {
                console.error('An error occurred while fetching streams:', error);
                alert("Failed to load streams. Please try again or contact support. Phone: 0701948782");
            });

        })
    });
})();