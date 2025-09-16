async function loadData() {
    // Fetch sections first
    const sectionsResponse = await fetch('/get_sections');
    const sections = await sectionsResponse.json();
    
    const sectionSelect = document.getElementById('save_to_section');
    sectionSelect.innerHTML = '';
    sections.forEach(sec => {
        const option = document.createElement('option');
        option.value = sec.name;
        option.textContent = sec.name;
        sectionSelect.appendChild(option);
    });

    // Then fetch accounts
    const accountsResponse = await fetch('/get_accounts');
    const accountsBySection = await accountsResponse.json();
    
    const listContainer = document.getElementById('saved-accounts-list');
    listContainer.innerHTML = '';
    const credentialsDisplayContainer = document.getElementById('credentials-display-container');
    const usernameDisplay = document.getElementById('username-display');
    const passwordDisplay = document.getElementById('password-display');
    const resultContainer = document.getElementById('result-container');
    const playerName = document.getElementById('player-name');
    const playerRank = document.getElementById('player-rank');
    const playerRr = document.getElementById('player-rr');

    for (const sectionName in accountsBySection) {
        const sectionDiv = document.createElement('div');
        sectionDiv.className = 'section-container';
        
        const sectionHeader = document.createElement('div');
        sectionHeader.className = 'section-header';
        
        const sectionTitle = document.createElement('h3');
        sectionTitle.textContent = sectionName;
        sectionHeader.appendChild(sectionTitle);
        
        if (sectionName !== 'Default') {
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'section-delete-btn';
            deleteBtn.innerHTML = '&times;';
            deleteBtn.onclick = (e) => {
                e.stopPropagation();
                if (confirm(`Are you sure you want to delete the "${sectionName}" section? Accounts will be moved to Default.`)) {
                    deleteSection(sectionName);
                }
            };
            sectionHeader.appendChild(deleteBtn);
        }

        sectionDiv.appendChild(sectionHeader);

        const accountList = document.createElement('ul');
        accountList.className = 'accounts-list';
        accountsBySection[sectionName].forEach(acc => {
            const item = document.createElement('li');
            item.className = 'saved-account-item';
            let rankInfo = acc.rank ? `${acc.rank} - ${acc.rr || 0} RR` : 'No rank data';
            item.innerHTML = `
                <div class="account-info">
                    <span class="account-name">${acc.username}#${acc.hashtag} (${acc.region.toUpperCase()})</span>
                    <span class="rank-details">${rankInfo}</span>
                </div>
                <button class="delete-btn" data-username="${acc.username}" data-hashtag="${acc.hashtag}" data-region="${acc.region}">&times;</button>
            `;
            item.querySelector('.account-info').addEventListener('click', () => {
                document.getElementById('in_game_name').value = acc.username;
                document.getElementById('hashtag').value = acc.hashtag;
                document.getElementById('region').value = acc.region;
                document.getElementById('account_username').value = acc.account_username || '';
                document.getElementById('password').value = acc.password || '';
                
                const hasUsername = acc.account_username && acc.account_username.trim() !== '';
                const hasPassword = acc.password && acc.password.trim() !== '';

                if (hasUsername || hasPassword) {
                    usernameDisplay.textContent = hasUsername ? `Username: ${acc.account_username}` : 'Username: Not saved';
                    passwordDisplay.textContent = hasPassword ? `Password: ${acc.password}` : 'Password: Not saved';
                    credentialsDisplayContainer.style.display = 'block';
                } else {
                    credentialsDisplayContainer.style.display = 'none';
                }

                if (acc.rank) {
                    playerName.textContent = `${acc.username}#${acc.hashtag}`;
                    playerRank.textContent = `Rank: ${acc.rank}`;
                    playerRr.textContent = `Rank Rating (RR): ${acc.rr || 0}`;
                    document.getElementById('error-message').textContent = '';
                    resultContainer.style.display = 'block';
                } else {
                    resultContainer.style.display = 'none';
                }
            });
            item.querySelector('.delete-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                deleteAccount(e.target.dataset.username, e.target.dataset.hashtag, e.target.dataset.region);
            });
            accountList.appendChild(item);
        });
        sectionDiv.appendChild(accountList);
        listContainer.appendChild(sectionDiv);

        // Add click listener to header for collapsing
        sectionHeader.addEventListener('click', () => {
            sectionDiv.classList.toggle('expanded');
        });

        // Expand by default
        sectionDiv.classList.add('expanded');
    }
}

function deleteAccount(username, hashtag, region) {
    fetch('/', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `action=delete&username=${encodeURIComponent(username)}&hashtag=${encodeURIComponent(hashtag)}&region=${encodeURIComponent(region)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadData();
            document.getElementById('credentials-display-container').style.display = 'none';
            document.getElementById('result-container').style.display = 'none';
        } else {
            alert('Failed to delete account.');
        }
    });
}

function deleteSection(sectionName) {
    fetch('/', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `action=delete_section&section_name=${encodeURIComponent(sectionName)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadData();
        } else {
            alert('Failed to delete section: ' + data.error);
        }
    });
}

document.getElementById('rank-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const username = document.getElementById('in_game_name').value;
    const hashtag = document.getElementById('hashtag').value;
    const region = document.getElementById('region').value;

    const resultContainer = document.getElementById('result-container');
    const playerName = document.getElementById('player-name');
    const playerRank = document.getElementById('player-rank');
    const playerRr = document.getElementById('player-rr');
    const errorMessage = document.getElementById('error-message');

    resultContainer.style.display = 'block';
    playerName.textContent = `Fetching data for ${username}#${hashtag}...`;
    playerRank.textContent = '';
    playerRr.textContent = '';
    errorMessage.textContent = '';

    fetch('/', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `action=check&username=${encodeURIComponent(username)}&hashtag=${encodeURIComponent(hashtag)}&region=${encodeURIComponent(region)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            playerName.textContent = '';
            playerRank.textContent = '';
            playerRr.textContent = '';
            errorMessage.textContent = `Error: ${data.error}`;
        } else {
            playerName.textContent = data.playerName;
            playerRank.textContent = data.rank ? `Rank: ${data.rank}` : 'Rank: N/A';
            playerRr.textContent = `Rank Rating (RR): ${data.rr}`;
            errorMessage.textContent = '';
        }
    })
    .catch(error => {
        playerName.textContent = '';
        errorMessage.textContent = 'An unexpected error occurred.';
        console.error('Fetch Error:', error);
    });
});

document.getElementById('save-button').addEventListener('click', function() {
    const username = document.getElementById('in_game_name').value;
    const hashtag = document.getElementById('hashtag').value;
    const region = document.getElementById('region').value;
    const account_username = document.getElementById('account_username').value;
    const password = document.getElementById('password').value;
    const section = document.getElementById('save_to_section').value;

    if (!username || !hashtag) {
        alert('Please enter an In-game Name and Hashtag before saving.');
        return;
    }

    fetch('/', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `action=save&username=${encodeURIComponent(username)}&hashtag=${encodeURIComponent(hashtag)}&region=${encodeURIComponent(region)}&account_username=${encodeURIComponent(account_username)}&password=${encodeURIComponent(password)}&section=${encodeURIComponent(section)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadData();
        } else {
            alert('Failed to save account: ' + data.error);
        }
    });
});

document.getElementById('section-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const newSectionName = document.getElementById('new_section_name').value;
    if (!newSectionName) return;

    fetch('/', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `action=create_section&section_name=${encodeURIComponent(newSectionName)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('new_section_name').value = '';
            loadData();
        } else {
            alert('Failed to create section: ' + data.error);
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    loadData();
    // Use a long-polling or WebSocket approach for real-time updates if needed,
    // but for this app, periodic refresh from the client is simple and effective.
    setInterval(loadData, 60000); 
});