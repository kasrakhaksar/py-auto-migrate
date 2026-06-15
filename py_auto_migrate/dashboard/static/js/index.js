document.querySelectorAll('.copy-btn').forEach(button => {

    button.addEventListener('click', async () => {

        const code =
            button.parentElement.querySelector('code').innerText;

        try {

            await navigator.clipboard.writeText(code);

            button.classList.add('copied');
            button.textContent = 'Copied ✓';

            setTimeout(() => {
                button.classList.remove('copied');
                button.textContent = 'Copy';
            }, 2000);

        } catch (err) {

            button.textContent = 'Failed';

            setTimeout(() => {
                button.textContent = 'Copy';
            }, 2000);
        }
    });

});