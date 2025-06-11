/**
 * Convivial Features Frontend Integration
 * Client-side JavaScript for real-time features
 */

// WebSocket connection
let socket = null;
let currentUser = null;
let currentMood = 'neutral';

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeConvivialFeatures();
});

/**
 * Initialize all convivial features
 */
function initializeConvivialFeatures() {
    // Get current user from page data
    currentUser = window.SEARXNG_USER || {
        id: 'guest',
        username: 'Guest',
        isAuthenticated: false
    };
    
    if (currentUser.isAuthenticated) {
        // Connect WebSocket
        connectWebSocket();
        
        // Initialize features
        initializePresenceBubbles();
        initializeDiscoveryFeed();
        initializeMoodSelector();
        initializeGiftWrapper();
        initializeMorningCoffee();
        
        // Set up event listeners
        setupSearchListeners();
        setupKeyboardShortcuts();
    }
}

/**
 * WebSocket Connection Management
 */
function connectWebSocket() {
    const wsUrl = window.location.protocol === 'https:' 
        ? `wss://${window.location.host}/socket.io/`
        : `ws://${window.location.host}/socket.io/`;
    
    socket = io(wsUrl, {
        auth: {
            token: currentUser.token || 'dev-token',
            userId: currentUser.id,
            username: currentUser.username
        },
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: 5
    });
    
    // Connection events
    socket.on('connect', () => {
        console.log('Connected to convivial server');
        updateConnectionStatus('connected');
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from convivial server');
        updateConnectionStatus('disconnected');
    });
    
    // Friend presence events
    socket.on('friend:online', (data) => {
        addPresenceBubble(data);
        showNotification(`${data.username} joined the salon`, 'presence');
    });
    
    socket.on('friend:offline', (data) => {
        removePresenceBubble(data.userId);
    });
    
    socket.on('friend:searching', (data) => {
        animatePresenceBubble(data.userId, 'searching');
        updateSearchingHint(data);
    });
    
    // Discovery events
    socket.on('discovery:new', (data) => {
        addToDiscoveryFeed(data);
    });
    
    socket.on('collision:detected', (data) => {
        celebrateCollision(data);
    });
    
    // Gift events
    socket.on('gift:received', (data) => {
        notifyNewGift(data.gift);
    });
    
    socket.on('gift:revealed', (data) => {
        revealGift(data);
    });
}

/**
 * Presence Bubbles
 */
function initializePresenceBubbles() {
    // Create presence container if not exists
    if (!document.querySelector('.presence-bubbles')) {
        const searchContainer = document.querySelector('.search-container') || 
                              document.querySelector('#search') ||
                              document.body;
        
        const presenceContainer = document.createElement('div');
        presenceContainer.className = 'presence-bubbles';
        searchContainer.insertBefore(presenceContainer, searchContainer.firstChild);
    }
}

function addPresenceBubble(userData) {
    const container = document.querySelector('.presence-bubbles');
    if (!container) return;
    
    // Check if bubble already exists
    let bubble = container.querySelector(`[data-user-id="${userData.userId}"]`);
    
    if (!bubble) {
        bubble = document.createElement('div');
        bubble.className = 'presence-bubble';
        bubble.dataset.userId = userData.userId;
        bubble.innerHTML = `
            <span class="avatar">${userData.avatar || userData.username[0].toUpperCase()}</span>
            <span class="tooltip">${userData.username}</span>
        `;
        container.appendChild(bubble);
        
        // Animate entrance
        bubble.style.animation = 'bubble-appear 0.3s ease-out';
    }
    
    // Update mood if provided
    if (userData.mood) {
        bubble.dataset.mood = userData.mood;
    }
}

function removePresenceBubble(userId) {
    const bubble = document.querySelector(`[data-user-id="${userId}"]`);
    if (bubble) {
        bubble.style.animation = 'bubble-disappear 0.3s ease-out';
        setTimeout(() => bubble.remove(), 300);
    }
}

function animatePresenceBubble(userId, animation) {
    const bubble = document.querySelector(`[data-user-id="${userId}"]`);
    if (bubble) {
        bubble.classList.add(animation);
        setTimeout(() => bubble.classList.remove(animation), 3000);
    }
}

/**
 * Discovery Feed
 */
function initializeDiscoveryFeed() {
    // Create feed container if not exists
    if (!document.querySelector('.discovery-feed')) {
        const feedHTML = `
            <div class="discovery-feed">
                <div class="feed-header">
                    <h3>Discovery Stream</h3>
                    <button class="feed-toggle" title="Toggle feed">📡</button>
                </div>
                <div class="feed-content">
                    <div class="feed-items"></div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', feedHTML);
        
        // Toggle functionality
        document.querySelector('.feed-toggle').addEventListener('click', () => {
            document.querySelector('.discovery-feed').classList.toggle('collapsed');
        });
    }
    
    // Load initial feed
    loadDiscoveryFeed();
}

function addToDiscoveryFeed(discovery) {
    const feedItems = document.querySelector('.feed-items');
    if (!feedItems) return;
    
    const item = document.createElement('div');
    item.className = 'discovery-item new';
    item.innerHTML = `
        <div class="discovery-header">
            <span class="user">${discovery.user}</span>
            <span class="time">just now</span>
        </div>
        <div class="discovery-content">
            <a href="${discovery.url}" target="_blank">${discovery.title}</a>
        </div>
        <div class="discovery-actions">
            <button class="action-btn" onclick="giftDiscovery('${discovery.id}')" title="Gift">🎁</button>
            <button class="action-btn" onclick="saveDiscovery('${discovery.id}')" title="Save">💾</button>
            <button class="action-btn" onclick="reactToDiscovery('${discovery.id}')" title="React">✨</button>
        </div>
    `;
    
    feedItems.insertBefore(item, feedItems.firstChild);
    
    // Remove 'new' class after animation
    setTimeout(() => item.classList.remove('new'), 1000);
    
    // Limit feed size
    while (feedItems.children.length > 20) {
        feedItems.removeChild(feedItems.lastChild);
    }
}

/**
 * Mood Selector
 */
function initializeMoodSelector() {
    const searchForm = document.querySelector('#search_form') || 
                      document.querySelector('form[role="search"]');
    
    if (!searchForm) return;
    
    // Create mood selector
    const moodSelector = document.createElement('div');
    moodSelector.className = 'mood-selector';
    moodSelector.innerHTML = `
        <div class="current-mood" data-mood="${currentMood}">
            <span class="mood-emoji">😊</span>
            <span class="mood-text">Choose vibe</span>
        </div>
        <div class="mood-dropdown" style="display: none;">
            <div class="mood-option" data-mood="late-night">
                <span>🌙</span> Late night rabbit hole
            </div>
            <div class="mood-option" data-mood="botanical">
                <span>🌺</span> Sunday morning botanical
            </div>
            <div class="mood-option" data-mood="vinyl-digging">
                <span>🎵</span> Vinyl digging simulation
            </div>
            <div class="mood-option" data-mood="serious-research">
                <span>📚</span> Serious research mode
            </div>
            <div class="mood-option" data-mood="weird-finds">
                <span>🍄</span> Weird finds only
            </div>
            <div class="mood-option" data-mood="historical">
                <span>🗺️</span> Historical adventures
            </div>
            <div class="mood-option" data-mood="deep-science">
                <span>🔬</span> Deep science dive
            </div>
            <div class="mood-option" data-mood="chaos">
                <span>🎪</span> Anything goes chaos
            </div>
        </div>
    `;
    
    searchForm.appendChild(moodSelector);
    
    // Toggle dropdown
    moodSelector.querySelector('.current-mood').addEventListener('click', (e) => {
        e.stopPropagation();
        const dropdown = moodSelector.querySelector('.mood-dropdown');
        dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
    });
    
    // Select mood
    moodSelector.querySelectorAll('.mood-option').forEach(option => {
        option.addEventListener('click', (e) => {
            e.stopPropagation();
            const mood = option.dataset.mood;
            setMood(mood);
            moodSelector.querySelector('.mood-dropdown').style.display = 'none';
        });
    });
    
    // Close on outside click
    document.addEventListener('click', () => {
        moodSelector.querySelector('.mood-dropdown').style.display = 'none';
    });
}

function setMood(mood) {
    currentMood = mood;
    
    // Update UI
    const moodOption = document.querySelector(`[data-mood="${mood}"]`);
    if (moodOption) {
        const emoji = moodOption.querySelector('span').textContent;
        const text = moodOption.textContent.trim().substring(2);
        
        document.querySelector('.current-mood').innerHTML = `
            <span class="mood-emoji">${emoji}</span>
            <span class="mood-text">${text}</span>
        `;
        
        // Apply mood theme
        document.body.dataset.mood = mood;
        
        // Notify server
        if (socket) {
            socket.emit('mood:set', { mood });
        }
    }
}

/**
 * Gift Wrapper
 */
function initializeGiftWrapper() {
    // Add gift buttons to search results
    observeSearchResults();
    
    // Initialize gift inbox
    createGiftInbox();
}

function observeSearchResults() {
    // Watch for new search results
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.classList && node.classList.contains('result')) {
                    addGiftButton(node);
                }
            });
        });
    });
    
    const resultsContainer = document.querySelector('#results') || 
                           document.querySelector('.results');
    
    if (resultsContainer) {
        observer.observe(resultsContainer, { childList: true, subtree: true });
    }
}

function addGiftButton(resultElement) {
    // Extract discovery data
    const url = resultElement.querySelector('a')?.href;
    const title = resultElement.querySelector('h3')?.textContent;
    
    if (!url || !title) return;
    
    const giftBtn = document.createElement('button');
    giftBtn.className = 'gift-result-btn';
    giftBtn.innerHTML = '🎁';
    giftBtn.title = 'Gift this discovery';
    giftBtn.onclick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        showGiftDialog({ url, title, element: resultElement });
    };
    
    // Add to result actions or title
    const actionsBar = resultElement.querySelector('.result-actions') || 
                      resultElement.querySelector('h3');
    if (actionsBar) {
        actionsBar.appendChild(giftBtn);
    }
}

function showGiftDialog(discovery) {
    const dialog = document.createElement('div');
    dialog.className = 'gift-dialog-overlay';
    dialog.innerHTML = `
        <div class="gift-dialog">
            <h3>🎁 Wrap this discovery</h3>
            <p class="discovery-preview">${discovery.title}</p>
            
            <div class="gift-recipients">
                <h4>Send to:</h4>
                <div class="friend-list">
                    <label><input type="radio" name="recipient" value="bob"> 🎵 Bob</label>
                    <label><input type="radio" name="recipient" value="carol"> 📚 Carol</label>
                </div>
            </div>
            
            <textarea class="gift-message" placeholder="Add a personal note..."></textarea>
            
            <div class="gift-options">
                <label>Reveal in:
                    <select class="reveal-time">
                        <option value="1">1 hour</option>
                        <option value="24" selected>24 hours</option>
                        <option value="72">3 days</option>
                    </select>
                </label>
                
                <label>Wrap style:
                    <select class="wrap-style">
                        <option value="classic">Classic 🎁</option>
                        <option value="birthday">Birthday 🎂</option>
                        <option value="mystery">Mystery 🎭</option>
                        <option value="seasonal">Seasonal ✨</option>
                    </select>
                </label>
            </div>
            
            <div class="dialog-actions">
                <button class="send-gift">Send Gift</button>
                <button class="cancel">Cancel</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(dialog);
    
    // Send gift
    dialog.querySelector('.send-gift').onclick = () => {
        const recipient = dialog.querySelector('input[name="recipient"]:checked')?.value;
        const message = dialog.querySelector('.gift-message').value;
        const revealHours = dialog.querySelector('.reveal-time').value;
        const wrapStyle = dialog.querySelector('.wrap-style').value;
        
        if (recipient) {
            sendGift({
                discovery,
                recipient,
                message,
                revealHours,
                wrapStyle
            });
            dialog.remove();
        }
    };
    
    // Cancel
    dialog.querySelector('.cancel').onclick = () => dialog.remove();
    dialog.onclick = (e) => {
        if (e.target === dialog) dialog.remove();
    };
}

function sendGift(giftData) {
    if (socket) {
        socket.emit('gift:send', giftData);
        showNotification('Gift sent! 🎁', 'success');
    }
}

/**
 * Morning Coffee
 */
function initializeMorningCoffee() {
    // Check if it's morning
    const hour = new Date().getHours();
    if (hour >= 6 && hour <= 10) {
        checkMorningCoffee();
    }
}

async function checkMorningCoffee() {
    try {
        const response = await fetch('/api/morning-coffee');
        const data = await response.json();
        
        if (data.available && !sessionStorage.getItem('coffee-viewed')) {
            showMorningCoffee(data);
        }
    } catch (error) {
        console.error('Failed to load morning coffee:', error);
    }
}

function showMorningCoffee(coffeeData) {
    const coffeeHTML = `
        <div class="morning-coffee-modal">
            <div class="coffee-content">
                <h2>☕ Morning Coffee</h2>
                <p class="coffee-date">${new Date().toLocaleDateString('en-US', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                })}</p>
                
                <div class="coffee-summary">
                    ${coffeeData.summary || 'Yesterday was full of discoveries!'}
                </div>
                
                <div class="coffee-stats">
                    <div class="stat">
                        <span class="number">${coffeeData.stats.total_discoveries}</span>
                        <span class="label">Discoveries</span>
                    </div>
                    <div class="stat">
                        <span class="number">${coffeeData.stats.collision_count}</span>
                        <span class="label">Collisions</span>
                    </div>
                    <div class="stat">
                        <span class="number">${coffeeData.stats.unique_engines}</span>
                        <span class="label">Sources</span>
                    </div>
                </div>
                
                <div class="coffee-highlights">
                    <h3>Top Discoveries</h3>
                    ${coffeeData.discoveries.slice(0, 5).map(d => `
                        <div class="coffee-discovery">
                            <a href="${d.url}" target="_blank">${d.title}</a>
                            <span class="discovered-by">by ${d.discovered_by}</span>
                        </div>
                    `).join('')}
                </div>
                
                <div class="coffee-reactions">
                    <p>How's your coffee?</p>
                    <div class="reaction-buttons">
                        <button onclick="reactToCoffee('☕')">☕</button>
                        <button onclick="reactToCoffee('☕☕')">☕☕</button>
                        <button onclick="reactToCoffee('☕☕☕')">☕☕☕</button>
                    </div>
                </div>
                
                <button class="close-coffee" onclick="closeMorningCoffee()">
                    Start Searching
                </button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', coffeeHTML);
    sessionStorage.setItem('coffee-viewed', 'true');
}

/**
 * Utility Functions
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function celebrateCollision(data) {
    // Create celebration overlay
    const celebration = document.createElement('div');
    celebration.className = 'collision-celebration';
    celebration.innerHTML = `
        <div class="collision-content">
            <h2>✨ Collision! ✨</h2>
            <p>${data.users.join(' & ')} searched for:</p>
            <p class="collision-query">"${data.query}"</p>
            <p>at the same time!</p>
        </div>
    `;
    
    document.body.appendChild(celebration);
    
    // Confetti animation
    createConfetti();
    
    // Remove after animation
    setTimeout(() => celebration.remove(), 5000);
}

function createConfetti() {
    const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b'];
    const confettiCount = 100;
    
    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.animationDelay = Math.random() * 3 + 's';
        confetti.style.animationDuration = (Math.random() * 3 + 2) + 's';
        
        document.body.appendChild(confetti);
        
        // Remove after animation
        setTimeout(() => confetti.remove(), 5000);
    }
}

// Export functions for external use
window.ConvivialFeatures = {
    setMood,
    showNotification,
    sendGift,
    reactToCoffee: function(reaction) {
        if (socket) {
            socket.emit('coffee:react', { reaction });
        }
        closeMorningCoffee();
    },
    closeMorningCoffee: function() {
        document.querySelector('.morning-coffee-modal')?.remove();
    }
};