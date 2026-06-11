document.addEventListener('DOMContentLoaded', function() {
    // Wait slightly to ensure Django's dynamic inline setup is ready
    setTimeout(initMultipleUpload, 100);

    function initMultipleUpload() {
        const inlineGroup = document.getElementById('images-group');
        if (!inlineGroup) return;

        // 1. Add a HUGE PRONOUNCED button
        const header = inlineGroup.querySelector('h2');
        if (header && !document.getElementById('custom-multi-upload-btn')) {
            const btn = document.createElement('button');
            btn.id = 'custom-multi-upload-btn';
            btn.type = 'button';
            btn.innerHTML = '📁 UPLOAD MULTIPLE IMAGES';
            btn.style.cssText = 'margin-left: 30px; background: #8224e3; color: white; padding: 8px 20px; border-radius: 6px; border: none; cursor: pointer; font-weight: bold; font-size: 14px; text-transform: uppercase; box-shadow: 0 2px 4px rgba(0,0,0,0.2);';
            
            const hiddenFile = document.createElement('input');
            hiddenFile.type = 'file';
            hiddenFile.multiple = true;
            hiddenFile.accept = 'image/*';
            hiddenFile.style.display = 'none';

            header.appendChild(btn);
            header.appendChild(hiddenFile);

            btn.addEventListener('click', function(e) {
                e.preventDefault();
                hiddenFile.click();
            });

            hiddenFile.addEventListener('change', function(e) {
                handleFiles(e.target.files);
                e.target.value = ''; // clear input so the same files can be selected again if needed
            });
        }

        // 2. Make all standard inputs multiple
        function makeInputsMultiple() {
            const fileInputs = inlineGroup.querySelectorAll('input[type="file"]:not([multiple])');
            fileInputs.forEach(input => {
                input.multiple = true;
                input.accept = 'image/*';
                
                // Add an event listener to intercept the multiple files on standard inputs
                input.addEventListener('change', function(e) {
                    if (e.target.files && e.target.files.length > 1) {
                        const files = e.target.files;
                        // Assign first file to this input
                        const dtFirst = new DataTransfer();
                        dtFirst.items.add(files[0]);
                        e.target.files = dtFirst.files;
                        
                        // Handle the rest
                        const restFiles = [];
                        for(let i = 1; i < files.length; i++) restFiles.push(files[i]);
                        handleFiles(restFiles);
                    }
                });
            });
        }
        
        makeInputsMultiple();

        // Observe new rows added by Django to make their inputs multiple too
        const tbody = inlineGroup.querySelector('fieldset table tbody');
        if (tbody) {
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                        makeInputsMultiple();
                    }
                });
            });
            observer.observe(tbody, { childList: true });
        }

        function handleFiles(files) {
            if (!files || files.length === 0) return;
            
            const addLink = inlineGroup.querySelector('.add-row a');
            if (!addLink) return;

            for (let i = 0; i < files.length; i++) {
                // Trigger Django's built in "Add another" function
                addLink.click();
                
                // Find the newly added row
                const rows = inlineGroup.querySelectorAll('.dynamic-images');
                const lastRow = rows[rows.length - 1];
                
                if (lastRow) {
                    const imgInput = lastRow.querySelector('input[type="file"]');
                    if (imgInput) {
                        imgInput.multiple = true; // Ensure the new input also accepts multiple
                        const dt = new DataTransfer();
                        dt.items.add(files[i]);
                        imgInput.files = dt.files;
                    }
                }
            }
            updateOrders();
        }

        // 3. SortableJS integration for drag-and-drop reordering
        if (tbody) {
            if (typeof Sortable === 'undefined') {
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/sortablejs@1.15.2/Sortable.min.js';
                script.onload = initSortable;
                document.head.appendChild(script);
            } else {
                initSortable();
            }

            function initSortable() {
                Sortable.create(tbody, {
                    animation: 150,
                    handle: 'tr.dynamic-images',
                    draggable: 'tr.dynamic-images',
                    ghostClass: 'sortable-ghost',
                    onEnd: function() {
                        updateOrders();
                    }
                });
                
                const style = document.createElement('style');
                style.innerHTML = `
                    tr.dynamic-images { cursor: grab; }
                    tr.dynamic-images:active { cursor: grabbing; }
                    tr.dynamic-images.sortable-ghost { opacity: 0.4; }
                `;
                document.head.appendChild(style);
            }
        }
        
        function updateOrders() {
            if (!tbody) return;
            const rows = tbody.querySelectorAll('tr.dynamic-images');
            let order = 0;
            rows.forEach(row => {
                const deleteInput = row.querySelector('.delete input[type="checkbox"]');
                if (deleteInput && deleteInput.checked) return;
                
                const orderInput = row.querySelector('.field-order input');
                if (orderInput) {
                    orderInput.value = order;
                    order++;
                }
            });
        }

        // Handle deletion changes to automatically update order
        inlineGroup.addEventListener('change', function(e) {
            if (e.target.matches('.delete input[type="checkbox"]')) {
                updateOrders();
            }
        });
    }
});
