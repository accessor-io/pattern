javascript:(function() {
    // Already injected check
    if (document.getElementById('eth-finder-ui')) {
        alert('ETH Finder is already running!');
        return;
    }

    // Store found ENS names
    const ensNames = new Set();

    // Create UI container with relative positioning
    const ui = document.createElement('div');
    ui.id = 'eth-finder-ui';
    ui.style.cssText = `
        position: fixed;
        top: 5px;
        right: 5px;
        background: rgba(29, 161, 242, 0.9);
        padding: 5px 8px;
        border-radius: 4px;
        z-index: 999999;
        color: white;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        min-width: 150px;
        font-size: 12px;
        backdrop-filter: blur(5px);
        display: flex;
        align-items: center;
        gap: 5px;
    `;

    // Create status indicator
    const statusIndicator = document.createElement('div');
    statusIndicator.style.cssText = `
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #ff4444;
        flex-shrink: 0;
    `;

    // Create notification light with improved visibility
    const notificationLight = document.createElement('div');
    notificationLight.style.cssText = `
        width: 100%;
        height: 2px;
        background: transparent;
        position: absolute;
        bottom: 0;
        left: 0;
        border-bottom-left-radius: 4px;
        border-bottom-right-radius: 4px;
        transition: all 0.2s ease;
    `;

    // Create controls container for better layout
    const controlsContainer = document.createElement('div');
    controlsContainer.style.cssText = `
        display: flex;
        align-items: center;
        gap: 5px;
    `;

    // Create controls
    const startBtn = document.createElement('button');
    startBtn.textContent = 'Start';
    startBtn.style.cssText = `
        background: #ffffff;
        color: #1da1f2;
        border: none;
        padding: 2px 6px;
        border-radius: 3px;
        cursor: pointer;
        font-size: 11px;
        font-weight: bold;
    `;

    const exportBtn = document.createElement('button');
    exportBtn.textContent = 'Export';
    exportBtn.style.cssText = startBtn.style.cssText;

    const counter = document.createElement('div');
    counter.textContent = '0';
    counter.style.cssText = `
        font-size: 11px;
        margin-left: 2px;
        white-space: nowrap;
    `;

    // Add elements to UI
    controlsContainer.appendChild(startBtn);
    controlsContainer.appendChild(exportBtn);
    controlsContainer.appendChild(counter);
    
    ui.appendChild(statusIndicator);
    ui.appendChild(controlsContainer);
    ui.appendChild(notificationLight);
    document.body.appendChild(ui);

    // Improved notification flash animation
    function flashNotification() {
        notificationLight.style.background = '#4CAF50';
        notificationLight.style.boxShadow = '0 0 5px #4CAF50';
        
        setTimeout(() => {
            notificationLight.style.background = 'transparent';
            notificationLight.style.boxShadow = 'none';
        }, 300);
    }

    // Scanning state
    let isScanning = false;
    let observer = null;
    let scanInterval = null;
    let heartbeatInterval = null;
    let lastScanTime = 0;
    let isProcessing = false;
    let restartAttempts = 0;
    const MAX_RESTART_ATTEMPTS = 3;

    // Function to find ENS names in text
    function findEnsNames(text) {
        if (!text || typeof text !== 'string') return;
        const matches = text.match(/\S+\.eth\b/g) || [];
        matches.forEach(name => {
            if (!ensNames.has(name)) {
                ensNames.add(name);
                counter.textContent = ensNames.size.toString();
                flashNotification();
                console.log('Found new ENS name:', name);
            }
        });
        lastScanTime = Date.now();
    }

    // Function to safely scan elements
    function scanElement(element) {
        try {
            if (element.nodeType === 3) { // Text node
                findEnsNames(element.textContent);
            } else if (element.nodeType === 1) { // Element node
                findEnsNames(element.textContent);
                // Scan attributes
                const attributes = ['title', 'alt', 'placeholder', 'value', 'href', 'data-screen-name'];
                attributes.forEach(attr => {
                    if (element.hasAttribute(attr)) {
                        findEnsNames(element.getAttribute(attr));
                    }
                });
            }
        } catch (error) {
            console.error('Element scan error:', error);
        }
    }

    // Function to scan current page content
    function scanPage() {
        if (!isScanning || isProcessing) return;
        isProcessing = true;

        try {
            // Process in chunks to avoid recursion
            const elements = Array.from(document.body.getElementsByTagName('*'));
            const chunkSize = 100;
            let currentIndex = 0;

            function processChunk() {
                if (!isScanning) {
                    isProcessing = false;
                    return;
                }

                const chunk = elements.slice(currentIndex, currentIndex + chunkSize);
                chunk.forEach(scanElement);

                currentIndex += chunkSize;
                if (currentIndex < elements.length) {
                    setTimeout(processChunk, 0);
                } else {
                    isProcessing = false;
                }
            }

            processChunk();
        } catch (error) {
            console.error('Scan error:', error);
            isProcessing = false;
            safeRestartScanning();
        }
    }

    // Function to safely restart scanning
    function safeRestartScanning() {
        if (!isScanning || restartAttempts >= MAX_RESTART_ATTEMPTS) return;
        
        restartAttempts++;
        console.log(`Attempting restart ${restartAttempts}/${MAX_RESTART_ATTEMPTS}`);

        try {
            observer?.disconnect();
            clearInterval(scanInterval);
            setupObserver();
        } catch (error) {
            console.error('Restart error:', error);
        }

        // Reset restart attempts after successful operation
        setTimeout(() => {
            restartAttempts = 0;
        }, 10000);
    }

    // Setup mutation observer with enhanced monitoring
    function setupObserver() {
        try {
            observer = new MutationObserver((mutations) => {
                if (!isScanning || isProcessing) return;
                
                mutations.forEach(mutation => {
                    try {
                        mutation.addedNodes.forEach(scanElement);

                        if (mutation.type === 'attributes') {
                            scanElement(mutation.target);
                        }

                        if (mutation.type === 'characterData') {
                            findEnsNames(mutation.target.textContent);
                        }
                    } catch (error) {
                        console.error('Mutation processing error:', error);
                    }
                });
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: true,
                characterData: true
            });

            // Set up periodic scanning for dynamic content
            scanInterval = setInterval(scanPage, 1000);

        } catch (error) {
            console.error('Observer setup error:', error);
            setTimeout(setupObserver, 1000);
        }
    }

    // Start/Stop scanning
    startBtn.addEventListener('click', () => {
        if (isScanning) {
            isScanning = false;
            isProcessing = false;
            observer?.disconnect();
            clearInterval(scanInterval);
            clearInterval(heartbeatInterval);
            startBtn.textContent = 'Start';
            startBtn.style.background = '#ffffff';
            startBtn.style.color = '#1da1f2';
            statusIndicator.style.background = '#ff4444';
        } else {
            isScanning = true;
            restartAttempts = 0;
            lastScanTime = Date.now();
            setupObserver();
            startBtn.textContent = 'Stop';
            startBtn.style.background = '#ff4444';
            startBtn.style.color = '#ffffff';
            statusIndicator.style.background = '#4CAF50';
        }
    });

    // Export functionality
    exportBtn.addEventListener('click', () => {
        const ensString = Array.from(ensNames).join(', ');
        const blob = new Blob([ensString], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'ens_names.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
})(); 