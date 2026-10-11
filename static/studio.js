'use strict';
document.querySelectorAll('.delete-form').forEach(form => form.addEventListener('submit', event => {
  if (!window.confirm('Delete this project permanently? It will also disappear from the public portfolio.')) event.preventDefault();
}));
