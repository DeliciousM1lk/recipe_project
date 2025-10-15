document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('step-formset-container');
    const addButton = document.getElementById('add-step-button');
    const emptyForm = document.getElementById('empty-form');
    const totalForms = document.querySelector('[name$="TOTAL_FORMS"]');

    let formCount = parseInt(totalForms.value);

    function updateForms() {
        let forms = container.querySelectorAll('.step-form-wrapper:not([style*="display: none"])');
        forms.forEach((form, index) => {
            let stepNumberPlaceholder = form.querySelector('.step-number-placeholder');
            if (!stepNumberPlaceholder) {
                let h4 = form.querySelector('h4');
                if (h4) h4.textContent = `Шаг ${index + 1}`;
            } else {
                stepNumberPlaceholder.textContent = index + 1;
            }

            form.setAttribute('data-form-index', index);

            // Обработка полей в пустой форме (используют __prefix__)
            form.querySelectorAll('[name*="__prefix__"]').forEach(field => {
                let name = field.getAttribute('name').replace(/__prefix__/, index);
                let id = field.getAttribute('id').replace(/__prefix__/, index);

                field.setAttribute('name', name);
                field.setAttribute('id', id);

                let label = form.querySelector(`label[for="${field.id}"]`);
                if (label) {
                    label.setAttribute('for', id);
                }
            });

            // Обработка полей в существующих формах (используют старый индекс)
            form.querySelectorAll('[id^="id_step_set-"]').forEach(field => {
                let parts = field.id.split('-');
                if (parts.length >= 3) {
                    let oldIndex = parts[1];
                    let newId = field.id.replace(`-${oldIndex}-`, `-${index}-`);
                    field.id = newId;

                    let newName = field.name.replace(`-${oldIndex}-`, `-${index}-`);
                    field.name = newName;

                    // Обновление атрибута 'for' у тегов <label>
                    let label = form.querySelector(`label[for$="-${oldIndex}-${parts[2]}"]`);
                    if (label) {
                        label.setAttribute('for', newId);
                    }
                }
            });
        });
    }

    function addStep(e) {
        e.preventDefault();

        const newForm = emptyForm.cloneNode(true);
        newForm.style.display = 'block';
        newForm.removeAttribute('id');

        container.insertBefore(newForm, emptyForm);

        formCount++;
        totalForms.value = formCount;

        updateForms();
    }

    function deleteStep(e) {
        if (e.target.classList.contains('remove-step-button-icon') || e.target.closest('.remove-step-button-icon')) {
            const wrapper = e.target.closest('.step-form-wrapper');
            const deleteCheckbox = wrapper.querySelector('input[type="checkbox"][id$="-DELETE"]');

            if (deleteCheckbox) {
                if (wrapper.querySelector('input[name$="-id"]').value) {
                    deleteCheckbox.checked = true;
                    wrapper.style.display = 'none';
                } else {
                    wrapper.remove();

                    formCount--;
                    totalForms.value = formCount;
                }
            }

            updateForms();
        }
    }

    addButton.addEventListener('click', addStep);
    container.addEventListener('click', deleteStep);

    updateForms();
});