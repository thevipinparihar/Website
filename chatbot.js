document.addEventListener('DOMContentLoaded', () => {
    const chatbotButton = document.getElementById('chatbot-button');
    const chatbotWindow = document.getElementById('chatbot-window');
    const chatbotClose = document.getElementById('chatbot-close');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const chatbotSuggestions = document.getElementById('chatbot-suggestions');

    if (!chatbotButton || !chatbotWindow || !chatbotClose || !chatbotInput || !chatbotMessages || !chatbotSuggestions) {
        console.error('Chatbot elements not found in the DOM.');
        return;
    }

    // Predefined questions and answers
    const qaPairs = [
        {
            question: "How do I register my vehicle for scrapping?",
            answer: "You can register your vehicle by clicking on the 'Register Vehicle' link on the home page and filling out the required details."
        },
        {
            question: "What documents are required for vehicle scrapping?",
            answer: "You need your vehicle registration certificate (RC), identity proof, and any other documents as specified by the scrapping facility."
        },
        {
            question: "How long does the scrapping process take?",
            answer: "The scrapping process typically takes 3-5 business days after vehicle pickup."
        },
        {
            question: "Can I get a quotation for my vehicle?",
            answer: "Yes, you can get an instant quotation by clicking on the 'Get Quotation' link and entering your vehicle details."
        },
        {
            question: "Is vehicle pickup available?",
            answer: "Yes, free vehicle pickup is available within Telangana coverage areas."
        },
        {
            question: "How do I get the Certificate of Destruction?",
            answer: "After scrapping, you will receive a Certificate of Destruction (COD) confirming lawful disposal."
        },
        {
            question: "Who can I contact for support?",
            answer: "You can contact our support team via the 'Contact Us' page for any assistance."
        }
    ];

    // Toggle chatbot window with smooth expansion
    chatbotButton.addEventListener('click', () => {
        console.log('Chatbot button clicked');
        if (chatbotWindow.classList.contains('expanded')) {
            chatbotWindow.classList.remove('expanded');
            chatbotButton.classList.remove('expanded');
            chatbotWindow.classList.add('hidden');
        } else {
            chatbotWindow.classList.remove('hidden');
            chatbotWindow.classList.add('expanded');
            chatbotButton.classList.add('expanded');
            chatbotInput.focus();
        }
    });

    // Close chatbot window
    chatbotClose.addEventListener('click', () => {
        chatbotWindow.classList.add('hidden');
        chatbotButton.classList.remove('expanded');
    });

    // Show suggestions based on input
    chatbotInput.addEventListener('input', () => {
        const input = chatbotInput.value.toLowerCase();
        chatbotSuggestions.innerHTML = '';
        if (input.length === 0) {
            chatbotSuggestions.style.display = 'none';
            return;
        }
        const filtered = qaPairs.filter(qa => qa.question.toLowerCase().includes(input));
        if (filtered.length === 0) {
            chatbotSuggestions.style.display = 'none';
            return;
        }
        filtered.forEach(qa => {
            const li = document.createElement('li');
            li.textContent = qa.question;
            li.addEventListener('click', () => {
                addMessage('user', qa.question);
                addMessage('bot', qa.answer);
                chatbotSuggestions.innerHTML = '';
                chatbotSuggestions.style.display = 'none';
                chatbotInput.value = '';
            });
            chatbotSuggestions.appendChild(li);
        });
        chatbotSuggestions.style.display = 'block';
    });

    // Add message to chat window
    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        if (sender === 'user') {
            messageDiv.classList.add('user-message');
        } else {
            messageDiv.classList.add('bot-message');
        }
        messageDiv.textContent = text;
        chatbotMessages.appendChild(messageDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    // Handle enter key to submit question
    chatbotInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const question = chatbotInput.value.trim();
            if (question.length === 0) return;
            addMessage('user', question);
            const matchedQA = qaPairs.find(qa => qa.question.toLowerCase() === question.toLowerCase());
            if (matchedQA) {
                addMessage('bot', matchedQA.answer);
            } else {
                addMessage('bot', "Sorry, I don't have an answer for that. Please try another question.");
            }
            chatbotInput.value = '';
            chatbotSuggestions.innerHTML = '';
            chatbotSuggestions.style.display = 'none';
        }
    });
});
