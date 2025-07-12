document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(el => {
      el.classList.add('hide');
    });
  }, 3000);

  const columns = document.querySelectorAll('.kanban-column');
  let draggingEl = null;

  document.querySelectorAll('.task-card').forEach(card => {
    card.setAttribute('draggable', true);

    card.addEventListener('dragstart', () => {
      draggingEl = card;
      card.classList.add('dragging');
    });

    card.addEventListener('dragend', () => {
      card.classList.remove('dragging');
      draggingEl = null;
    });
  });

  columns.forEach(col => {
    col.addEventListener('dragover', e => {
      e.preventDefault();
      const afterElement = getDragAfterElement(col, e.clientY);
      if (draggingEl) {
        if (afterElement == null) {
          col.appendChild(draggingEl);
        } else {
          col.insertBefore(draggingEl, afterElement);
        }
      }
    });
    col.addEventListener('drop', e => {
      e.preventDefault();
      if (draggingEl) {
        const newStatus = col.getAttribute('data-status');
        const taskId = draggingEl.getAttribute('data-task-id');
        // Send AJAX request to update status
        fetch(`/tasks/${taskId}/status`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: `status=${encodeURIComponent(newStatus)}`
        })
        .then(res => {
          if (res.ok) {
            col.appendChild(draggingEl);
          } else {
            window.location.reload();
          }
        })
        .catch(() => window.location.reload());
      }
    });
  });

  function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.task-card:not(.dragging)')];
    return draggableElements.reduce((closest, child) => {
      const box = child.getBoundingClientRect();
      const offset = y - box.top - box.height / 2;
      if (offset < 0 && offset > closest.offset) {
        return { offset: offset, element: child };
      } else {
        return closest;
      }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
  }
});