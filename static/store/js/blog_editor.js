document.addEventListener('DOMContentLoaded', function() {
    // Find the title field and the CKEditor container
    const titleField = document.getElementById('id_title');
    if (!titleField) return;

    // Create the AI button
    const aiBtn = document.createElement('button');
    aiBtn.type = 'button';
    aiBtn.className = 'button';
    aiBtn.style.marginLeft = '10px';
    aiBtn.style.backgroundColor = '#8224e3';
    aiBtn.style.color = '#fff';
    aiBtn.innerHTML = '<i class="bi bi-stars"></i> Magic AI Generate';
    
    // Append after title field
    titleField.parentNode.appendChild(aiBtn);

    aiBtn.addEventListener('click', async () => {
        const topic = titleField.value;
        if (!topic) {
            alert('Please enter a title/topic first!');
            return;
        }

        aiBtn.disabled = true;
        aiBtn.innerText = 'Generating...';

        try {
            const response = await fetch('/ai/generate-blog/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ topic: topic })
            });

            const data = await response.json();
            if (data.content) {
                // Find the CKEditor instance
                // django-ckeditor-5 usually uses the name of the field
                const editorElement = document.querySelector('.ck-editor__editable');
                if (editorElement && editorElement.ckeditorInstance) {
                    editorElement.ckeditorInstance.setData(data.content);
                } else {
                    // Fallback to manual insertion if possible or alert
                    alert('Content generated! Please paste this in manually or look for the updated editor.');
                    console.log(data.content);
                }
            } else {
                alert('Error: ' + (data.error || 'Failed to generate content'));
            }
        } catch (error) {
            console.error(error);
            alert('Error generating blog content.');
        } finally {
            aiBtn.disabled = false;
            aiBtn.innerHTML = '<i class="bi bi-stars"></i> Magic AI Generate';
        }
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
