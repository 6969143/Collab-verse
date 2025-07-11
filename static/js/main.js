document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(el => {
      el.classList.add('hide');
    });
  }, 3000);

  const lists = document.querySelectorAll('.list-group');
  let draggingEl = null;

  document.querySelectorAll('.list-group-item').forEach(card => {
    card.setAttribute('draggable', true);

    card.addEventListener('dragstart', () => {
      draggingEl = card;
      card.classList.add('dragging');
    });

    card.addEventListener('dragend', () => {
      draggingEl.classList.remove('dragging');
      draggingEl = null;
    });
  });

  lists.forEach(list => {
    list.addEventListener('dragover', e => {
      e.preventDefault();
      if (draggingEl) {
        list.appendChild(draggingEl);
      }
    });
  });
});