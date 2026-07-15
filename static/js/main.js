// Digital Complaint Management System - Core JavaScripts

document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Mobile Sidebar Toggle Functionality
    const sidebar = document.getElementById('sidebar');
    const menuToggle = document.getElementById('menuToggle');
    const closeSidebar = document.getElementById('closeSidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.add('open');
        });
    }
    
    if (closeSidebar && sidebar) {
        closeSidebar.addEventListener('click', function() {
            sidebar.classList.remove('open');
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 991 && sidebar && sidebar.classList.contains('open')) {
            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickInsideToggle = menuToggle ? menuToggle.contains(event.target) : false;
            
            if (!isClickInsideSidebar && !isClickInsideToggle) {
                sidebar.classList.remove('open');
            }
        }
    });

    // 2. Alert Dismissing
    const closeButtons = document.querySelectorAll('.close-alert');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        });
    });

    // Auto-dismiss alert boxes after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // 3. Image Upload Preview (Submit Form)
    const imageInput = document.getElementById('complaint_image_input');
    const imagePreviewContainer = document.getElementById('image_preview_container');
    const imagePreview = document.getElementById('image_preview');
    
    if (imageInput && imagePreview && imagePreviewContainer) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreviewContainer.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                imagePreview.src = '#';
                imagePreviewContainer.style.display = 'none';
            }
        });
    }

    // 4. Client-side Search and Filter for Complaint Tables
    const searchInput = document.getElementById('tableSearch');
    const categorySelect = document.getElementById('filterCategory');
    const statusSelect = document.getElementById('filterStatus');
    const dateInput = document.getElementById('filterDate');
    const complaintsTable = document.getElementById('complaintsTable');
    
    if (complaintsTable) {
        const rows = complaintsTable.querySelectorAll('tbody tr');
        
        function filterTable() {
            const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
            const category = categorySelect ? categorySelect.value.toLowerCase() : '';
            const status = statusSelect ? statusSelect.value.toLowerCase() : '';
            const filterDate = dateInput ? dateInput.value : ''; // format YYYY-MM-DD
            
            rows.forEach(row => {
                let matchSearch = true;
                let matchCategory = true;
                let matchStatus = true;
                let matchDate = true;
                
                // Text search (checks ID, Title, and Student Name columns)
                if (query !== '') {
                    const idText = row.cells[0] ? row.cells[0].textContent.toLowerCase() : '';
                    const titleText = row.cells[1] ? row.cells[1].textContent.toLowerCase() : '';
                    // Some tables have student name/category in other cells. We check all cell content.
                    let rowText = '';
                    for (let i = 0; i < row.cells.length - 1; i++) {
                        rowText += row.cells[i].textContent.toLowerCase() + ' ';
                    }
                    matchSearch = rowText.includes(query);
                }
                
                // Category Filter
                if (category !== '') {
                    // Category column is usually at index 2 (Student view) or index 3 (Admin view)
                    // We check cells text content
                    let rowHasCategory = false;
                    for (let i = 0; i < row.cells.length; i++) {
                        const cellText = row.cells[i].textContent.toLowerCase().trim();
                        if (cellText === category) {
                            rowHasCategory = true;
                            break;
                        }
                    }
                    matchCategory = rowHasCategory;
                }
                
                // Status Filter
                if (status !== '') {
                    let rowHasStatus = false;
                    for (let i = 0; i < row.cells.length; i++) {
                        const cellText = row.cells[i].textContent.toLowerCase().trim().replace(/\s+/g, '-');
                        const statusFormatted = status.replace(/\s+/g, '-');
                        if (cellText === statusFormatted) {
                            rowHasStatus = true;
                            break;
                        }
                    }
                    matchStatus = rowHasStatus;
                }
                
                // Date Filter (YYYY-MM-DD)
                if (filterDate !== '') {
                    // Find a date cell and compare. Date formats are usually 'YYYY-MM-DD HH:MM:SS' or 'Month DD, YYYY'
                    // We parse dates to compare them
                    let rowHasDate = false;
                    for (let i = 0; i < row.cells.length; i++) {
                        const cellText = row.cells[i].textContent.trim();
                        // Try parsing cellText to date
                        const cellDate = new Date(cellText);
                        if (!isNaN(cellDate.getTime())) {
                            const filterDateObj = new Date(filterDate);
                            // Compare year, month, and day
                            if (cellDate.getFullYear() === filterDateObj.getFullYear() &&
                                cellDate.getMonth() === filterDateObj.getMonth() &&
                                cellDate.getDate() === filterDateObj.getDate()) {
                                rowHasDate = true;
                                break;
                            }
                        }
                    }
                    matchDate = rowHasDate;
                }
                
                // Show/hide row based on combined conditions
                if (matchSearch && matchCategory && matchStatus && matchDate) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }
        
        // Add event listeners for filter inputs
        if (searchInput) searchInput.addEventListener('input', filterTable);
        if (categorySelect) categorySelect.addEventListener('change', filterTable);
        if (statusSelect) statusSelect.addEventListener('change', filterTable);
        if (dateInput) dateInput.addEventListener('change', filterTable);
    }
});

// 5. Dual Login Switcher Helper (Login Page)
function switchLoginTab(role) {
    // Buttons
    const studentTabBtn = document.getElementById('studentTabBtn');
    const adminTabBtn = document.getElementById('adminTabBtn');
    
    // Form containers
    const studentForm = document.getElementById('studentFormContainer');
    const adminForm = document.getElementById('adminFormContainer');
    
    if (role === 'student') {
        studentTabBtn.classList.add('active');
        adminTabBtn.classList.remove('active');
        studentForm.classList.add('active');
        adminForm.classList.remove('active');
    } else {
        adminTabBtn.classList.add('active');
        studentTabBtn.classList.remove('active');
        adminForm.classList.add('active');
        studentForm.classList.remove('active');
    }
}
