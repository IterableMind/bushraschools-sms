(function IIFE (){
    document.addEventListener('DOMContentLoaded', function () {
        let deleteButtons = document.querySelectorAll('.btn-delete'); 
  
        // reload the page to reset the model.
        function reloadPage() {
           location.reload();
        }
         
        // Eventlistener to open edit model. 
        let editButtons = document.querySelectorAll('.btn-edit');
        editButtons.forEach(button => {
           button.addEventListener('click', function() {
              let teacherName = this.closest('tr').querySelector('.teacher-name').textContent.trim();
              const teacherId = this.closest('tr').querySelector('.tr-id').textContent.trim();
  
              // Fetch data to display on the form.
              fetch(fetchUrl, { 
                 method: 'POST',
                 headers: { 'Content-Type': 'application/json' },
                 body: JSON.stringify({ id: teacherId })
              })
              .then(response => {
                 if (!response.ok) throw new Error("Failed to fetch student data");
                 return response.json();
              })
              .then(data => { 
                 document.getElementById('t-id').value = data['id'];
                 document.getElementById('teacher-name').textContent = data['fullname'];
                 document.getElementById('teacher-name-input').value = data['fullname'];
                 document.getElementById('id-no').value = data['id_no'];
                 document.getElementById('tsc-no').value = data['tsc_no'];
                 document.getElementById('phone-no').value = data['phone_no'];
                 document.getElementById('branch').value = data['branch'];
                 document.getElementById('salary').value = data['salary'];
              })
              .catch(error => {
                 console.log("Fetch error:", error);
              });
           });
        });
  
         // Handle delete teacher Model
         function handleDeleteModal(button) {
             const row = button.closest('tr');
             if (!row) return;
 
             const teacherNameElement = row.querySelector('.teacher-name');
             if (!teacherNameElement) return;
 
             const teacherName = teacherNameElement.textContent.trim();
             document.getElementById('del-teacher-name').textContent = teacherName;
             document.getElementById('delete-hidden-teacher-name').value = teacherName;
         }
         // Attach event listeners to delete buttons
         deleteButtons.forEach(button => {
         button.addEventListener('click', () => handleDeleteModal(button));
         });
     });
}())