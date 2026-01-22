document.addEventListener('DOMContentLoaded', function() {
    ClassicEditor
        .create(document.querySelector('.richtext-editor'))
        .catch(error => {
            console.error(error);
        });
});
