let currentQuestion = 0;
const totalQuestions = 10;

function switchScreen(screenId) {
    // Hide all screens
    const screens = document.querySelectorAll('.screen');
    screens.forEach(screen => screen.classList.remove('active'));
    
    // Show the target screen
    const targetScreen = document.getElementById(screenId);
    if (targetScreen) {
        targetScreen.classList.add('active');
    }
}

function startGame() {
    switchScreen('infoCollection');
}

function showInstructions() {
    switchScreen('instructions');
}

function backToMenu() {
    switchScreen('mainMenu');
    currentQuestion = 0;
}

function exitGame() {
    if (confirm('Are you sure you want to exit?')) {
        alert('Thank you for using the Stress Assessment Game. Goodbye!');
        // Optionally redirect or close
    }
}

function submitInfo() {
    const age = document.getElementById('age').value;
    const grade = document.getElementById('grade').value;
    const strand = document.getElementById('strand').value;
    
    if (!age || !grade || !strand) {
        alert('Please fill in all fields');
        return;
    }
    
    fetch('/api/submit-info', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ age, grade, strand })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentQuestion = 0;
            loadQuestion();
            switchScreen('questionsScreen');
        }
    });
}

function loadQuestion() {
    if (currentQuestion >= totalQuestions) {
        showResults();
        return;
    }
    
    fetch(`/api/get-question?num=${currentQuestion}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('questionText').textContent = data.question;
            document.getElementById('questionCounter').textContent = `Question ${data.number} of ${data.total}`;
            
            const progress = ((currentQuestion) / totalQuestions) * 100;
            document.getElementById('progressFill').style.width = progress + '%';
        });
}

function submitAnswer(answer) {
    fetch('/api/submit-answer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question_index: currentQuestion, answer: answer })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentQuestion++;
            if (currentQuestion < totalQuestions) {
                loadQuestion();
            } else {
                showResults();
            }
        }
    });
}

function showResults() {
    fetch('/api/calculate-score', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('finalScore').textContent = data.score;
        document.getElementById('stressLevel').textContent = data.stress_level;
        document.getElementById('advice').textContent = data.advice;
        switchScreen('results');
    });
}

function shareApp() {
    // Open the share modal so users can pick a platform
    openShareModal();
}

function openShareModal() {
    const modal = document.getElementById('shareModal');
    if (modal) modal.style.display = 'block';
}

function closeShareModal() {
    const modal = document.getElementById('shareModal');
    if (modal) modal.style.display = 'none';
}

function shareTo(platform) {
    const pageUrl = window.location.href.split('?')[0];
    const text = encodeURIComponent('Try the Stress Assessment Game and check your stress levels! ' + pageUrl);
    const url = encodeURIComponent(pageUrl);

    let shareUrl = null;

    switch (platform) {
        case 'whatsapp':
            // works on web and mobile; wa.me is preferred
            shareUrl = `https://api.whatsapp.com/send?text=${text}`;
            break;
        case 'telegram':
            shareUrl = `https://t.me/share/url?url=${url}&text=${text}`;
            break;
        case 'facebook':
            shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
            break;
        case 'twitter':
            shareUrl = `https://twitter.com/intent/tweet?text=${text}`;
            break;
        case 'messenger':
            // try deep link for mobile messenger; fallback to Facebook sharer
            shareUrl = `fb-messenger://share?link=${url}`;
            break;
        case 'email':
            shareUrl = `mailto:?subject=${encodeURIComponent('Stress Assessment Game')}&body=${text}`;
            break;
        case 'copy':
            // copy to clipboard
            copyToClipboard(decodeURIComponent(text));
            alert('Link copied to clipboard. You can paste it in Messenger, WhatsApp, or any app.');
            closeShareModal();
            return;
        case 'native':
            if (navigator.share) {
                navigator.share({
                    title: 'Stress Assessment Game',
                    text: 'Take the stress assessment test and get personalized advice.',
                    url: pageUrl
                }).catch(err => console.log('Native share failed:', err));
            } else {
                alert('Native sharing is not available in this browser. Use one of the app buttons instead.');
            }
            closeShareModal();
            return;
        default:
            return;
    }

    // Try to open the sharing URL.
    // For messenger deep link, opening may fail on desktop; fallback to facebook sharer.
    const win = window.open(shareUrl, '_blank');
    if (!win && platform === 'messenger') {
        // fallback
        window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank');
    }
    closeShareModal();
}

function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).catch(() => {
            // fallback
            const input = document.createElement('input');
            input.value = text;
            document.body.appendChild(input);
            input.select();
            document.execCommand('copy');
            document.body.removeChild(input);
        });
    } else {
        const input = document.createElement('input');
        input.value = text;
        document.body.appendChild(input);
        input.select();
        document.execCommand('copy');
        document.body.removeChild(input);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    switchScreen('mainMenu');
});
