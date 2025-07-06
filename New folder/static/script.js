function fetchEvents() {
    fetch('/events')
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById('activity-list');
            list.innerHTML = '';
            data.forEach(event => {
                let text = '';
                if (event.action === 'push') {
                    text = `"${event.author}" pushed to "${event.to_branch}" on ${event.timestamp}`;
                } else if (event.action === 'pull_request') {
                    text = `"${event.author}" submitted a pull request from "${event.from_branch}" to "${event.to_branch}" on ${event.timestamp}`;
                } else if (event.action === 'merge') {
                    text = `"${event.author}" merged branch "${event.from_branch}" to "${event.to_branch}" on ${event.timestamp}`;
                }
                const li = document.createElement('li');
                li.textContent = text;
                list.appendChild(li);
            });
        });
}
fetchEvents();
setInterval(fetchEvents, 15000);
