document.getElementById('addNoteButton').addEventListener('click', function() {
    const noteInput = document.getElementById('noteInput');
    const note = noteInput.value;

    if (note) {
        fetch('/api/notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ note: note })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            noteInput.value = '';
            loadNotes();
        });
    }
});

function loadNotes() {
    fetch('/api/notes')
        .then(response => response.json())
        .then(notes => {
            const notesList = document.getElementById('notesList');
            notesList.innerHTML = '';
            notes.forEach(note => {
                const li = document.createElement('li');
                li.textContent = note;
                notesList.appendChild(li);
            });
        });
}

// Загрузка заметок при загрузке страницы
loadNotes();